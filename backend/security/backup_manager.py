"""高风险操作备份管理器 —— CREATE/DROP/ALTER 前自动备份（安全增强版）"""
import os
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pymysql

from config import settings
from security.connection_pool import pool_manager

BACKUP_DIR = Path(__file__).parent.parent.parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


def backup_before_dangerous(
    operation: str, database: str, target: str, username: str,
) -> str | None:
    """在执行危险操作前创建备份，返回备份文件路径或 None"""
    if operation in ("CREATE_DATABASE", "CREATE_TABLE", "INSERT_INTO"):
        return None

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_target = target.replace("`", "").replace("'", "").replace(";", "")
    filename = f"{operation}_{database}_{safe_target}_{username}_{timestamp}.sql"
    backup_path = BACKUP_DIR / filename

    try:
        if operation == "DROP_DATABASE":
            _backup_database_mysqldump(database, str(backup_path))
        elif operation in ("DROP_TABLE", "TRUNCATE_TABLE", "ALTER_TABLE"):
            _backup_table(database, target, str(backup_path))
        else:
            return None

        meta_path = backup_path.with_suffix(".meta.json")
        meta = {
            "operation": operation, "database": database, "target": target,
            "username": username, "timestamp": timestamp, "backup_file": filename,
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return str(backup_path)
    except Exception as e:
        print(f"[Backup] 备份失败: {e}")
        return None


def _backup_database_mysqldump(database: str, output_path: str):
    """使用 mysqldump 备份整个数据库（安全方式：临时配置文件传递密码）"""
    # 创建临时配置文件避免密码暴露在进程列表
    fd, cnf_path = tempfile.mkstemp(suffix=".cnf")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("[client]\n")
            f.write(f"host={settings.mysql_host}\n")
            f.write(f"port={settings.mysql_port}\n")
            f.write(f"user={settings.mysql_user}\n")
            f.write(f'password="{settings.mysql_password}"\n')

        import subprocess

        # 使用列表参数形式避免 shell 注入
        cmd = [
            "mysqldump",
            f"--defaults-extra-file={cnf_path}",
            "--single-transaction",
            "--routines",
            "--triggers",
            "--add-drop-database",
            "--databases",
            database,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0 and result.stdout.strip():
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            return

    except FileNotFoundError:
        print("[Backup] mysqldump 未找到，回退到手动备份")
    except Exception as e_:
        print(f"[Backup] mysqldump 失败 ({e_})，回退到手动备份")
    finally:
        try:
            os.unlink(cnf_path)
        except OSError:
            pass

    # 回退方案：使用连接池手动备份
    _backup_database_manual(database, output_path)


def _backup_database_manual(database: str, output_path: str):
    """手动备份整个数据库（回退方案，不使用 mysqldump）"""
    conn = pool_manager.get_connection(database)
    try:
        with conn.cursor() as cursor:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"-- Backup of database `{database}`\n")
                f.write(f"-- Generated at {datetime.now(timezone.utc).isoformat()}\n\n")

                cursor.execute("SHOW TABLES")
                tables = [list(row.values())[0] for row in cursor.fetchall()]

                for table in tables:
                    cursor.execute(f"SHOW CREATE TABLE `{table}`")
                    create_row = cursor.fetchone()
                    if create_row:
                        f.write(f"-- Table: {table}\n")
                        f.write(f"{list(create_row.values())[1]};\n\n")

                    cursor.execute(f"SELECT * FROM `{table}` LIMIT 10000")
                    columns = (
                        [desc[0] for desc in cursor.description]
                        if cursor.description
                        else []
                    )
                    rows = cursor.fetchall()
                    if rows:
                        cols_fmt = ", ".join(f"`{c}`" for c in columns)
                        f.write(f"-- Data for {table} ({len(rows)} rows)\n")
                        for row in rows:
                            vals = []
                            for c in columns:
                                v = row.get(c)
                                if v is None:
                                    vals.append("NULL")
                                elif isinstance(v, (int, float)):
                                    vals.append(str(v))
                                else:
                                    escaped = (
                                        str(v)
                                        .replace("\\", "\\\\")
                                        .replace("'", "\\'")
                                    )
                                    vals.append(f"'{escaped}'")
                            f.write(
                                f"INSERT INTO `{table}` ({cols_fmt}) "
                                f"VALUES ({', '.join(vals)});\n"
                            )
                        f.write("\n")
    finally:
        conn.close()


def _backup_table(database: str, table: str, output_path: str):
    """备份单个表"""
    conn = pool_manager.get_connection(database)
    try:
        with conn.cursor() as cursor:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"-- Backup of `{database}`.`{table}`\n")
                f.write(f"-- Generated at {datetime.now(timezone.utc).isoformat()}\n\n")

                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_row = cursor.fetchone()
                if create_row:
                    f.write(list(create_row.values())[1] + ";\n\n")

                cursor.execute(f"SELECT * FROM `{table}` LIMIT 10000")
                columns = (
                    [desc[0] for desc in cursor.description]
                    if cursor.description
                    else []
                )
                rows = cursor.fetchall()
                if rows:
                    cols_fmt = ", ".join(f"`{c}`" for c in columns)
                    f.write(f"-- Data ({len(rows)} rows)\n")
                    for row in rows:
                        vals = []
                        for c in columns:
                            v = row.get(c)
                            if v is None:
                                vals.append("NULL")
                            elif isinstance(v, (int, float)):
                                vals.append(str(v))
                            else:
                                escaped = (
                                    str(v).replace("\\", "\\\\").replace("'", "\\'")
                                )
                                vals.append(f"'{escaped}'")
                        f.write(
                            f"INSERT INTO `{table}` ({cols_fmt}) "
                            f"VALUES ({', '.join(vals)});\n"
                        )
    finally:
        conn.close()


def list_backups(database: str = None, limit: int = 50) -> list[dict]:
    """列出备份文件列表"""
    backups = []
    for f in sorted(BACKUP_DIR.glob("*.sql"), reverse=True):
        if f.stat().st_size == 0:
            continue
        meta_file = f.with_suffix(".meta.json")
        meta = {}
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as mf:
                    meta = json.load(mf)
            except Exception:
                pass
        entry = {
            "filename": f.name,
            "size_bytes": f.stat().st_size,
            "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "operation": meta.get("operation", "UNKNOWN"),
            "database": meta.get("database", ""),
            "target": meta.get("target", ""),
            "username": meta.get("username", ""),
        }
        if database and entry["database"] != database:
            continue
        backups.append(entry)
        if len(backups) >= limit:
            break
    return backups


def restore_backup(filename: str, target_database: str = None) -> dict:
    """从备份文件恢复数据"""
    backup_file = BACKUP_DIR / filename
    if not backup_file.exists():
        return {"success": False, "message": "备份文件不存在"}

    meta_file = backup_file.with_suffix(".meta.json")
    meta = {}
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as mf:
                meta = json.load(mf)
        except Exception:
            pass

    db_name = target_database or meta.get("database", "")
    if not db_name:
        return {"success": False, "message": "无法确定目标数据库"}

    conn = pool_manager.get_connection(db_name)
    try:
        with open(backup_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        statements = [
            s.strip()
            for s in sql_content.split(";")
            if s.strip() and not s.strip().startswith("--")
        ]

        executed = 0
        with conn.cursor() as cursor:
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                    executed += 1
                except pymysql.MySQLError:
                    continue

        conn.commit()
        return {
            "success": True,
            "message": f"恢复完成，成功执行 {executed}/{len(statements)} 条语句",
            "executed": executed,
            "total": len(statements),
        }
    except Exception as e:
        return {"success": False, "message": f"恢复失败: {e}"}
    finally:
        conn.close()