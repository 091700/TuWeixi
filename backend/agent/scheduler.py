"""Agent 调度层 v3.0 — 集成 Token Budget + 自适应终止 + 自愈 + 缓存 + 反思 + 工作记忆

本模块是 Agent 的主控中心，负责：
1. 管理 SSE 流式对话的主循环（chat_stream_generator）
2. 协调所有子模块：Token预算、Loop控制、工具调用、评估、摘要
3. 集成 P0-P2 所有功能：Orchestrator、SelfEvaluator、PER、Guardrails

依赖关系：
    loop_engine.py     → TokenBudget, AdaptiveLoopController, SelfHealingToolExecutor, etc.
    session_manager.py → SessionManager
    episodical_memory.py  → PrioritizedEpisodicMemory
    self_evaluator.py  → LLMSelfEvaluator
    tool_dependency.py → ToolDependencyAnalyzer
"""

import json
import time
import uuid
import re
import asyncio
import logging
from typing import AsyncGenerator, List, Dict, Optional, Any

from openai import OpenAI

from config import settings
from rag.knowledge_base import retrieve_knowledge, add_knowledge
from agent.agent_registry import router as agent_router, agent_registry
logger = logging.getLogger("db_agent.scheduler")

from tools.metadata_tool import get_table_metadata, TOOL_METADATA_DEFINITION
from tools.execute_sql_tool import execute_readonly_sql, TOOL_EXECUTE_SQL_DEFINITION
from tools.explain_tool import explain_sql, TOOL_EXPLAIN_DEFINITION
from tools.schema_inspector import inspect_table_schema, TOOL_INSPECT_DEFINITION
from tools.test_data_generator import generate_test_data, TOOL_GENERATE_DATA_DEFINITION
from tools.sql_formatter_tool import format_sql, TOOL_FORMAT_SQL_DEFINITION
from tools.admin_execute_tool import execute_admin_sql, TOOL_ADMIN_SQL_DEFINITION

# ── Loop Engine 导入 ─────────────────────────────────
from agent.loop_engine import (
    TokenBudget,
    AdaptiveLoopController,
    SelfHealingToolExecutor,
    ToolResultCache,
    ResultCompletenessChecker,
    AgentWorkingState,
    OptimizationTrigger,
)

READONLY_TOOLS = [
    TOOL_METADATA_DEFINITION, TOOL_EXECUTE_SQL_DEFINITION, TOOL_EXPLAIN_DEFINITION,
    TOOL_INSPECT_DEFINITION, TOOL_GENERATE_DATA_DEFINITION, TOOL_FORMAT_SQL_DEFINITION,
]
ADMIN_TOOLS = READONLY_TOOLS + [TOOL_ADMIN_SQL_DEFINITION]

TOOL_DISPATCH = {
    "get_table_metadata": get_table_metadata,
    "execute_readonly_sql": execute_readonly_sql,
    "explain_sql": explain_sql,
    "inspect_table_schema": inspect_table_schema,
    "generate_test_data": generate_test_data,
    "format_sql": format_sql,
    "execute_admin_sql": execute_admin_sql,
}

# ── System Prompt 模板 ─────────────────────────────
SYSTEM_PROMPT_TEMPLATE = """你是一个数据库查询助手，帮助用户查询和分析 MySQL 数据库。

## 对话风格（极其重要）
- 用自然的口语回复，像同事聊天一样，**不要用任何 Markdown 格式**（不用表格、不用加粗、不用标题、不用列表符号）
- 回复简洁直接，用户问什么答什么
- 用中文回复

## 当前工作数据库
{current_database}

{history_summary}

{working_memory}

## 核心铁律（违反将给出错误答案）
1. 严禁猜测！任何关于表结构、数据量的结论，必须先调用工具查询再回答
2. 工具返回"查询失败"时直接告诉用户实际错误，不要编造结果
3. ⚠️ 每次都必须重新调用工具查询最新数据，绝对不能复用对话历史

## 工作规则（每次提问都必须遵守）
1. 查询前先通过 get_table_metadata 确认表结构
2. 只用 SELECT 语句，自动加 LIMIT 100
3. 字段名必须来自元数据查询结果
4. 如果当前用户是管理员(admin)且要求写入/插入/删除数据，使用 execute_admin_sql 工具完成操作
5. 如果表名不确定，查看当前库下所有表来推断

## 任务规划指令（极其重要 —— 按此顺序执行）
你必须按以下顺序逐步执行，**每轮只调用完成当前步骤所需的工具**，
完成后再开始下一步。不要试图一次性调用所有工具。

对于任何数据查询（如"查看哪些表""查询数据""分析性能"），必须遵守：
1. 第一步：调用 get_table_metadata 获取表结构（不带 table 参数查看全部表）
2. 第二步：基于元数据结果，调用 execute_readonly_sql 执行查询
3. 第三步：如果涉及性能问题或用户要求分析，调用 explain_sql 分析执行计划
4. 第四步：汇总结果，用自然语言向用户解释
5. 如果有巡检类需求，额外调用 inspect_table_schema

对于复杂分析（如"找出最大的表并分析索引"），必须分步执行：
- 先查出数据量最大的表 → 再分析该表的索引
- 先查询数据 → 再 EXPLAIN 分析性能
- 每步的结果直接影响下一步的决策

记住：你是一个多步推理 Agent。不要一步到位。每一步只完成一件事。

## 参考知识
{retrieved_knowledge}
"""

DEGRADED_PROMPT = """你是一个数据库查询助手，帮助用户查询 MySQL 数据库。
请用最简短的文字回答问题，不要用 Markdown。

## 当前工作数据库
{current_database}

{working_memory}

核心规则：必须调用工具查询后再回答，不能猜测。

## 参考知识
{retrieved_knowledge}
"""

_deepseek_client: Optional[OpenAI] = None

def _get_client() -> OpenAI:
    global _deepseek_client
    if _deepseek_client is None:
        _deepseek_client = OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
    return _deepseek_client


# ══════════════════════════════════════════════════════
# 全局引擎实例
# ══════════════════════════════════════════════════════
from agent.session_manager import SessionManager
session_manager = SessionManager()

_tool_cache = ToolResultCache(ttl_seconds=30)
_healing_executor = SelfHealingToolExecutor(TOOL_DISPATCH, get_table_metadata)
_optimization_trigger = OptimizationTrigger()
_self_evaluator = None  # 延迟初始化，避免循环导入

from agent.self_evaluator import LLMSelfEvaluator
from agent.episodic_memory import PrioritizedEpisodicMemory
from agent.tool_dependency import ToolDependencyAnalyzer

def _get_self_evaluator() -> LLMSelfEvaluator:
    global _self_evaluator
    if _self_evaluator is None:
        _self_evaluator = LLMSelfEvaluator(_get_client)
    return _self_evaluator


# ══════════════════════════════════════════════════════
# Summary Generator — 自动对话摘要 (P0 新增)
# ══════════════════════════════════════════════════════

class SummaryGenerator:
    """当对话历史超过阈值时，自动用 LLM 生成摘要"""

    SUMMARY_PROMPT = """请用 200 字以内总结以下对话的关键信息：

{conversation}

摘要应包含: 用户意图、查询了哪些表、主要发现、未解决的问题"""

    def maybe_summarize(self, session_id: str):
        """在对话结束后检查是否需要生成摘要"""
        session = session_manager.get_session(session_id)
        if not session:
            return
        msgs = session["messages"]
        if len(msgs) < 6:
            return

        # 取最近 20 条用户和助手消息
        recent = [m["content"] for m in msgs[-20:]
                  if m.get("role") in ("user", "assistant")]
        if len(recent) < 4:
            return

        combined = "\n".join(recent[-8:])
        try:
            client = _get_client()
            response = client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[
                    {"role": "system", "content": "你是对话摘要器。只输出一段简洁的摘要。"},
                    {"role": "user", "content": self.SUMMARY_PROMPT.format(conversation=combined)},
                ],
                temperature=0,
                max_tokens=200,
            )
            summary = response.choices[0].message.content.strip()
            session_manager.set_summary(session_id, summary)

            # 裁剪旧消息，保留最近 5 条 + 摘要
            if len(msgs) > 15:
                session["messages"] = msgs[:2] + msgs[-5:]
                logger.info(f"[Summary] 生成摘要 + 裁剪 (会话 {session_id[:8]})")
        except Exception as e:
            logger.debug(f"[Summary] 摘要生成跳过: {e}")


_summary_generator = SummaryGenerator()

# ══════════════════════════════════════════════════════
# PER 经验记忆 + 并行执行引擎 (P1)
# ══════════════════════════════════════════════════════
_per_memory = PrioritizedEpisodicMemory()


async def execute_tools_parallel(tool_calls_accumulated: dict, session_id: str,
                                  working_state, username: str, user_role: str) -> list:
    """并行执行工具调用 (P1-2)"""
    tc_list = list(tool_calls_accumulated.values())
    if len(tc_list) <= 1:
        tc = tc_list[0]
        func_name = tc["function"]["name"]
        try:
            func_args = json.loads(tc["function"]["arguments"])
        except json.JSONDecodeError:
            return [{"success": False, "error": "JSON解析失败"}]
        db = session_manager.get_database(session_id)
        if db and "database" not in func_args:
            func_args["database"] = db
        if func_name == "execute_admin_sql":
            func_args.update(username=username, role=user_role)
        return [execute_tool_with_healing(func_name, func_args, session_id, working_state)]

    batches = ToolDependencyAnalyzer.analyze(tc_list)
    all_results = []
    for batch in batches:
        if len(batch) == 1:
            tc = tc_list[batch[0]]
            func_name = tc["function"]["name"]
            try:
                func_args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                continue
            db = session_manager.get_database(session_id)
            if db and "database" not in func_args:
                func_args["database"] = db
            if func_name == "execute_admin_sql":
                func_args.update(username=username, role=user_role)
            all_results.append(execute_tool_with_healing(func_name, func_args, session_id, working_state))
        else:
            tasks = []
            for idx in batch:
                tc = tc_list[idx]
                func_name = tc["function"]["name"]
                try:
                    func_args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    continue
                db = session_manager.get_database(session_id)
                if db and "database" not in func_args:
                    func_args["database"] = db
                if func_name == "execute_admin_sql":
                    func_args.update(username=username, role=user_role)
                tasks.append(asyncio.to_thread(
                    execute_tool_with_healing, func_name, func_args, session_id, working_state))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            all_results.extend([r if not isinstance(r, Exception) else {"success": False, "error": str(r)} for r in results])
    return all_results


def execute_tool_with_healing(func_name: str, args: dict, session_id: str,
                               working_state: Optional[AgentWorkingState] = None) -> dict:
    """统一工具执行入口 —— 缓存 → 执行 → 自愈 → 更新工作记忆"""
    # 1. 检查缓存（session 隔离）
    cached = _tool_cache.get(func_name, args, session_id)
    if cached:
        if working_state:
            working_state.record_tool_result(func_name, cached)
        return cached

    # 2. 执行（带自愈）
    result = _healing_executor.execute(func_name, args, session_id)

    # 3. 写入缓存（session 隔离）
    if result.get("success"):
        _tool_cache.set(func_name, args, result, session_id)

    # 4. 更新工作记忆
    if working_state:
        working_state.record_tool_result(func_name, result)

    return result


def build_messages(session_id: str, user_message: str, retrieved_knowledge: str = "",
                   working_state: Optional[AgentWorkingState] = None) -> List[dict]:
    """构建 LLM 消息列表（System Prompt + 历史 + 用户消息 + PER 经验注入）"""
    db = session_manager.get_database(session_id)
    db_context = f"当前连接的是「{db}」数据库。" if db else "用户尚未指定数据库。"
    summary = session_manager.get_summary(session_id)
    memory_context = working_state.to_prompt_context() if working_state else ""

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        current_database=db_context,
        history_summary=summary or "",
        retrieved_knowledge=retrieved_knowledge or "无",
        working_memory=memory_context,
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(session_manager.get_history(session_id))
    messages.append({"role": "user", "content": user_message})
    _per_memory.inject_into_prompt(messages, n=2)
    return messages


# ══════════════════════════════════════════════════════
# 主循环：SSE 流式对话生成器
# ══════════════════════════════════════════════════════

async def chat_stream_generator(
    session_id: str,
    user_message: str,
    database: str = None,
    user_role: str = "reader",
    username: str = "unknown",
    model: str = None,
) -> AsyncGenerator[str, None]:
    """SSE 流式对话 — v3.0 集成版

    集成以下 P0-P2 功能：
    - Orchestrator 多 Agent 编排（复杂任务接管控制流）
    - Token Budget 经济模型 + 自适应降级
    - Adaptive Loop 五维信号终止
    - Self-Healing 失败自愈矩阵
    - CoT 思维链跟踪（DeepSeek R1 reasoning_content）
    - 并行工具调度（Kahn 拓扑排序 + asyncio.gather）
    - LLM Self-Evaluator 自主终止判断
    - PER 优先经验回放（Prompt 注入）
    - Summary Generator 自动对话摘要
    - Cost Tracker 成本追踪
    - Guardrails 防幻觉检查
    """

    # ── 初始化会话 ────────────────────────────
    if not session_manager.get_session(session_id):
        session_manager.create_session(session_id)
    if database:
        session_manager.set_database(session_id, database)
    session_manager.add_message(session_id, "user", user_message)

    working_state = session_manager.get_working_state(session_id)
    working_state.detect_plan_from_user_message(user_message)

    tools = ADMIN_TOOLS if user_role == "admin" else READONLY_TOOLS

    # ── Multi-Agent 路由 ──────────────────────
    route_result = agent_router.route(user_message, user_role)
    logger.info(f"[Router] 意图: {route_result.get('intent')} (置信度: {route_result.get('confidence', 'N/A')})")

    # ── Orchestrator 编排（复杂任务接管控制流） ──
    if len(working_state.plan) > 1:
        try:
            from agent.orchestrator import AgentOrchestrator
            orchestrator = AgentOrchestrator(_get_client, execute_tool_with_healing)
            orch_result = await orchestrator.orchestrate(
                user_message, user_role, session_id, tools
            )
            if orch_result.get("tasks_completed", 0) > 0:
                summary = orch_result.get("summary", "编排完成")
                findings = orch_result.get("findings", [])
                full_answer = f"[Orchestrator] {summary}\n" + "\n".join(f"· {f}" for f in findings[:5])
                yield f"data: {json.dumps({'type': 'content', 'text': full_answer}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                return  # 编排完成后直接返回，不进入主循环
            logger.info(f"[Orchestrator] 编排完成: {orch_result.get('tasks_completed', 0)} 个任务")
        except Exception as e:
            logger.debug(f"[Orchestrator] 编排跳过: {e}")

    # ── 初始化引擎 ────────────────────────────
    budget = TokenBudget(max_total_tokens=30000)
    loop_ctrl = AdaptiveLoopController(max_rounds=8, staleness_window=3)
    completeness_checker = ResultCompletenessChecker()
    self_evaluator = _get_self_evaluator()

    try:
        # ── RAG 检索 ──────────────────────────
        knowledge_items = retrieve_knowledge(user_message)
        knowledge_text = "\n".join(
            f"· {item['metadata'].get('title', '')}: {item['document']}"
            for item in knowledge_items
        ) if knowledge_items else ""

        messages = build_messages(session_id, user_message, knowledge_text, working_state)
        client = _get_client()

        for round_num in range(1, loop_ctrl.max_rounds + 1):
            # ── Token Budget 检查 ──────────────
            status = budget.get_status()
            if status["status"] == "exceeded":
                yield f"data: {json.dumps({'type': 'content', 'text': '(Token预算耗尽，基于当前信息回答)'}, ensure_ascii=False)}\n\n"
                break

            # ── 动态 System Prompt ─────────────
            effective_prompt = DEGRADED_PROMPT if budget.should_degrade() else messages[0]["content"]
            current_db = f"当前连接的是「{session_manager.get_database(session_id)}」数据库。" if session_manager.get_database(session_id) else "未指定数据库。"
            memory_ctx = working_state.to_prompt_context() if working_state else ""
            messages[0]["content"] = effective_prompt.format(
                current_database=current_db,
                retrieved_knowledge=knowledge_text or "无",
                history_summary=session_manager.get_summary(session_id) or "",
                working_memory=memory_ctx,
            )

            # ── LLM 调用（SSE 流式）───────────────
            stream = client.chat.completions.create(
                model=model or settings.deepseek_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                stream=True,
                temperature=0.1,
                max_tokens=4096,
            )

            full_content = ""
            tool_calls_accumulated: Dict[int, dict] = {}

            # ── 解析 SSE Chunk ──────────────────
            for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta is None:
                    continue
                # CoT 思维链提取（DeepSeek R1）
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    yield f"data: {json.dumps({'type': 'reasoning', 'text': delta.reasoning_content}, ensure_ascii=False)}\n\n"
                if delta.content:
                    full_content += delta.content
                    yield f"data: {json.dumps({'type': 'content', 'text': delta.content}, ensure_ascii=False)}\n\n"
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index if tc.index is not None else 0
                        if idx not in tool_calls_accumulated:
                            tool_calls_accumulated[idx] = {"id": tc.id or "", "function": {"name": "", "arguments": ""}}
                        if tc.id:
                            tool_calls_accumulated[idx]["id"] = tc.id
                        if tc.function and tc.function.name:
                            tool_calls_accumulated[idx]["function"]["name"] += tc.function.name
                        if tc.function and tc.function.arguments:
                            tool_calls_accumulated[idx]["function"]["arguments"] += tc.function.arguments

            # ── Token 记录 ─────────────────────
            budget.record_round(0, len(full_content) // 4)

            # ── 处理工具调用 ───────────────────
            if tool_calls_accumulated:
                assistant_tool_msg = {
                    "role": "assistant",
                    "content": full_content or None,
                    "tool_calls": [
                        {"id": tc["id"], "type": "function", "function": tc["function"]}
                        for tc in tool_calls_accumulated.values()
                    ],
                }
                messages.append(assistant_tool_msg)

                # 发送 tool_start 事件
                for tc in tool_calls_accumulated.values():
                    fn = tc["function"]["name"]
                    try:
                        fa = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        fa = {}
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': fn, 'args': fa}, ensure_ascii=False)}\n\n"

                # 并行执行工具调用（P1-2）
                round_results = await execute_tools_parallel(
                    tool_calls_accumulated, session_id, working_state, username, user_role
                )

                # 发送 tool_result 事件
                for i, tc in enumerate(tool_calls_accumulated.values()):
                    result = round_results[i] if i < len(round_results) else {"success": False, "error": "执行异常"}
                    fn = tc["function"]["name"]
                    yield f"data: {json.dumps({'type': 'tool_result', 'tool': fn, 'success': result.get('success', False)}, ensure_ascii=False)}\n\n"
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })
                    if fn == "explain_sql" and result.get("success"):
                        explain_data = result.get("explain_traditional", {})
                        if explain_data and _optimization_trigger.should_trigger(
                            {"type": explain_data.get("type", ""), "rows": explain_data.get("rows", 0)},
                            working_state, budget
                        ):
                            yield f"data: {json.dumps({'type': 'optimize_trigger', 'text': '检测到全表扫描，正在分析...'}, ensure_ascii=False)}\n\n"

                # ── 规则级终止判断 ──────────────
                should_continue, reason = loop_ctrl.evaluate(round_num, list(tool_calls_accumulated.values()), round_results)
                if not should_continue:
                    logger.info(f"[Loop] 规则终止: {reason} (第{round_num}轮)")
                    if full_content:
                        session_manager.add_message(session_id, "assistant", full_content)
                    break

                # ── LLM 语义级终止判断 ──────────
                if should_continue and round_num >= 2:
                    eval_result = self_evaluator.evaluate(
                        user_message, working_state, budget,
                        adapter={"model": settings.deepseek_model}
                    )
                    if eval_result.get("can_answer") and eval_result.get("confidence", 0) > 0.65:
                        conf = eval_result.get("confidence", 0)
                        logger.info(f"[Loop] LLM自评终止: confidence={conf}, reason={eval_result.get('reason')}")
                        stop_text = f"(信息已充分，confidence={conf:.0%})"
                        yield f"data: {json.dumps({'type': 'content', 'text': stop_text}, ensure_ascii=False)}\n\n"
                        if full_content:
                            session_manager.add_message(session_id, "assistant", full_content)
                        break

                # ── Reflection 步骤 ──────────────
                reflection = completeness_checker.check(working_state)
                if reflection.get("should_continue"):
                    logger.info(f"[Loop] Reflection: 需要继续，{reflection.get('suggestion', '')}")
                else:
                    logger.info(f"[Loop] Reflection: 信息完整 (已探索 {len(working_state.explored_tables)} 表)")

                session_manager.increment_tool_call(session_id)
                continue

            # ── 无工具调用 → 最终输出 ──────────
            if full_content:
                session_manager.add_message(session_id, "assistant", full_content)
            break

        else:
            # for-else：循环正常耗尽
            yield f"data: {json.dumps({'type': 'content', 'text': '(查询比较复杂，请换个方式提问)'}, ensure_ascii=False)}\n\n"

        # ── 自动知识沉淀 + PER 存储 ─────
        if working_state and working_state.last_query_sql:
            try:
                _auto_precipitate_knowledge(session_id, working_state, username)
                _per_memory.store(session_id, {
                    "user_intent": user_message[:150],
                    "tool_chain": list(set(tc["function"]["name"]
                                          for tc in list(tool_calls_accumulated.values())))
                }, success=True)
            except Exception:
                pass

    except Exception as e:
        logger.error(f"[Loop] 异常: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'text': '处理请求时出现问题，请重试'}, ensure_ascii=False)}\n\n"

    # ── 自动生成对话摘要 ──────────────────────
    try:
        _summary_generator.maybe_summarize(session_id)
    except Exception:
        pass

    # ── 成本追踪 ──────────────────────────
    try:
        from agent.cost_tracker import cost_tracker
        total_tokens = budget.total_consumed if budget else 0
        cost_tracker.record(session_id, settings.deepseek_model, total_tokens // 2, total_tokens // 2)
    except Exception:
        pass

    # ── 防幻觉检查 + 拦截 ────────────────────
    if full_content:
        from agent.guardrails import _guardrail
        if not _guardrail.validate(full_content, working_state):
            yield f"data: {json.dumps({'type': 'content', 'text': '(⚠ 注意：以上回答可能引用未验证的表名，请谨慎参考)'}, ensure_ascii=False)}\n\n"
            logger.warning("[Guardrail] 回答包含幻觉引用，已向用户发出警告")

    # ── 发送完成信号 ──────────────────────────
    yield "data: [DONE]\n\n"


# ══════════════════════════════════════════════════════
# 自动知识沉淀
# ══════════════════════════════════════════════════════

def _auto_precipitate_knowledge(session_id: str, working_state: AgentWorkingState, username: str):
    """从成功对话中自动沉淀知识到 RAG 知识库"""
    if not working_state.last_query_sql or working_state.last_query_row_count < 1:
        return

    session = session_manager.get_session(session_id)
    if not session:
        return

    messages = session.get("messages", [])
    user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
    ai_msgs = [m["content"] for m in messages if m.get("role") == "assistant"]

    if not user_msgs or not ai_msgs:
        return

    knowledge_text = (
        f"问题: {user_msgs[-1][:200]}\n"
        f"回答: {ai_msgs[-1][:300]}\n"
        f"SQL: {working_state.last_query_sql[:500]}\n"
        f"涉及表: {', '.join(working_state.explored_tables[:5])}"
    )

    try:
        doc_id = add_knowledge(knowledge_text, {
            "category": "自动沉淀",
            "title": user_msgs[-1][:60],
            "source": "auto_precipitation",
            "session_id": session_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tool_chain": json.dumps(list(set(
                tc.get("function", {}).get("name", "")
                for m in messages
                if isinstance(m, dict) and m.get("tool_calls")
                for tc in (m.get("tool_calls") or [])
            ))[:5]),
            "explored_tables": json.dumps(working_state.explored_tables[:5]),
        })
        logger.info(f"[Memory] 自动沉淀知识: {doc_id} ← 会话 {session_id}")
    except Exception as e:
        logger.debug(f"[Memory] 知识沉淀跳过: {e}")