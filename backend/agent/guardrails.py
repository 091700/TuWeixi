"""Output Guardrails + Human-in-the-loop — P2 防幻觉 + 高危审批"""

import re
import logging
import uuid
from typing import Dict, Optional

logger = logging.getLogger("db_agent.guardrails")


# ══════════════════════════════════════════════════════
# Output Guardrail — 防幻觉验证
# ══════════════════════════════════════════════════════

class OutputGuardrail:
    """验证 Agent 回答的准确性和安全性"""

    def validate(self, response: str, working_state) -> bool:
        """检查回答中提到的表名是否在 explored_tables 中

        Returns:
            True 如果验证通过（无幻觉迹象）
        """
        if not working_state or not working_state.explored_tables:
            return True

        mentioned_tables = re.findall(r'[`\'](\w+)[`\']', response)
        if not mentioned_tables:
            return True

        explored_lower = {t.lower() for t in working_state.explored_tables}
        for table in mentioned_tables:
            if table.lower() not in explored_lower:
                logger.warning(f"[Guardrail] 检测到可能的幻觉: 提到未探索表 `{table}`")
                return False
        return True


_guardrail = OutputGuardrail()


# ══════════════════════════════════════════════════════
# Human-in-the-loop — 高危操作审批
# ══════════════════════════════════════════════════════

class PendingApprovalQueue:
    """高危操作审批队列 — DROP/TRUNCATE 等操作需二次确认"""

    DANGEROUS_PATTERNS = [
        (r"\bDROP\b", "DROP 操作"),
        (r"\bTRUNCATE\b", "TRUNCATE 操作"),
        (r"\bALTER\s+TABLE\b", "ALTER TABLE 操作"),
    ]

    def __init__(self):
        self._pending: Dict[str, dict] = {}

    def requires_approval(self, sql: str) -> Optional[str]:
        """检查 SQL 是否需要审批，返回危险操作类型"""
        for pattern, desc in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                return desc
        return None

    def request_approval(self, operation: str, details: str, sql: str) -> str:
        """创建审批请求，返回 approval_id"""
        approval_id = uuid.uuid4().hex[:12]
        self._pending[approval_id] = {
            "operation": operation,
            "details": details,
            "sql": sql,
            "approved": None,
        }
        logger.info(f"[Approval] 高危操作待审批: {operation} (id={approval_id})")
        return approval_id

    def approve(self, approval_id: str) -> bool:
        if approval_id not in self._pending:
            return False
        self._pending[approval_id]["approved"] = True
        return True

    def reject(self, approval_id: str) -> bool:
        if approval_id not in self._pending:
            return False
        self._pending[approval_id]["approved"] = False
        return True

    def is_approved(self, approval_id: str) -> Optional[bool]:
        entry = self._pending.get(approval_id)
        return entry["approved"] if entry else None


approval_queue = PendingApprovalQueue()