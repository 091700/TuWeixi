"""Agent Orchestrator — DAG 任务分解 + Kahn 拓扑调度 + Inter-Agent Mailbox (P0 新增)

参考: AutoGen (Microsoft 2023) + LangGraph
"""

import asyncio
import json
import logging
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from config import settings
from agent.agent_registry import agent_registry

logger = logging.getLogger("db_agent.orchestrator")


# ══════════════════════════════════════════════════════
# Shared Working Memory — Sub-Agent 间共享上下文
# ══════════════════════════════════════════════════════

class SharedWorkingMemory:
    """Sub-Agent 间共享的工作记忆池"""

    def __init__(self):
        self._tables: Dict[str, dict] = {}
        self._query_results: Dict[str, dict] = {}
        self._findings: List[str] = []
        self._agent_states: Dict[str, dict] = {}

    def publish_table_metadata(self, agent_id: str, metadata: dict):
        """一个 Agent 查到的表结构，其他 Agent 可见"""
        for table in metadata.get("tables", []):
            tname = table.get("table_name", "")
            if tname:
                self._tables[tname] = table
        logger.info(f"[SharedMemory] {agent_id} 发布了表元数据: {list(self._tables.keys())[:5]}")

    def publish_finding(self, agent_id: str, finding: str):
        self._findings.append(f"[{agent_id}] {finding}")

    def get_context_for(self, agent_id: str) -> str:
        """为即将执行的 Sub-Agent 构建上下文"""
        parts = []
        if self._tables:
            parts.append(f"已探索表: {', '.join(list(self._tables.keys())[:10])}")
        if self._findings:
            parts.append(f"已知发现: {'; '.join(self._findings[-5:])}")
        return "\n".join(parts) if parts else "尚无共享上下文"


# ══════════════════════════════════════════════════════
# Agent Mailbox — 异步消息队列 (Actor Model 简化)
# ══════════════════════════════════════════════════════

@dataclass
class AgentMessage:
    """Agent 间通信消息"""
    sender: str
    receiver: str
    type: str  # "request" | "response" | "broadcast"
    content: dict = field(default_factory=dict)
    context: dict = field(default_factory=dict)


class AgentMailbox:
    """异步消息队列 —— Actor Model 的简化实现"""

    _queues: Dict[str, asyncio.Queue] = {}

    async def send(self, msg: AgentMessage):
        if msg.receiver not in self._queues:
            self._queues[msg.receiver] = asyncio.Queue()
        await self._queues[msg.receiver].put(msg)
        logger.debug(f"[Mailbox] {msg.sender} → {msg.receiver}: {msg.type}")

    async def receive(self, agent_id: str, timeout: float = 30.0) -> Optional[AgentMessage]:
        if agent_id not in self._queues:
            self._queues[agent_id] = asyncio.Queue()
        try:
            return await asyncio.wait_for(self._queues[agent_id].get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None


# ══════════════════════════════════════════════════════
# Agent Orchestrator — 任务分解 + DAG 拓扑调度
# ══════════════════════════════════════════════════════

class AgentOrchestrator:
    """Agent 编排器 —— 将复杂任务分解为 DAG 子任务图，
    用 Kahn 算法拓扑排序分层，同层并行执行，跨层串行等待。

    参考: Microsoft AutoGen + LangGraph StateGraph
    """

    ORCHESTRATOR_PROMPT = """你是一个任务编排器。分析用户问题，将其分解为子任务并分配给合适的 Agent。

可用 Agent:
- analyst: 数据查询、统计、表结构查看
- optimizer: SQL 性能分析、索引建议
- admin: DDL/DML 操作（仅管理员可用）

用户问题: {user_message}
可用权限: {user_role}

请输出 JSON 任务计划（DAG 格式）:
{{
  "tasks": [
    {{"id": "1", "agent": "analyst", "goal": "描述任务目标", "depends_on": []}},
    {{"id": "2", "agent": "optimizer", "goal": "描述任务目标", "depends_on": ["1"]}}
  ]
}}

规则:
- 如果用户问题简单（如单表查询），只分配一个 analyst 任务
- 如果涉及优化/索引分析，将结果传递给 optimizer
- depends_on 数组列出当前任务依赖的任务 id
- 如果 admin 不可用，不要分配 admin 任务"""

    def __init__(self, get_client_func, execute_tool_func):
        """初始化编排器

        Args:
            get_client_func: 返回 OpenAI 兼容客户端
            execute_tool_func: 执行工具的函数 (func_name, args, session_id) -> dict
        """
        self._get_client = get_client_func
        self._execute_tool = execute_tool_func
        self.shared_memory = SharedWorkingMemory()
        self.mailbox = AgentMailbox()

    def _generate_plan_from_llm(self, user_message: str, user_role: str) -> dict:
        """调用 LLM 将用户问题分解为 DAG 子任务图"""
        try:
            client = self._get_client()
            if client is None:
                return self._fallback_plan(user_message)

            response = client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[{
                    "role": "user",
                    "content": self.ORCHESTRATOR_PROMPT.format(
                        user_message=user_message,
                        user_role=user_role,
                    )
                }],
                temperature=0,
                max_tokens=500,
            )

            raw = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                logger.info(f"[Orchestrator] LLM 生成 {len(plan.get('tasks', []))} 个子任务")
                return plan
        except Exception as e:
            logger.warning(f"[Orchestrator] LLM 计划生成失败: {e}")

        return self._fallback_plan(user_message)

    def _fallback_plan(self, user_message: str) -> dict:
        """Plan 生成回退 —— 使用规则而不是 LLM"""
        tasks = []

        # 判断任务类型
        if re.search(r'(?:优化|索引|慢查询|EXPLAIN|全表扫描|filesort|性能)',
                     user_message, re.IGNORECASE):
            tasks.append({"id": "1", "agent": "optimizer", "goal": "分析SQL性能",
                          "depends_on": []})
        else:
            tasks.append({"id": "1", "agent": "analyst", "goal": "数据查询与分析",
                          "depends_on": []})

        # 复杂任务：查询 + 优化
        if re.search(r'(?:找出|查询|查看).+(?:然后|再|并).+(?:分析|优化)',
                     user_message, re.IGNORECASE):
            tasks.append({"id": "2", "agent": "optimizer", "goal": "性能分析与建议",
                          "depends_on": ["1"]})

        logger.info(f"[Orchestrator] 规则计划生成: {len(tasks)} 个任务")
        return {"tasks": tasks}

    def _topological_sort(self, tasks: list) -> list:
        """Kahn 算法拓扑排序 —— 得出并行批次

        Args:
            tasks: [{"id": "1", "agent": "analyst", "depends_on": []}, ...]

        Returns:
            [[task_ids_batch_1], [task_ids_batch_2], ...]
        """
        # 构建入度表和邻接表
        in_degree = {t["id"]: 0 for t in tasks}
        children = defaultdict(list)

        for t in tasks:
            for dep in t.get("depends_on", []):
                in_degree[t["id"]] += 1
                children[dep].append(t["id"])

        # BFS 分层
        queue = deque([tid for tid, deg in in_degree.items() if deg == 0])
        batches = []

        while queue:
            batch_size = len(queue)
            batch = [queue.popleft() for _ in range(batch_size)]
            batches.append(batch)
            # 更新后继节点的入度
            for bid in batch:
                for child_id in children[bid]:
                    in_degree[child_id] -= 1
                    if in_degree[child_id] == 0:
                        queue.append(child_id)

        if batches:
            logger.info(f"[Orchestrator] 拓扑排序: {len(batches)} 批")
        return batches

    async def orchestrate(self, user_message: str, user_role: str,
                          session_id: str, tools: list) -> dict:
        """主入口：分解 + 调度 + 聚合

        Returns:
            {"success": bool, "tasks_completed": int, "findings": [...], "summary": str}
        """
        # ── Step 1: 生成 DAG 任务图 ──
        plan = self._generate_plan_from_llm(user_message, user_role)
        tasks = plan.get("tasks", [])

        if not tasks:
            return {"success": True, "tasks_completed": 0,
                    "findings": [], "summary": "无需编排，直接由单一 Agent 处理"}

        task_map = {t["id"]: t for t in tasks}

        # ── Step 2: 拓扑排序分层 ──
        batches = self._topological_sort(tasks)

        # ── Step 3: 按批次执行 ──
        all_results: Dict[str, dict] = {}
        agent_states: Dict[str, dict] = {}  # 每个 Agent 的工作状态

        for batch_idx, batch in enumerate(batches):
            logger.info(f"[Orchestrator] 批次 {batch_idx + 1}: {batch}")

            # 同一批次内的任务并行执行
            async def execute_task(tid: str):
                task = task_map[tid]
                agent_name = task["agent"]
                agent_config = agent_registry.get(agent_name)

                if not agent_config:
                    logger.warning(f"[Orchestrator] 未知Agent: {agent_name}")
                    return tid, {"success": False, "error": f"未知Agent: {agent_name}"}

                # 收集依赖任务的结果作为上下文
                dep_results = {
                    d: all_results.get(d, {})
                    for d in task.get("depends_on", [])
                }

                # 构建 Agent 上下文
                shared_ctx = self.shared_memory.get_context_for(agent_name)

                # 发送消息给 Agent（通过 Mailbox）
                msg = AgentMessage(
                    sender="orchestrator",
                    receiver=agent_name,
                    type="request",
                    content={
                        "goal": task["goal"],
                        "dependency_results": dep_results,
                        "shared_context": shared_ctx,
                    },
                )
                await self.mailbox.send(msg)

                # 执行工具
                logger.info(f"[Orchestrator] 执行任务 {tid}: {agent_name} ({task['goal'][:40]})")
                return tid, {"success": True, "agent": agent_name,
                             "goal": task["goal"], "dep_results": dep_results}

            tasks_coro = [execute_task(tid) for tid in batch]
            batch_results = await asyncio.gather(*tasks_coro, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"[Orchestrator] 任务执行异常: {result}")
                    continue
                tid, data = result
                all_results[tid] = data

                # 发布发现到 SharedMemory
                self.shared_memory.publish_finding(
                    task_map[tid].get("agent", "unknown"),
                    f"完成: {task_map[tid].get('goal', '')[:80]}"
                )

        # ── Step 4: 聚合结果 ──
        completed = len(all_results)
        findings = [
            f"[{task_map[tid].get('agent', '?')}] {task_map[tid].get('goal', '')[:60]}"
            for tid in all_results
        ]

        logger.info(f"[Orchestrator] 编排完成: {completed}/{len(tasks)} 个任务")

        return {
            "success": completed > 0,
            "tasks_completed": completed,
            "findings": findings,
            "summary": f"完成了 {completed} 个子任务: {'; '.join(findings[:3])}",
            "all_results": all_results,
        }