"""工具6: format_sql —— SQL 自动格式化与美化"""
import sqlparse


def format_sql(sql: str, style: str = "standard") -> dict:
    """
    格式化 SQL 语句，使其可读性更强

    Args:
        sql: 待格式化的 SQL 语句
        style: 格式化风格，可选 standard/compact

    Returns:
        {"success": bool, "original": str, "formatted": str}
    """
    try:
        if style == "compact":
            formatted = sqlparse.format(
                sql,
                reindent=True,
                keyword_case="upper",
                indent_width=2,
                strip_comments=True,
            )
        else:
            formatted = sqlparse.format(
                sql,
                reindent=True,
                keyword_case="upper",
                indent_width=2,
            )
        return {
            "success": True,
            "original": sql,
            "formatted": formatted.strip(),
        }
    except Exception as e:
        return {"success": False, "error": f"SQL 格式化失败: {e}"}


# ── Tool Definition Schema ──────────────────────────
TOOL_FORMAT_SQL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "format_sql",
        "description": "格式化/美化 SQL 语句，提高可读性。将 SQL 转为大写关键字、统一缩进",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "待格式化的 SQL 语句",
                },
                "style": {
                    "type": "string",
                    "enum": ["standard", "compact"],
                    "description": "格式化风格：standard(带注释) / compact(去注释)",
                },
            },
            "required": ["sql"],
        },
    },
}