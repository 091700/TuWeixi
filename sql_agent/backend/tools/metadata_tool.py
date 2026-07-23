"""工具1: get_table_metadata —— 获取数据库/表的完整元数据"""
import time
import pymysql
from typing import Optional
from config import settings
from security.connection_pool import pool_manager


# ── 简易内存缓存 ───────────────────────────────────
_metadata_cache: dict = {}
_cache_timestamps: dict = {}


def get_table_metadata(database: str, table: Optional[str] = None) -> dict:
    """
    获取指定数据库/表的完整元数据信息

    Args:
        database: 目标数据库名
        table: 目标表名，不传则返回该库全部表

    Returns:
        {
            "success": bool,
            "database": str,
            "tables": [
                {
                    "table_name": "...",
                    "engine": "...",
                    "row_count_approx": ...,
                    "create_time": "...",
                    "comment": "...",
                    "columns": [
                        {
                            "name": "...",
                            "type": "...",
                            "nullable": bool,
                            "default": "...",
                            "key": "PRI"/"MUL"/"UNI"/"",
                            "extra": "...",
                            "comment": "..."
                        }
                    ],
                    "indexes": [
                        {"name": "...", "columns": [...], "unique": bool, "type": "..."}
                    ],
                    "foreign_keys": [
                        {"name": "...", "column": "...", "ref_table": "...", "ref_column": "..."}
                    ]
                }
            ]
        }
    """
    cache_key = f"{database}:{table or '__all__'}"
    now = time.time()

    # 检查缓存
    if cache_key in _metadata_cache:
        if now - _cache_timestamps.get(cache_key, 0) < settings.metadata_cache_ttl:
            return _metadata_cache[cache_key]

    result = {"success": False, "database": database, "tables": []}
    conn = None
    cursor = None

    try:
        conn = pool_manager.get_connection(database)
        cursor = conn.cursor()
    except pymysql.MySQLError as e:
        return {"success": False, "error": f"数据库连接失败 ({database}): {e}"}

    try:
        # 1. 获取表列表
        if table:
            table_list_sql = (
                "SELECT TABLE_NAME, ENGINE, TABLE_ROWS, CREATE_TIME, TABLE_COMMENT "
                "FROM information_schema.TABLES "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s"
            )
            cursor.execute(table_list_sql, (database, table))
        else:
            table_list_sql = (
                "SELECT TABLE_NAME, ENGINE, TABLE_ROWS, CREATE_TIME, TABLE_COMMENT "
                "FROM information_schema.TABLES "
                "WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE' "
                "ORDER BY TABLE_NAME"
            )
            cursor.execute(table_list_sql, (database,))

        tables_info = cursor.fetchall()

        if not tables_info:
            result["success"] = True
            result["tables"] = []
            _metadata_cache[cache_key] = result
            _cache_timestamps[cache_key] = now
            return result

        tables_schema = []

        for tbl in tables_info:
            table_name = tbl["TABLE_NAME"]

            # 2. 获取列信息
            cursor.execute(
                "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, "
                "COLUMN_KEY, EXTRA, COLUMN_COMMENT, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH "
                "FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                "ORDER BY ORDINAL_POSITION",
                (database, table_name),
            )
            columns_raw = cursor.fetchall()

            columns = []
            for col in columns_raw:
                columns.append(
                    {
                        "name": col["COLUMN_NAME"],
                        "type": col["COLUMN_TYPE"],
                        "data_type": col["DATA_TYPE"],
                        "nullable": col["IS_NULLABLE"] == "YES",
                        "default": str(col["COLUMN_DEFAULT"]) if col["COLUMN_DEFAULT"] is not None else None,
                        "key": col["COLUMN_KEY"],
                        "extra": col["EXTRA"],
                        "comment": col["COLUMN_COMMENT"] or "",
                        "max_length": col["CHARACTER_MAXIMUM_LENGTH"],
                    }
                )

            # 3. 获取索引信息
            cursor.execute(
                "SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE, INDEX_TYPE, SEQ_IN_INDEX "
                "FROM information_schema.STATISTICS "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                "ORDER BY INDEX_NAME, SEQ_IN_INDEX",
                (database, table_name),
            )
            indexes_raw = cursor.fetchall()

            # 聚合索引列
            indexes_map: dict = {}
            for idx in indexes_raw:
                idx_name = idx["INDEX_NAME"]
                if idx_name not in indexes_map:
                    indexes_map[idx_name] = {
                        "name": idx_name,
                        "columns": [],
                        "unique": idx["NON_UNIQUE"] == 0,
                        "type": idx["INDEX_TYPE"],
                    }
                indexes_map[idx_name]["columns"].append(idx["COLUMN_NAME"])

            indexes = list(indexes_map.values())

            # 4. 获取外键信息
            cursor.execute(
                "SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, "
                "REFERENCED_COLUMN_NAME "
                "FROM information_schema.KEY_COLUMN_USAGE "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
                "AND REFERENCED_TABLE_NAME IS NOT NULL",
                (database, table_name),
            )
            fks_raw = cursor.fetchall()

            foreign_keys = []
            for fk in fks_raw:
                foreign_keys.append(
                    {
                        "name": fk["CONSTRAINT_NAME"],
                        "column": fk["COLUMN_NAME"],
                        "ref_table": fk["REFERENCED_TABLE_NAME"],
                        "ref_column": fk["REFERENCED_COLUMN_NAME"],
                    }
                )

            tables_schema.append(
                {
                    "table_name": table_name,
                    "engine": tbl["ENGINE"],
                    "row_count_approx": tbl["TABLE_ROWS"] or 0,
                    "create_time": str(tbl["CREATE_TIME"]) if tbl["CREATE_TIME"] else None,
                    "comment": tbl["TABLE_COMMENT"] or "",
                    "columns": columns,
                    "indexes": indexes,
                    "foreign_keys": foreign_keys,
                }
            )

        result["success"] = True
        result["tables"] = tables_schema

        # 更新缓存
        _metadata_cache[cache_key] = result
        _cache_timestamps[cache_key] = now

    except pymysql.MySQLError as e:
        result["success"] = False
        result["error"] = f"元数据查询失败: {e}"
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    return result


# ── Tool Definition Schema ──────────────────────────
TOOL_METADATA_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_table_metadata",
        "description": (
            "获取指定数据库/表的完整元数据信息，包括表结构、字段名、字段类型、"
            "是否可空、默认值、主键、外键、索引信息。在执行任何 SQL 查询之前，"
            "应先调用此工具了解表结构"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "database": {
                    "type": "string",
                    "description": "目标数据库名",
                },
                "table": {
                    "type": "string",
                    "description": "目标表名，不传则返回该库全部表的结构",
                },
            },
            "required": ["database"],
        },
    },
}