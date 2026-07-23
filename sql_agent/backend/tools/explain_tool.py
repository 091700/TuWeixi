"""工具3: explain_sql —— 对 SQL 执行 EXPLAIN 分析，用于慢 SQL 诊断"""
import re
import pymysql
from config import settings
from security.sql_validator import validate_sql
from security.connection_pool import pool_manager


def explain_sql(database: str, sql: str) -> dict:
    """
    对指定的 SQL 执行 EXPLAIN 分析，返回执行计划详情

    执行 EXPLAIN + EXPLAIN FORMAT=JSON + SHOW WARNINGS
    全面分析查询性能

    Args:
        database: 目标数据库名
        sql: 待分析的 SELECT 语句

    Returns:
        {
            "success": bool,
            "explain_traditional": [...],   # EXPLAIN 表格结果
            "explain_json": {...},          # EXPLAIN FORMAT=JSON 结果
            "warnings": [...],              # SHOW WARNINGS
            "analyzed": bool,               # 是否已完成自动分析标记
        }
    """
    # 安全检查
    is_safe, error_msg = validate_sql(sql, allow_explain=False)
    if not is_safe:
        return {"success": False, "error": error_msg}

    try:
        conn = pool_manager.get_connection(database)
    except pymysql.MySQLError as e:
        return {"success": False, "error": f"数据库连接失败: {e}"}

    result = {
        "success": False,
        "explain_traditional": [],
        "explain_json": {},
        "warnings": [],
    }

    try:
        with conn.cursor() as cursor:
            # 1. 标准 EXPLAIN
            cursor.execute(f"EXPLAIN {sql}")
            explain_rows = cursor.fetchall()
            result["explain_traditional"] = explain_rows

            # 2. EXPLAIN FORMAT=JSON (更详细)
            try:
                cursor.execute(f"EXPLAIN FORMAT=JSON {sql}")
                json_row = cursor.fetchone()
                result["explain_json"] = json_row.get("EXPLAIN") if json_row else {}
            except Exception:
                result["explain_json"] = {"error": "EXPLAIN FORMAT=JSON 不可用"}

            # 3. SHOW WARNINGS
            try:
                cursor.execute("SHOW WARNINGS")
                result["warnings"] = cursor.fetchall()
            except Exception:
                pass

        result["success"] = True

        # 4. 自动标记分析要点
        result["analysis_summary"] = _auto_analyze(explain_rows)

    except pymysql.MySQLError as e:
        result["success"] = False
        result["error"] = f"EXPLAIN 执行失败: {e}"
    finally:
        conn.close()

    return result


def _auto_analyze(explain_rows: list) -> dict:
    """
    自动分析 EXPLAIN 结果，提取关键风险指标

    返回一个分析摘要，供大模型在生成优化建议时参考
    """
    issues = []
    warnings_list = []

    for i, row in enumerate(explain_rows):
        step = row.get("id", i + 1)
        select_type = str(row.get("select_type", ""))
        table = str(row.get("table", ""))
        access_type = str(row.get("type", "ALL"))
        possible_keys = str(row.get("possible_keys", ""))
        key_used = str(row.get("key", ""))
        key_len = str(row.get("key_len", ""))
        rows_examined = row.get("rows", 0)
        extra = str(row.get("Extra", ""))
        filtered = row.get("filtered", 100.0)

        # 全表扫描检测
        if access_type == "ALL":
            issues.append(
                f"⚠️ 步骤 {step}: 表 `{table}` 为全表扫描 (type=ALL)，"
                f"预计扫描 {rows_examined} 行。建议添加索引"
            )

        # 索引未命中检测
        if access_type in ("ALL", "index") and possible_keys:
            issues.append(
                f"⚠️ 步骤 {step}: 表 `{table}` 有可用索引 ({possible_keys})"
                f"但未命中，实际使用 {key_used or '无'}"
            )

        # Using filesort
        if "Using filesort" in extra:
            issues.append(
                f"⚠️ 步骤 {step}: 需要文件排序 (Using filesort)，"
                f"建议优化 ORDER BY 或添加覆盖索引"
            )

        # Using temporary
        if "Using temporary" in extra:
            issues.append(
                f"⚠️ 步骤 {step}: 使用临时表 (Using temporary)，"
                f"通常由 GROUP BY 或 DISTINCT 触发，建议优化"
            )

        # Using where（行数多时告警）
        if "Using where" in extra and rows_examined > 10000:
            warnings_list.append(
                f"💡 步骤 {step}: 在 {rows_examined} 行上做 WHERE 过滤，"
                f"考虑用索引覆盖过滤条件"
            )

        # filtered 比例低
        if filtered and float(filtered) < 10:
            warnings_list.append(
                f"💡 步骤 {step}: 过滤后仅保留 {filtered}% 数据，选择性高，可考虑针对性索引"
            )

        # 索引长度异常
        if key_len and str(key_len) in ("4", "8") and rows_examined > 1000:
            warnings_list.append(
                f"🔍 步骤 {step}: 索引长度 {key_len}，可能在使用单列索引，"
                f"但扫描行数较多 ({rows_examined})"
            )

    return {
        "total_steps": len(explain_rows),
        "issues": issues,
        "warnings": warnings_list,
        "has_full_scan": any(r.get("type") == "ALL" for r in explain_rows),
        "has_filesort": any("Using filesort" in str(r.get("Extra", "")) for r in explain_rows),
        "has_temporary": any("Using temporary" in str(r.get("Extra", "")) for r in explain_rows),
    }


# ── Tool Definition Schema ──────────────────────────
TOOL_EXPLAIN_DEFINITION = {
    "type": "function",
    "function": {
        "name": "explain_sql",
        "description": (
            "对指定的 SQL 语句执行 EXPLAIN 分析，返回执行计划详情"
            "（含标准 EXPLAIN 表格、JSON 格式计划、优化器警告）。"
            "用于诊断慢 SQL 性能瓶颈"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "待分析的 SELECT 语句",
                },
                "database": {
                    "type": "string",
                    "description": "目标数据库名",
                },
            },
            "required": ["sql", "database"],
        },
    },
}