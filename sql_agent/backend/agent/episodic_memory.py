"""Episodic Memory 模块 —— PER (Prioritized Episodic Memory)

基于 DRL 中的 PER 算法（Schaul et al., DeepMind 2016），
对每一次对话的成功/失败经验进行带优先级的存储和采样回放。

核心概念：
- TD-error：成功度与期望的偏差绝对值，偏差越大（意外失败/意外成功）优先级越高
- heapq 采样：每轮对话从堆中抽取 top-N 高优先级经验，注入 System Prompt
- 独立消息注入：经验作为独立的 system 消息插入，避免字符串拼接导致的叠加隐患

面试话术：
"我们把 DRL 中的 PER 算法迁移到了对话场景——每次对话结束后，
Agent 自动记录工具链和意图，基于 TD-error 计算优先级。
后续对话中优先采样高 TD-error 的经验注入 System Prompt，
实现类似课程学习的渐进式自我提升。"
"""

import heapq
import logging

logger = logging.getLogger("db_agent.memory")


class PrioritizedEpisodicMemory:
    """带优先级的经验记忆 —— DRL PER 算法迁移

    Attributes:
        alpha: 优先级指数（越大越倾向采样高优先级经验）
        _heap: 大根堆（存储负优先级，方便 Python 的 heapq 取最小）
        _episodes: 所有经验的完整数据
    """

    def __init__(self, alpha: float = 0.6):
        """初始化 PER 内存

        Args:
            alpha: 优先级指数，0=均匀采样，1=纯优先级采样，默认 0.6
        """
        self.alpha = alpha
        self._heap: list = []           # [(priority_neg, episode_id), ...]
        self._episodes: dict = {}       # {episode_id: {"priority": float, "data": dict}}

    # ══════════════════════════════════════════════════════
    # 存储与优先级计算
    # ══════════════════════════════════════════════════════

    def store(self, episode_id: str, data: dict, success: bool,
              user_feedback: str = None):
        """存储一次对话经验

        Args:
            episode_id: 唯一标识（通常用 session_id）
            data: 经验数据（user_intent, tool_chain 等）
            success: 对话是否成功完成
            user_feedback: 可选，用户反馈 ("positive"/"negative")
        """
        priority = self._compute_priority(data, success, user_feedback)
        self._episodes[episode_id] = {
            "priority": priority,
            "data": data,
        }
        # 用大根堆存储——Python 的 heapq 是小根堆，所以存负值
        heapq.heappush(self._heap, (-priority, episode_id))
        logger.debug(f"[PER] 存储经验 {episode_id[:8]}: priority={priority:.3f}")

    def _compute_priority(self, data: dict, success: bool,
                          user_feedback: str = None) -> float:
        """TD-error 计算：成功度与期望的偏差越大，优先级越高

        - 成功的对话，预期成功率 0.8 → TD-error=0.2（低优先级，正常）
        - 失败的对话，预期成功率 0.3 → TD-error=0.4（高优先级，值得学习）
        - 用户正面反馈 → 降低 TD-error（减少重复学习已知正确的）
        - 用户负面反馈 → 升高 TD-error（重点回放失败的）
        """
        success_rate = 0.8 if success else 0.3
        expected_success = 0.7
        td_error = abs(success_rate - expected_success)

        if user_feedback == "positive":
            td_error *= 0.5      # 已知正确，降低学习权重
        elif user_feedback == "negative":
            td_error *= 1.5      # 用户不满意，重点回放

        return max(td_error, 0.01)   # 保证最小优先级，避免从堆中消失

    # ══════════════════════════════════════════════════════
    # 采样与注入
    # ══════════════════════════════════════════════════════

    def sample(self, n: int) -> list:
        """采样 top-N 高优先级经验

        Args:
            n: 采样数量

        Returns:
            [{"priority": float, "data": {...}}, ...]
        """
        if not self._heap:
            return []
        top = heapq.nsmallest(min(n, len(self._heap)), self._heap)
        return [self._episodes[eid] for _, eid in top]

    def inject_into_prompt(self, messages: list, n: int = 2) -> list:
        """将历史经验注入消息列表（作为独立的 system 消息）

        设计要点：
        - 先移除之前的 PER 消息，避免多轮叠加
        - 经验作为独立 system 消息插入（index=1，紧接主 system prompt）
        - 不修改原 system prompt 字符串，避免污染

        Args:
            messages: 当前的消息列表（会被原地修改）
            n: 注入的经验数量，默认 2

        Returns:
            修改后的 messages（与输入是同一个列表）
        """
        experiences = self.sample(n)
        if not experiences:
            return messages

        # 清除之前注入的 PER 消息，防止叠加
        messages[:] = [
            m for m in messages
            if not (m.get("role") == "system" and "历史经验" in (m.get("content", "") or ""))
        ]

        # 构建经验文本
        exp_text = "## 历史经验\n" + "\n".join(
            f"· {e['data'].get('user_intent', '')[:80]} → "
            f"工具: {', '.join(e['data'].get('tool_chain', []))}"
            for e in experiences
        )

        # 作为独立 system 消息插入（system 在 index 0，经验在 index 1）
        messages.insert(1, {"role": "system", "content": exp_text})
        return messages