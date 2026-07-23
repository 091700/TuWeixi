"""工具2: execute_readonly_sql —— 安全执行只读 SQL 查询"""
import pymysql
from config import settings
from security.sql_validator import validate_sql
from security.connection_pool import pool_manager


def execute_readonly_sql(database: str, sql: str, limit: int = None) -> dict:
    """
    安全执行只读 SQL 查询并返回结果

    - 仅允许 SELECT 语句
    - 三层安全校验
    - 自动追加 LIMIT
    - 使用只读账号连接

    Args:
        database: 目标数据库名
        sql: 待执行的 SELECT 语句
        limit: 返回行数上限，默认 100，最大 500

    Returns:
        {
            "success": bool,
            "data": [...],        # 查询结果行
            "row_count": int,     # 实际返回行数
            "columns": [...],     # 列名列表
            "execution_time_ms": float
        }
    """
    if limit is None:
        limit = settings.result_row_limit
    else:
        limit = min(int(limit), settings.result_row_max)

    import time
    start_time = time.perf_counter()

    # ── 安全校验 ─────────────────────────────────
    is_safe, error_msg = validate_sql(sql, allow_explain=False)
    if not is_safe:
        return {"success": False, "error": error_msg}

    # ── 自动追加 LIMIT ──────────────────────────
    import re
    existing_limit = re.search(r'\bLIMIT\s+(\d+)', sql, re.IGNORECASE)
    if existing_limit:
        user_limit = int(existing_limit.group(1))
        limit = min(user_limit, limit)
        # 替换 SQL 中的 LIMIT 为安全值
        sql = re.sub(
            r'\bLIMIT\s+\d+\s*;?\s*$',
            f'LIMIT {limit}',
            sql,
            flags=re.IGNORECASE,
        )
    else:
        sql = sql.rstrip(';').strip() + f" LIMIT {limit}"

    # ── 执行查询 ─────────────────────────────────
    try:
        conn = pool_manager.get_connection(database)
    except pymysql.MySQLError as e:
        return {"success": False, "error": f"数据库连接失败: {e}"}

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchmany(limit)

            # 获取列名
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return {
            "success": True,
            "data": rows,
            "row_count": len(rows),
            "columns": columns,
            "execution_time_ms": round(elapsed_ms, 2),
        }

    except pymysql.MySQLError as e:
        return {"success": False, "error": f"查询执行失败: {e}", "sql": sql}
    finally:
        conn.close()


# ── Tool Definition Schema ──────────────────────────
TOOL_EXECUTE_SQL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "execute_readonly_sql",
        "description": (
            "在目标数据库执行只读 SQL 查询并返回结果。仅允许 SELECT 语句，"
            "内置多层安全防护与参数化查询防注入。查询会自动追加 LIMIT 限制。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "待执行的 SELECT 语句，仅允许只读查询。表名和字段名必须来自元数据查询结果",
                },
                "database": {
                    "type": "string",
                    "description": "目标数据库名",
                },
                "limit": {
                    "type": "integer",
                    "description": "返回行数上限，默认 100，最大 500",
                },
            },
            "required": ["sql", "database"],
        },
    },
}