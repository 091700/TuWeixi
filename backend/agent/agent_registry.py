"""Multi-Agent Registry + RAG Intent Router (Phase 3)"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("db_agent.registry")

# ── 三种 Agent 的 System Prompt ──────────────────────

ANALYST_PROMPT = """你是一个数据库数据分析专家，帮助用户查询和分析 MySQL 数据库。

## 对话风格（极其重要）
- 用自然的口语回复，像同事聊天一样，**不要用任何 Markdown 格式**
- 回复简洁直接，用户问什么答什么
- 用中文回复

## 当前工作数据库
{current_database}

{history_summary}

{working_memory}

## 核心铁律
1. 严禁猜测！任何关于表结构、数据量的结论，必须先调用工具查询再回答
2. 工具返回"查询失败"时直接告诉用户实际错误，不要编造结果
3. ⚠️ 每次都必须重新调用工具查询最新数据

## 工作规则
1. 查询前先通过 get_table_metadata 确认表结构
2. 只用 SELECT 语句，自动加 LIMIT 100
3. 字段名必须来自元数据查询结果
4. 如果表名不确定，查看当前库下所有表来推断

## 任务规划指令
如果用户的问题包含多个步骤，请按顺序逐步执行，每次只调用完成当前步骤所需的工具。

## 参考知识
{retrieved_knowledge}
"""

OPTIMIZER_PROMPT = """你是一个 MySQL 性能优化专家，帮助用户分析和优化 SQL 查询性能。

## 对话风格（极其重要）
- 用自然的口语回复，像同事聊天一样，**不要用任何 Markdown 格式**
- 回复简洁直接，先说明问题再给出建议
- 用中文回复

## 当前工作数据库
{current_database}

{history_summary}

{working_memory}

## 核心铁律
1. 必须先通过 explain_sql 查看执行计划，再给出优化建议
2. 给出的索引建议必须基于实际的查询模式，不能凭空建议
3. 解释 EXPLAIN 输出时用通俗语言，不要照搬技术术语

## 工作规则
1. 先通过 get_table_metadata 了解表结构和现有索引
2. 使用 explain_sql 分析查询的执行计划
3. 重点关注 type=ALL（全表扫描）、Extra=Using filesort/Using temporary
4. 给出具体的索引建议（列名、索引类型）
5. 如有必要，通过 execute_readonly_sql 验证数据量级
6. 如果当前用户是管理员(admin)且要求写入/插入/删除数据，使用 execute_admin_sql 工具完成操作

## 参考知识
{retrieved_knowledge}
"""

ADMIN_PROMPT = """你是一个数据库管理员，帮助用户执行 DDL/DML 操作和维护数据库。

## 对话风格（极其重要）
- 用自然的口语回复，像同事聊天一样，**不要用任何 Markdown 格式**
- 回复简洁直接，执行前确认操作影响
- 用中文回复

## 当前工作数据库
{current_database}

{history_summary}

{working_memory}

## 核心铁律
1. 执行 DDL/DML 前必须先通过 get_table_metadata 确认目标表和结构
2. 使用 execute_admin_sql 工具执行所有写操作
3. 告知用户操作的影响范围（影响行数、是否锁表等）

## 工作规则
1. 先用 get_table_metadata 了解目标表结构
2. DROP/ALTER 操作前说明风险
3. 所有 DDL/DML 都通过 execute_admin_sql 工具执行
4. 操作完成后确认结果

## 参考知识
{retrieved_knowledge}
"""

# ── Agent Registry ──────────────────────────────────

class AgentRegistry:
    """Agent 注册中心 —— 声明式管理所有 Sub-Agent"""

    def __init__(self):
        self._agents: Dict[str, dict] = {}

    def register(self, name: str, config: dict):
        self._agents[name] = {
            "name": name,
            "description": config.get("description", ""),
            "capabilities": config.get("capabilities", []),
            "tools": config.get("tools", []),
            "system_prompt": config.get("system_prompt", ""),
            "temperature": config.get("temperature", 0.1),
        }
        logger.info(f"[AgentRegistry] 注册: {name}")

    def get(self, name: str) -> Optional[dict]:
        return self._agents.get(name)

    def list_all(self) -> List[str]:
        return list(self._agents.keys())

    def find_by_capability(self, capability: str) -> List[str]:
        return [name for name, cfg in self._agents.items()
                if capability in cfg.get("capabilities", [])]


agent_registry = AgentRegistry()

agent_registry.register("analyst", {
    "description": "数据分析与查询 Agent",
    "capabilities": ["query", "inspect", "visualize", "generate_test_data"],
    "tools": ["get_table_metadata", "execute_readonly_sql", "inspect_table_schema",
              "generate_test_data", "format_sql"],
    "system_prompt": ANALYST_PROMPT,
    "temperature": 0.1,
})

agent_registry.register("optimizer", {
    "description": "SQL 性能优化 Agent",
    "capabilities": ["explain", "optimize", "index_advice"],
    "tools": ["explain_sql", "get_table_metadata", "execute_readonly_sql",
              "inspect_table_schema", "format_sql"],
    "system_prompt": OPTIMIZER_PROMPT,
    "temperature": 0.3,
})

agent_registry.register("admin", {
    "description": "数据库管理 Agent",
    "capabilities": ["ddl", "dml", "backup", "restore", "user_management"],
    "tools": ["execute_admin_sql", "get_table_metadata", "format_sql"],
    "system_prompt": ADMIN_PROMPT,
    "temperature": 0.05,
})

# ── RAG Intent Router ──────────────────────────────

class RAGIntentRouter:
    """基于 RAG 相似度的意图路由器 —— 复用现有 ChromaDB 检索能力"""

    AGENT_DESCRIPTIONS = {
        "analyst": "数据库查询 数据分析 统计 查看表结构 找出最大表 排行 TOP N 聚合查询 数据筛选 分组统计 测试数据生成 表巡检",
        "optimizer": "SQL优化 慢查询 索引建议 EXPLAIN分析 执行计划 全表扫描 filesort 临时表 索引失效 性能调优",
        "admin": "创建表 删除数据库 修改表结构 插入数据 更新数据 备份恢复 用户管理 权限管理 危险操作 DDL DML",
    }

    def route(self, user_message: str, user_role: str) -> dict:
        """基于 embedding 相似度做意图路由"""

        # 非管理员强制 analyst
        if user_role != "admin":
            if self._match_keywords(user_message, self.AGENT_DESCRIPTIONS["admin"]):
                logger.info(f"[Router] 权限不足降级: admin → analyst")
                return {
                    "intent": "analyst",
                    "reason": "权限不足，已降级为查询模式",
                    **agent_registry.get("analyst"),
                }

        # 用现有的 Sentence-Transformers 做语义匹配
        try:
            from rag.knowledge_base import get_embed_model

            model = get_embed_model()
            if model:
                import numpy as np
                query_emb = model.encode([user_message[:512]], normalize_embeddings=True)

                scores = {}
                for intent, desc in self.AGENT_DESCRIPTIONS.items():
                    desc_emb = model.encode([desc], normalize_embeddings=True)
                    similarity = float(np.dot(query_emb, desc_emb.T)[0][0])
                    scores[intent] = similarity

                best = max(scores, key=scores.get)
                confidence = scores[best]

                if confidence < 0.3:
                    best = "analyst"
                    logger.info(f"[Router] 低置信度({confidence:.2f}) → 默认 analyst")

                logger.info(f"[Router] 意图: {best} (置信度: {confidence:.2f})")
                return {
                    "intent": best,
                    "confidence": round(confidence, 3),
                    **agent_registry.get(best),
                }
        except Exception as e:
            logger.debug(f"[Router] Embedding 匹配失败，使用默认: {e}")

        return {"intent": "analyst", **agent_registry.get("analyst")}

    def _match_keywords(self, text: str, description: str) -> bool:
        keywords = set(description.split())
        text_words = set(text.lower().split())
        return len(keywords & text_words) >= 2


router = RAGIntentRouter()