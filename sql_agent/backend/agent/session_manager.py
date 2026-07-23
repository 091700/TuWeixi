"""会话管理器 —— 内存级会话生命周期管理

功能：
- 会话创建 / 销毁 / 查询
- 消息增删及智能裁剪（基于重要性评分）
- 工作记忆（AgentWorkingState）绑定
- TTL 过期清理
- 会话持久化到 MySQL（agent_sessions 表）

设计思路：
- 内存为主、MySQL 为辅的混合存储
- get_history() 过滤 _timestamp 字段，防止泄露给 LLM
- trim_history() 基于规则评分保留关键消息，避免 token 爆炸
"""

import json
import time
import uuid
import re
import logging
from typing import List, Dict, Optional

from config import settings
from agent.loop_engine import AgentWorkingState

logger = logging.getLogger("db_agent.session")


class SessionManager:
    """内存级会话管理器 — 支持 AgentWorkingState + TTL清理 + Running Summary"""

    def __init__(self):
        self._sessions: Dict[str, dict] = {}

    # ══════════════════════════════════════════════════════
    # 会话生命周期
    # ══════════════════════════════════════════════════════

    def create_session(self, session_id: str = None) -> str:
        """创建新会话

        Args:
            session_id: 可选，指定 session_id。不指定则自动生成 16 位 hex

        Returns:
            新会话的 session_id
        """
        sid = session_id or uuid.uuid4().hex[:16]
        self._sessions[sid] = {
            "messages": [],
            "created_at": time.time(),
            "last_active": time.time(),
            "database": None,
            "last_table": None,
            "summary": None,
            "tool_call_count": 0,
            "round_count": 0,
            "working_state": AgentWorkingState(),
        }
        return sid

    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话完整数据"""
        return self._sessions.get(session_id)

    # ══════════════════════════════════════════════════════
    # 工作记忆
    # ══════════════════════════════════════════════════════

    def get_working_state(self, session_id: str) -> Optional[AgentWorkingState]:
        """获取会话绑定的 AgentWorkingState"""
        s = self._sessions.get(session_id)
        return s.get("working_state") if s else None

    # ══════════════════════════════════════════════════════
    # 消息管理
    # ══════════════════════════════════════════════════════

    def add_message(self, session_id: str, role: str, content: str):
        """向会话添加一条消息

        Args:
            session_id: 会话 ID
            role: 消息角色（user / assistant / tool）
            content: 消息内容
        """
        session = self._sessions.get(session_id)
        if not session:
            return
        session["messages"].append({
            "role": role,
            "content": content,
            "_timestamp": time.time(),   # 内部用，不传给 LLM
        })
        session["last_active"] = time.time()

        # 如果助手回复中提到了数据库名，自动更新会话的当前数据库
        if role == "assistant" and content:
            db_match = re.search(
                r'(?:数据库|库|database)\s*[:：]?\s*[`\'\"]?(\w+)[`\'\"]?',
                content,
            )
            if db_match:
                session["database"] = db_match.group(1)

    def get_history(self, session_id: str) -> List[dict]:
        """获取会话历史（过滤内部字段）

        B1 修复：不返回 _timestamp 字段，防止泄露给 LLM。
        返回格式：{"role": str, "content": str}
        """
        session = self._sessions.get(session_id)
        if not session:
            return []
        msgs = session["messages"]
        max_msgs = settings.session_max_messages
        if len(msgs) > max_msgs:
            msgs = msgs[:2] + msgs[-(max_msgs - 2):]
        return [{"role": m["role"], "content": m.get("content", "")} for m in msgs]

    def trim_history(self, session_id: str):
        """智能裁剪 —— 基于语义重要性评分保留关键消息

        评分规则：
        - 包含 SQL 语句的消息 +5
        - 包含错误信息的消息 +4
        - tool 角色的消息 +3
        - 其余 +1

        策略：保留头 2 条 + 尾 10 条 + 中间评分最高的 10 条
        """
        session = self._sessions.get(session_id)
        if not session:
            return
        msgs = session["messages"]
        if len(msgs) <= 30:
            return

        head = msgs[:2]
        tail = msgs[-10:]
        middle = msgs[2:-10]

        def _score(m):
            c = m.get("content", "") or ""
            s = 1
            if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE)\b', c, re.IGNORECASE):
                s += 5
            if re.search(r'(?:error|failed|失败|错误)', c, re.IGNORECASE):
                s += 4
            if m.get("role") == "tool":
                s += 3
            return s

        scored = [(_score(m), m) for m in middle]
        scored.sort(key=lambda x: x[0], reverse=True)
        kept = [m for _, m in scored[:10]]
        kept.sort(key=middle.index)   # 保持时间顺序
        session["messages"] = head + kept + tail
        logger.debug(f"[Session] 裁剪: {len(msgs)} → {len(session['messages'])} 条消息")

    # ══════════════════════════════════════════════════════
    # 数据库 / 摘要
    # ══════════════════════════════════════════════════════

    def set_database(self, session_id: str, database: str):
        """设置会话的当前工作数据库"""
        s = self._sessions.get(session_id)
        if s:
            s["database"] = database
            ws = s.get("working_state")
            if ws:
                ws.current_database = database

    def get_database(self, session_id: str) -> Optional[str]:
        s = self._sessions.get(session_id)
        return s.get("database") if s else None

    def get_summary(self, session_id: str) -> Optional[str]:
        s = self._sessions.get(session_id)
        return s.get("summary") if s else None

    def set_summary(self, session_id: str, summary: str):
        s = self._sessions.get(session_id)
        if s:
            s["summary"] = summary
            logger.info(f"[Session] Running Summary 已更新 (会话 {session_id[:8]}...)")

    # ══════════════════════════════════════════════════════
    # 统计计数
    # ══════════════════════════════════════════════════════

    def increment_tool_call(self, session_id: str):
        s = self._sessions.get(session_id)
        if s:
            s["tool_call_count"] = s.get("tool_call_count", 0) + 1
            ws = s.get("working_state")
            if ws:
                ws.tool_call_count += 1

    def increment_round(self, session_id: str):
        s = self._sessions.get(session_id)
        if s:
            s["round_count"] = s.get("round_count", 0) + 1

    def get_round_count(self, session_id: str) -> int:
        s = self._sessions.get(session_id)
        return s.get("round_count", 0) if s else 0

    # ══════════════════════════════════════════════════════
    # TTL 清理与持久化
    # ══════════════════════════════════════════════════════

    def cleanup_expired(self):
        """清理过期会话（基于 SESSION_TTL 配置）"""
        now = time.time()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s.get("last_active", now) > settings.session_ttl
        ]
        for sid in expired:
            del self._sessions[sid]
        if expired:
            logger.info(f"[Session] 清理 {len(expired)} 个过期会话")

    def persist_session(self, session_id: str, username: str):
        """会话持久化到 MySQL agent_sessions 表"""
        session = self._sessions.get(session_id)
        if not session or len(session["messages"]) < 2:
            return
        try:
            from auth.database import _get_auth_conn
            conn = _get_auth_conn()
            try:
                now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                messages_json = json.dumps(
                    session["messages"][-50:], ensure_ascii=False, default=str
                )
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO agent_sessions (id, username, messages_json, database_name,
                           tool_call_count, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           ON DUPLICATE KEY UPDATE messages_json=%s, updated_at=%s""",
                        (session_id, username, messages_json,
                         session.get("database", ""),
                         session.get("tool_call_count", 0), now, now,
                         messages_json, now),
                    )
                conn.commit()
                logger.debug(f"[Session] 持久化会话 {session_id[:8]}... ")
            finally:
                conn.close()
        except Exception as e:
            logger.debug(f"[Session] 持久化跳过: {e}")