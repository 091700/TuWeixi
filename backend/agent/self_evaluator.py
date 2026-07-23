"""LLM Self-Evaluator —— Epistemic Uncertainty 自主终止判断模块 (P0)

参考论文：Self-Refine (Madaan et al., Meta 2023)

核心设计：
- 双层判断：规则兜底（硬安全） + LLM 语义判断（智能决策）
- 规则检查覆盖 Token 耗尽、最大轮次、重复错误三种强制终止场景
- LLM 判断让模型自主评估信息充分性，输出 JSON 格式的终止决策
- JSON 解析容错 + 关键词回退，保证即使 LLM 输出格式不规范也能正常工作

面试话术：
"我的终止策略是混合式的——规则做硬上限保护（防死循环），
LLM 做语义级充分性判断。规则负责 saying 'stop because you must'，
LLM 负责 saying 'stop because you're done'。
这在 Agent 领域叫做 Epistemic Uncertainty Estimation。"
"""

import json
import re
import logging

logger = logging.getLogger("db_agent.evaluator")


class LLMSelfEvaluator:
    """LLM 自评终止判断器 —— 让 LLM 自主评估信息充分性

    混合式终止策略：
    ┌─────────────────────────────────────┐
    │  Step 1: 规则安全兜底              │
    │  - Token 预算耗尽 → 强制终止       │
    │  - 轮次达到上限 → 强制终止         │
    │  - 连续工具错误 → 强制终止         │
    │  ↓                                  │
    │  Step 2: LLM 语义判断              │
    │  - 调用 LLM 评估信息充分性         │
    │  - 输出 JSON: {can_answer, confidence, missing} │
    │  - 解析容错 + 关键词回退           │
    └─────────────────────────────────────┘
    """

    # 评估 Prompt —— 要求 LLM 判断信息是否足够
    EVAL_PROMPT = """你是一个评估器。根据以下信息判断是否能完整回答用户问题。

用户问题: {user_question}
已探索表: {explored_tables}
关键发现: {findings}
工具调用次数: {tool_count}

请严格输出 JSON（不要出现其他文字）:
{{"can_answer": true/false, "confidence": 0.0-1.0, "missing": "还需要什么信息", "next_action": "建议下一步"}}"""

    def __init__(self, get_client_func):
        """初始化 Self Evaluator

        Args:
            get_client_func: 无参数函数，返回 OpenAI 兼容客户端实例。
                             延迟调用避免循环导入。
                             如果返回 None 则回退到规则判断。
        """
        self._get_client = get_client_func

    def evaluate(self, question: str, working_state, budget,
                 adapter: dict = None) -> dict:
        """LLM 自主判断 + 规则兜底 —— 主入口

        Args:
            question: 用户原始问题
            working_state: AgentWorkingState 实例（含 explored_tables, findings, tool_call_count）
            budget: TokenBudget 实例
            adapter: 可选，{"model": "deepseek-chat"} 用于指定评估模型

        Returns:
            {
                "can_answer": bool,       # 是否可以基于当前信息回答
                "confidence": float,      # 置信度 0-1
                "reason": str,            # 终止原因
                "next_action": str        # 建议的下一步
            }
        """
        # ════════════════════════════════════════
        # 规则安全兜底 —— 无脑硬判断
        # ════════════════════════════════════════

        if budget and budget.get_status()["status"] in ("exceeded", "critical"):
            return {"can_answer": True, "confidence": 0.9,
                    "reason": "token_exhausted", "next_action": "基于当前信息回答"}
        if working_state.tool_call_count >= 8:
            return {"can_answer": True, "confidence": 0.8,
                    "reason": "max_rounds", "next_action": "基于当前信息回答"}
        if len(working_state.last_tool_errors) >= 2:
            return {"can_answer": True, "confidence": 0.7,
                    "reason": "repeated_errors", "next_action": "向用户说明遇到的错误"}

        # ════════════════════════════════════════
        # LLM 语义判断 —— 让 AI 决定是否充分
        # ════════════════════════════════════════

        try:
            client = self._get_client()
            if client is None:
                return {"can_answer": False, "confidence": 0.5,
                        "reason": "client_unavailable", "next_action": "继续探索"}

            # 构建评估消息 —— 告诉 LLM 当前已知什么
            messages = [
                {"role": "system", "content": "你是评估器。只输出 JSON，不要输出其他文字。"},
                {"role": "user", "content": self.EVAL_PROMPT.format(
                    user_question=question,
                    explored_tables=", ".join(working_state.explored_tables[-10:] or ["无"]),
                    findings="; ".join(working_state.findings[-5:] or ["无"]),
                    tool_count=working_state.tool_call_count,
                )}
            ]

            # 调用 LLM 做评估（temperature=0 确保可重复性）
            model_name = adapter.get("model", "deepseek-chat") if adapter else "deepseek-chat"
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0,
                max_tokens=200,
            )

            raw = response.choices[0].message.content.strip()

            # 提取 JSON —— LLM 可能输出多余的前导/尾随文本
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result["reason"] = "llm_self_evaluation"
                return result

            # JSON 解析失败，根据关键词回退判断
            if any(kw in raw.lower() for kw in ("can answer", "可以回答", "完整", "充分")):
                return {"can_answer": True, "confidence": 0.6,
                        "reason": "llm_keyword_fallback", "next_action": "基于当前信息回答"}

        except Exception as e:
            logger.warning(f"[SelfEval] LLM自评失败: {e}，回退到规则判断")

        # 最终回退 —— 保守策略：信息不足，继续探索
        return {"can_answer": False, "confidence": 0.5,
                "reason": "eval_fallback", "next_action": "继续探索"}