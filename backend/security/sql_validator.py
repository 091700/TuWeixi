"""SQL 安全校验器 —— 三层安全沙箱的体验层与防护层"""
import re
import sqlparse
from typing import Tuple

# ── 危险关键字黑名单 ──────────────────────────────────
DANGEROUS_KEYWORDS: set = {
    "DROP", "TRUNCATE", "ALTER", "DELETE", "UPDATE", "INSERT",
    "CREATE", "REPLACE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
    "LOAD", "RENAME", "SHUTDOWN", "CALL",
}

# ── SQL 注入特征模式 ─────────────────────────────────
INJECTION_PATTERNS: list = [
    # 注释符截断（在末尾截断后续 SQL）
    r"(?im)(--|\#|\/\*).*$",
    # 堆叠查询（分号后跟随写操作）
    r"(?i);\s*(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|TRUNCATE|EXEC|SELECT)",
    # UNION 注入
    r"(?i)UNION\s+(ALL\s+)?SELECT",
    # 文件写入
    r"(?i)INTO\s+(OUTFILE|DUMPFILE)",
    # 时间盲注
    r"(?i)SLEEP\s*\(\s*\d+\s*\)",
    # 基准测试注入
    r"(?i)BENCHMARK\s*\(\s*\d+\s*,",
    # 信息模式探测
    r"(?i)information_schema\.",
    # CHAR() 编码绕过
    r"(?i)CHAR\s*\(\s*\d+",
    # 十六进制编码注入
    r"(?i)0x[0-9a-fA-F]{4,}",
    # 子查询嵌套危险操作
    r"(?i)\(\s*SELECT\s+.*(?:DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|TRUNCATE)",
    # 系统变量探测
    r"(?i)@@(?:version|datadir|basedir|hostname|tmpdir)",
]

# ── 安全白名单：允许的 SQL 关键字（仅 SELECT 相关）─
ALLOWED_LEADING_KEYWORDS = {"SELECT", "EXPLAIN", "DESCRIBE", "DESC", "SHOW"}


def _strip_sql_comments(sql: str) -> str:
    """移除 SQL 中的注释，用于安全检测"""
    # 移除单行注释
    sql = re.sub(r'--[^\n]*', '', sql)
    # 移除多行注释
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    return sql


def validate_sql(sql: str, allow_explain: bool = True) -> Tuple[bool, str]:
    """
    校验 SQL 安全性，返回 (是否安全, 错误信息)

    检查策略（纵深防御）：
    1. 类型检查 —— 只能以 SELECT/EXPLAIN/DESCRIBE/SHOW 开头
    2. 危险关键字检查 —— 拦截所有 DML/DDL
    3. SQL 注入特征检测 —— 堆叠查询、UNION、盲注等
    4. 参数化标记 —— 标记为安全 SQL，由执行器统一执行
    """
    stripped = sql.strip()

    if not stripped:
        return False, "SQL 语句不能为空"

    # 1. 类型检查：仅允许只读操作
    allowed_leading = ALLOWED_LEADING_KEYWORDS.copy()
    if allow_explain:
        allowed_leading.add("EXPLAIN")

    try:
        parsed = sqlparse.parse(stripped)
        if not parsed or not parsed[0].tokens:
            return False, "无法解析 SQL 语句"

        first_token = parsed[0].token_first(skip_cm=True)
        if first_token is None:
            return False, "无法识别 SQL 类型"
        first_keyword = str(first_token).upper().strip()
    except Exception:
        # sqlparse 解析失败时回退到正则
        first_keyword = stripped.split()[0].upper() if stripped.split() else ""

    if first_keyword not in allowed_leading:
        return False, f"仅支持 {', '.join(sorted(allowed_leading))} 查询，不支持 {first_keyword} 操作"

    # 2. 危险关键字检查
    upper_sql = stripped.upper()
    for keyword in DANGEROUS_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', upper_sql):
            return False, f"检测到危险操作关键字: {keyword}，已拦截"

    # 3. SQL 注入特征检测
    comment_free_sql = _strip_sql_comments(stripped)
    for i, pattern in enumerate(INJECTION_PATTERNS):
        if re.search(pattern, comment_free_sql, re.IGNORECASE):
            return False, "检测到 SQL 注入特征，已拦截"

    return True, ""


def validate_sql_list(queries: list) -> Tuple[bool, str]:
    """批量校验多条 SQL"""
    for i, sql in enumerate(queries):
        ok, err = validate_sql(sql)
        if not ok:
            return False, f"第 {i + 1} 条 SQL 校验失败: {err}"
    return True, ""