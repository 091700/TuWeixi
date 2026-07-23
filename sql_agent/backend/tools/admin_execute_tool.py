"""管理员专用工具: execute_admin_sql —— 执行高风险 DDL/DML 操作，自动备份 + 审计"""
import re
import uuid
import pymysql

from config import settings
from security.backup_manager import backup_before_dangerous
from auth.database import add_audit_log
from security.connection_pool import pool_manager


def _classify_operation(sql: str) -> tuple[str, str, str]:
    upper = sql.strip().upper()

    db_match = re.match(r'(CREATE|DROP)\s+DATABASE\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?`?(\w+)`?', upper)
    if db_match:
        return f"{db_match.group(1)}_DATABASE", db_match.group(2), db_match.group(2)

    table_match = re.search(
        r'(?:CREATE|DROP|ALTER|TRUNCATE)\s+(?:TEMPORARY\s+)?TABLE\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?`?(\w+)`?',
        upper
    )
    if table_match:
        action_map = {
            "CREATE": "CREATE_TABLE", "DROP": "DROP_TABLE",
            "ALTER": "ALTER_TABLE", "TRUNCATE": "TRUNCATE_TABLE",
        }
        keyword = re.match(r'(\w+)', upper).group(1)
        return action_map.get(keyword, "OTHER"), None, table_match.group(1)

    dml_match = re.search(r'(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+`?(\w+)`?', upper)
    if dml_match:
        action_map = {
            "INSERT": "INSERT_INTO", "UPDATE": "UPDATE_TABLE", "DELETE": "DELETE_FROM",
        }
        keyword = re.match(r'(\w+)', upper).group(1)
        return action_map.get(keyword, "OTHER"), None, dml_match.group(1)

    return "OTHER", None, ""


def execute_admin_sql(
    sql: str,
    database: str = None,
    username: str = "unknown",
    role: str = "admin",
    ip_address: str = "",
) -> dict:
    import time
    start_time = time.perf_counter()

    stripped = sql.strip()
    if not stripped:
        return {"success": False, "message": "SQL 语句不能为空"}

    first_word = stripped.split()[0].upper()
    if first_word in ("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN"):
        return {"success": False, "message": "查询操作请使用只读通道"}

    operation, op_database, target = _classify_operation(stripped)
    effective_db = database or op_database

    backup_path = ""
    if operation in ("DROP_DATABASE", "DROP_TABLE", "TRUNCATE_TABLE", "ALTER_TABLE"):
        if effective_db and target:
            backup_path = backup_before_dangerous(operation, effective_db, target, username) or ""

    conn = None
    try:
        conn = pymysql.connect(
            host=settings.mysql_host, port=settings.mysql_port,
            user=settings.mysql_user, password=settings.mysql_password,
            database=(None if operation == "CREATE_DATABASE" else effective_db),
            charset="utf8mb4", autocommit=True,
            read_timeout=30, connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
        )
        with conn.cursor() as cursor:
            cursor.execute(stripped)
            affected = cursor.rowcount if cursor.rowcount is not None else 0

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        add_audit_log(
            username=username, role=role, action=operation,
            target=f"{effective_db or ''}.{target or ''}" if target else effective_db or "N/A",
            detail=stripped[:2000], result="SUCCESS",
            backup_path=backup_path, ip_address=ip_address,
        )

        return {
            "success": True, "message": f"{operation} 执行成功",
            "affected_rows": affected, "backup_path": backup_path,
            "operation": operation, "execution_time_ms": round(elapsed_ms, 2),
        }

    except pymysql.MySQLError as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        add_audit_log(
            username=username, role=role, action=operation,
            target=f"{effective_db or ''}.{target or ''}" if target else effective_db or "N/A",
            detail=stripped[:2000], result="FAILED",
            backup_path=backup_path, ip_address=ip_address,
        )
        return {
            "success": False, "message": f"执行失败: {e}",
            "affected_rows": 0, "backup_path": backup_path,
            "operation": operation, "execution_time_ms": round(elapsed_ms, 2),
        }
    except Exception as e:
        return {"success": False, "message": f"未知错误: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


TOOL_ADMIN_SQL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "execute_admin_sql",
        "description": (
            "【管理员专用】执行数据库 DDL/DML 操作。执行前自动备份，所有操作记录到审计日志。"
            "注意：普通 SELECT 查询请使用 execute_readonly_sql 工具。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "待执行的 SQL 语句"},
                "database": {"type": "string", "description": "目标数据库名"},
            },
            "required": ["sql"],
        },
    },
}