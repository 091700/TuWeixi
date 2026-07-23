"""工具4: inspect_table_schema —— 表结构反模式自动巡检"""
import re
import pymysql
from config import settings
from security.connection_pool import pool_manager


# ── 命名规范正则 ──────────────────────────────────
VALID_TABLE_NAME = re.compile(r'^[a-z][a-z0-9_]*$', re.IGNORECASE)
VALID_COLUMN_NAME = re.compile(r'^[a-z][a-z0-9_]*$', re.IGNORECASE)
RESERVED_KEYWORDS = {
    "ORDER", "GROUP", "KEY", "VALUE", "TABLE", "DATABASE", "INDEX",
    "SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "CREATE",
    "DROP", "ALTER", "STATUS", "LEVEL", "NAME", "TYPE", "NUMBER",
    "DATE", "TIME", "TIMESTAMP", "DEFAULT", "PRIMARY"
}

# ── 不推荐的大字段类型 ────────────────────────────
LARGE_FIELD_TYPES = {"TEXT", "MEDIUMTEXT", "LONGTEXT", "BLOB", "MEDIUMBLOB", "LONGBLOB"}

# ── 常用索引字段模式（启发式） ────────────────────
COMMON_INDEX_PATTERNS = [
    r'^(created_at|updated_at|deleted_at)$',
    r'^(create_time|update_time|delete_time)$',
    r'^(.*_id)$',
    r'^(status|type|state|is_deleted|is_active|deleted)$',
]


from typing import Optional


def inspect_table_schema(database: str) -> dict:
    """
    扫描指定库中全部表，自动检测反模式问题

    检测规则：
    1. 无主键表
    2. 表名/列名不符合 snake_case 命名规范
    3. 列名使用 SQL 保留关键字
    4. 字段类型不合理（如 TEXT 滥用）
    5. NULL 列缺乏默认值
    6. 缺失常用索引（created_at, status 等）
    7. 冗余索引（前缀重复的复合索引）
    8. 自增主键非 BIGINT
    9. VARCHAR 长度不合理

    Args:
        database: 待巡检的数据库名

    Returns:
        {
            "success": bool,
            "database": str,
            "total_tables": int,
            "issues": [
                {
                    "table": str,
                    "severity": "critical"|"warning"|"info",
                    "category": str,
                    "detail": str,
                    "suggestion": str,
                }
            ]
        }
    """
    result = {
        "success": False,
        "database": database,
        "total_tables": 0,
        "issues": [],
    }

    try:
        conn = pool_manager.get_connection(database)
    except pymysql.MySQLError as e:
        return {"success": False, "error": f"数据库连接失败: {e}", "issues": []}

    try:
        with conn.cursor() as cursor:
            # 获取所有基础表
            cursor.execute(
                "SELECT TABLE_NAME, ENGINE, TABLE_ROWS, TABLE_COMMENT, CREATE_TIME "
                "FROM information_schema.TABLES "
                "WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE' "
                "ORDER BY TABLE_NAME",
                (database,),
            )
            tables = cursor.fetchall()
            result["total_tables"] = len(tables)

            table_names = [t["TABLE_NAME"] for t in tables]
            all_columns = {}
            all_indexes = {}

            # 批量获取列信息
            for tbl_name in table_names:
                cursor.execute(
                    "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, "
                    "COLUMN_KEY, EXTRA, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, "
                    "NUMERIC_PRECISION, ORDINAL_POSITION "
                    "FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                    "ORDER BY ORDINAL_POSITION",
                    (database, tbl_name),
                )
                all_columns[tbl_name] = cursor.fetchall()

                cursor.execute(
                    "SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE, SEQ_IN_INDEX "
                    "FROM information_schema.STATISTICS "
                    "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                    "ORDER BY INDEX_NAME, SEQ_IN_INDEX",
                    (database, tbl_name),
                )
                all_indexes[tbl_name] = cursor.fetchall()

            # ── 逐表逐规则检测 ─────────────────
            for tbl in tables:
                table_name = tbl["TABLE_NAME"]
                columns = all_columns.get(table_name, [])
                indexes = all_indexes.get(table_name, [])

                _check_no_primary_key(result, table_name, columns)
                _check_table_naming(result, table_name)
                _check_column_naming(result, table_name, columns)
                _check_column_types(result, table_name, columns)
                _check_nullable_defaults(result, table_name, columns)
                _check_missing_indexes(result, table_name, columns, indexes)
                _check_redundant_indexes(result, table_name, indexes)
                _check_auto_increment_type(result, table_name, columns)
                _check_varchar_length(result, table_name, columns)

        result["success"] = True

        severity_order = {"critical": 0, "warning": 1, "info": 2}
        result["issues"].sort(key=lambda x: severity_order.get(x["severity"], 99))

    except pymysql.MySQLError as e:
        result["success"] = False
        result["error"] = f"巡检失败: {e}"
    finally:
        conn.close()

    return result


def _add_issue(result, table, severity, category, detail, suggestion):
    result["issues"].append({
        "table": table, "severity": severity,
        "category": category, "detail": detail, "suggestion": suggestion,
    })


def _check_no_primary_key(result, table_name, columns):
    has_pk = any(c["COLUMN_KEY"] == "PRI" for c in columns)
    if not has_pk:
        _add_issue(result, table_name, "critical", "无主键",
                   "表缺少主键定义", "建议添加自增 BIGINT 主键")


def _check_table_naming(result, table_name):
    if not VALID_TABLE_NAME.match(table_name):
        _add_issue(result, table_name, "warning", "表名不规范",
                   f"表名 '{table_name}' 不符合 snake_case 命名规范",
                   "建议改为全小写 + 下划线格式")
    if table_name.upper() in RESERVED_KEYWORDS:
        _add_issue(result, table_name, "warning", "表名冲突",
                   f"表名 '{table_name}' 是 SQL 保留关键字",
                   "建议重命名避免与保留字冲突")


def _check_column_naming(result, table_name, columns):
    for col in columns:
        col_name = col["COLUMN_NAME"]
        if not VALID_COLUMN_NAME.match(col_name):
            _add_issue(result, table_name, "warning", "列名不规范",
                       f"列 '{col_name}' 不符合 snake_case 命名规范",
                       "建议改为全小写 + 下划线格式")
        if col_name.upper() in RESERVED_KEYWORDS:
            _add_issue(result, table_name, "warning", "列名冲突",
                       f"列 '{col_name}' 是 SQL 保留关键字，查询时需要加反引号",
                       f"建议将列名改为非保留字")


def _check_column_types(result, table_name, columns):
    text_cols = []
    varchar_with_excessive_len = []
    for col in columns:
        dt = col["DATA_TYPE"].upper() if col["DATA_TYPE"] else ""
        if dt in LARGE_FIELD_TYPES:
            text_cols.append(col["COLUMN_NAME"])
        if dt == "VARCHAR":
            max_len = col.get("CHARACTER_MAXIMUM_LENGTH", 0)
            if max_len and max_len > 1000:
                varchar_with_excessive_len.append(f'{col["COLUMN_NAME"]}({max_len})')

    if len(text_cols) > 3:
        _add_issue(result, table_name, "warning", "大字段滥用",
                   f"表中有 {len(text_cols)} 个 TEXT/BLOB 列: {text_cols}",
                   "大量大字段影响行存储效率，评估是否可改用 VARCHAR")
    if varchar_with_excessive_len:
        _add_issue(result, table_name, "info", "VARCHAR 过长",
                   f"VARCHAR 列长度 >1000: {varchar_with_excessive_len}",
                   "过长的 VARCHAR 影响索引效率，考虑是否实际需要")


def _check_nullable_defaults(result, table_name, columns):
    null_no_default = []
    for col in columns:
        if col["IS_NULLABLE"] == "YES" and col["COLUMN_DEFAULT"] is None and col["COLUMN_KEY"] != "PRI":
            null_no_default.append(col["COLUMN_NAME"])
    if len(null_no_default) > 5:
        _add_issue(result, table_name, "info", "NULL 列默认值",
                   f"超过 {len(null_no_default)} 个 NULL 列无默认值: {null_no_default[:5]}...",
                   "设置合理的默认值可减少插入时的疏忽错误")


def _check_missing_indexes(result, table_name, columns, indexes):
    indexed_cols = set()
    for idx in indexes:
        indexed_cols.add(idx["COLUMN_NAME"])

    col_names = [c["COLUMN_NAME"] for c in columns]

    missing = []
    for col_name in col_names:
        if col_name in indexed_cols:
            continue
        for pattern in COMMON_INDEX_PATTERNS:
            if re.match(pattern, col_name, re.IGNORECASE):
                missing.append(col_name)
                break

    if missing:
        _add_issue(result, table_name, "warning", "缺失常用索引",
                   f"以下列可能缺少索引: {missing}",
                   "建议为高频查询条件、排序、关联字段添加索引")


def _check_redundant_indexes(result, table_name, indexes):
    idx_map = {}
    for idx in indexes:
        name = idx["INDEX_NAME"]
        if name not in idx_map:
            idx_map[name] = []
        idx_map[name].append(idx["COLUMN_NAME"])

    idx_items = list(idx_map.items())
    for i in range(len(idx_items)):
        for j in range(i + 1, len(idx_items)):
            cols_a = idx_items[i][1]
            cols_b = idx_items[j][1]
            if len(cols_a) != len(cols_b) and (
                cols_a == cols_b[:len(cols_a)] or cols_b == cols_a[:len(cols_b)]
            ):
                _add_issue(result, table_name, "info", "可能冗余索引",
                           f"索引 '{idx_items[i][0]}' ({', '.join(cols_a)}) 与 "
                           f"'{idx_items[j][0]}' ({', '.join(cols_b)}) 前缀重合",
                           "较短的索引可能被较长索引覆盖，考虑删除冗余索引")


def _check_auto_increment_type(result, table_name, columns):
    for col in columns:
        if col["EXTRA"] and "auto_increment" in col["EXTRA"].lower():
            dt = col["DATA_TYPE"].upper() if col["DATA_TYPE"] else ""
            if dt == "INT":
                _add_issue(result, table_name, "warning", "自增主键类型",
                           f"自增主键 '{col['COLUMN_NAME']}' 使用 INT 类型，上限约 21 亿",
                           "建议使用 BIGINT UNSIGNED 作为自增主键，上限约 184 亿亿")


def _check_varchar_length(result, table_name, columns):
    for col in columns:
        dt = col["DATA_TYPE"].upper() if col["DATA_TYPE"] else ""
        if dt == "VARCHAR":
            max_len = col.get("CHARACTER_MAXIMUM_LENGTH", 0)
            if max_len and max_len == 1:
                _add_issue(result, table_name, "info", "VARCHAR 长度",
                           f"列 '{col['COLUMN_NAME']}' 为 VARCHAR(1)，是否为布尔标志？",
                           "若为布尔值建议用 TINYINT(1) 或 BOOLEAN")


# ── Tool Definition Schema ──────────────────────────
TOOL_INSPECT_DEFINITION = {
    "type": "function",
    "function": {
        "name": "inspect_table_schema",
        "description": (
            "扫描指定库中全部表的结构，自动检测反模式问题，包括：无主键、"
            "命名不规范、类型不合理、冗余字段、缺失常用索引、大字段滥用、"
            "自增主键类型过小、VARCHAR 长度不合理等，并给出整改建议"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "database": {
                    "type": "string",
                    "description": "待巡检的数据库名",
                },
            },
            "required": ["database"],
        },
    },
}