"""认证数据库 —— MySQL 存储用户、角色、操作审计日志（从 SQLite 迁移到 MySQL）"""
import os
import pymysql
from datetime import datetime, timezone
from contextlib import contextmanager
from config import settings

AUTH_DB = getattr(settings, 'auth_mysql_database', 'agent_auth')

# ── MySQL 兼容的建表 SQL ──────────────────────────
SCHEMA_SQL_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role        VARCHAR(20)  NOT NULL DEFAULT 'reader',
    display_name VARCHAR(50)  DEFAULT '',
    created_at  DATETIME     NOT NULL,
    last_login  DATETIME,
    is_active   TINYINT      NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

SCHEMA_SQL_AUDIT = """
CREATE TABLE IF NOT EXISTS audit_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL,
    role        VARCHAR(20)  NOT NULL,
    action      VARCHAR(50)  NOT NULL,
    target      VARCHAR(255) DEFAULT '',
    detail      TEXT,
    result      VARCHAR(20)  DEFAULT '',
    backup_path VARCHAR(500) DEFAULT '',
    ip_address  VARCHAR(45)  DEFAULT '',
    session_id  VARCHAR(32)  DEFAULT '',
    round_number INT         DEFAULT 0,
    token_consumed INT       DEFAULT 0,
    created_at  DATETIME     NOT NULL,
    INDEX idx_audit_username (username),
    INDEX idx_audit_action  (action),
    INDEX idx_audit_created  (created_at),
    INDEX idx_audit_session  (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

SCHEMA_SQL_SESSIONS = """
CREATE TABLE IF NOT EXISTS agent_sessions (
    id VARCHAR(32) PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    messages_json LONGTEXT NOT NULL,
    database_name VARCHAR(100),
    tool_call_count INT DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_session_user (username),
    INDEX idx_session_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


def _get_auth_conn() -> pymysql.Connection:
    """获取认证数据库连接（复用连接池）"""
    from security.connection_pool import pool_manager
    return pool_manager.get_connection(AUTH_DB)


def init_auth_db():
    """初始化认证数据库：建库 + 建表 + 创建默认管理员"""
    from security.connection_pool import pool_manager

    # 1. 确保 agent_auth 数据库存在
    try:
        conn = pool_manager.get_connection(None)  # 无数据库的服务器级连接
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{AUTH_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()
    except Exception as e:
        print(f"[Auth] 创建认证数据库失败: {e}")
        return

    # 2. 创建表
    conn = _get_auth_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL_USERS)
            cur.execute(SCHEMA_SQL_AUDIT)
            cur.execute(SCHEMA_SQL_SESSIONS)
        conn.commit()
    except Exception as e:
        print(f"[Auth] 创建认证表失败: {e}")
        conn.close()
        return

    # 3. 创建默认用户（admin / reader）
    import bcrypt
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", ("admin",))
            if not cur.fetchone():
                now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                pwd = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
                cur.execute(
                    "INSERT INTO users (username, password_hash, role, display_name, created_at) VALUES (%s, %s, %s, %s, %s)",
                    ("admin", pwd, "admin", "系统管理员", now),
                )
                cur.execute(
                    "INSERT INTO users (username, password_hash, role, display_name, created_at) VALUES (%s, %s, %s, %s, %s)",
                    ("reader", bcrypt.hashpw(b"reader123", bcrypt.gensalt()).decode(), "reader", "只读用户", now),
                )
                conn.commit()
                print("[Auth] 默认用户已创建: admin (管理员) / reader (只读用户)")
    except Exception as e:
        print(f"[Auth] 默认用户创建失败: {e}")
    finally:
        conn.close()


@contextmanager
def get_db():
    """获取认证数据库连接（上下文管理器）"""
    conn = _get_auth_conn()
    try:
        yield conn
    finally:
        conn.close()


def get_user_by_username(username: str) -> dict | None:
    """根据用户名查询用户"""
    conn = _get_auth_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, password_hash, role, display_name, is_active, created_at, last_login FROM users WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()


def update_last_login(username: str):
    """更新最后登录时间"""
    conn = _get_auth_conn()
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET last_login = %s WHERE username = %s", (now, username))
        conn.commit()
    finally:
        conn.close()


def create_user(username: str, password_hash: str, role: str, display_name: str = "") -> bool:
    """创建新用户"""
    conn = _get_auth_conn()
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password_hash, role, display_name, created_at) VALUES (%s, %s, %s, %s, %s)",
                (username, password_hash, role, display_name, now),
            )
        conn.commit()
        return True
    except pymysql.IntegrityError:
        return False
    finally:
        conn.close()


def list_users() -> list[dict]:
    """列出所有用户（不含密码哈希）"""
    conn = _get_auth_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, username, role, display_name, is_active, created_at, last_login FROM users ORDER BY id")
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_audit_log(
    username: str,
    role: str,
    action: str,
    target: str = "",
    detail: str = "",
    result: str = "SUCCESS",
    backup_path: str = "",
    ip_address: str = "",
):
    """写入审计日志"""
    conn = _get_auth_conn()
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO audit_log (username, role, action, target, detail, result, backup_path, ip_address, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (username, role, action, target, detail[:2000] if detail else "", result, backup_path, ip_address, now),
            )
        conn.commit()
    finally:
        conn.close()


def update_user_status(username: str, is_active: bool) -> bool:
    """启用/禁用用户"""
    conn = _get_auth_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET is_active = %s WHERE username = %s",
                (1 if is_active else 0, username),
            )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def update_user_role(username: str, role: str) -> bool:
    """修改用户角色"""
    conn = _get_auth_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET role = %s WHERE username = %s",
                (role, username),
            )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def update_user_password(username: str, password_hash: str) -> bool:
    """重置用户密码"""
    conn = _get_auth_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE username = %s",
                (password_hash, username),
            )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def query_audit_logs(
    username: str = None,
    action: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    """查询审计日志（支持筛选），返回 (日志列表, 总数)"""
    conn = _get_auth_conn()
    conditions = []
    params = []

    if username:
        conditions.append("username = %s")
        params.append(username)
    if action:
        conditions.append("action = %s")
        params.append(action)
    if start_date:
        conditions.append("created_at >= %s")
        params.append(start_date + " 00:00:00")
    if end_date:
        conditions.append("created_at <= %s")
        params.append(end_date + " 23:59:59")

    where = " WHERE " + " AND ".join(conditions) if conditions else ""

    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) as cnt FROM audit_log {where}", tuple(params))
            total = cur.fetchone()["cnt"]

            cur.execute(
                f"SELECT * FROM audit_log {where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
                tuple(params + [limit, offset]),
            )
            rows = cur.fetchall()

        return [dict(r) for r in rows], total
    finally:
        conn.close()