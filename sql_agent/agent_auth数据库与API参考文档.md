# agent_auth 认证数据库 — 备份文档 & API 参考

> 此文档备份了 `agent_auth` 数据库的完整表结构、核心函数清单和 21 个 API 端点说明。  
> 数据库代码位于 `backend/auth/database.py`，路由位于 `backend/api/routes.py`。

---

## 一、数据库结构

### 1.1 数据库信息

| 属性 | 值 |
|------|-----|
| 数据库名 | `agent_auth`（通过 `AUTH_MYSQL_DATABASE` 环境变量配置） |
| 引擎 | MySQL 8.0+ (InnoDB) |
| 字符集 | utf8mb4 / utf8mb4_unicode_ci |
| 连接方式 | 复用 `security.connection_pool.pool_manager` |

### 1.2 表结构

#### 表 1：`users` — 用户表

```sql
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)   UNIQUE NOT NULL,
    password_hash VARCHAR(255)  NOT NULL,
    role          VARCHAR(20)   NOT NULL DEFAULT 'reader',  -- 'admin' 或 'reader'
    display_name  VARCHAR(50)   DEFAULT '',
    created_at    DATETIME      NOT NULL,
    last_login    DATETIME,
    is_active     TINYINT       NOT NULL DEFAULT 1           -- 1=启用, 0=禁用
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**默认用户**（自动创建）：
| 用户名 | 密码(BCrypt) | 角色 | 说明 |
|--------|-------------|------|------|
| `admin` | bcrypt.hashpw(b"admin123") | admin | 系统管理员 |
| `reader` | bcrypt.hashpw(b"reader123") | reader | 只读用户 |

#### 表 2：`audit_log` — 审计日志表

```sql
CREATE TABLE IF NOT EXISTS audit_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  NOT NULL,
    role        VARCHAR(20)  NOT NULL,
    action      VARCHAR(50)  NOT NULL,
    target      VARCHAR(255) DEFAULT '',
    detail      TEXT,
    result      VARCHAR(20)  DEFAULT '',      -- 'SUCCESS' / 'FAILED'
    backup_path VARCHAR(500) DEFAULT '',
    ip_address  VARCHAR(45)  DEFAULT '',
    created_at  DATETIME     NOT NULL,
    INDEX idx_audit_username (username),
    INDEX idx_audit_action  (action),
    INDEX idx_audit_created  (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 二、核心函数清单（`backend/auth/database.py`）

| 函数 | 说明 | 参数 |
|------|------|------|
| `init_auth_db()` | 初始化：建库 + 建表 + 创建默认 admin/reader | 无 |
| `get_user_by_username(username)` | 按用户名查询用户 | `username: str` → dict or None |
| `update_last_login(username)` | 更新最后登录时间 | `username: str` |
| `create_user(username, password_hash, role, display_name)` | 创建用户 | `username, password_hash, role, display_name` → bool |
| `list_users()` | 列出所有用户（不含密码哈希） | 无 → list[dict] |
| `add_audit_log(username, role, action, ...)` | 写入审计日志 | 详见代码 |
| `query_audit_logs(username, action, start_date, end_date, limit, offset)` | 查询审计日志（支持日期筛选） | → (logs, total) |
| `update_user_status(username, is_active)` | 启用/禁用用户 | `username, is_active` → bool |
| `update_user_role(username, role)` | 修改用户角色 | `username, role` → bool |
| `update_user_password(username, password_hash)` | 重置用户密码 | `username, password_hash` → bool |

**初始化流程**（`init_auth_db()`）：
1. 连接 MySQL 服务器（无指定数据库）
2. 执行 `CREATE DATABASE IF NOT EXISTS agent_auth`
3. 连接 `agent_auth` 数据库
4. 执行 `CREATE TABLE IF NOT EXISTS users`
5. 执行 `CREATE TABLE IF NOT EXISTS audit_log`
6. 检查 admin 用户是否存在，不存在则插入 admin + reader

---

## 三、API 接口文档（共 21 个端点，`/api` 前缀）

### 3.1 认证接口（无需登录）

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | `/auth/login` | 用户登录 | `{"username":"admin","password":"admin123"}` | `{"access_token":"...","username":"admin","role":"admin","display_name":"系统管理员"}` |
| POST | `/auth/register` | 用户注册 | `{"username":"user1","password":"pass123","display_name":"可选"}` | 同上 |
| GET | `/auth/me` | 获取当前用户信息 | 无（Bearer Token） | `{"username":"...","role":"...","display_name":"..."}` |

### 3.2 管理员用户管理（需要 admin 角色）

| 方法 | 路径 | 说明 | 请求体 |
|------|------|------|--------|
| GET | `/admin/users` | 列出所有用户 | — |
| POST | `/admin/users/create` | 创建用户（可指定角色） | `{"username":"u","password":"p","role":"admin\\|reader","display_name":"可选"}` |
| POST | `/admin/users/status` | 启用/禁用用户 | `{"username":"u","is_active":false}` |
| POST | `/admin/users/role` | 修改用户角色 | `{"username":"u","role":"admin\\|reader"}` |
| POST | `/admin/users/password` | 重置密码 | `{"username":"u","new_password":"newpwd"}` |

### 3.3 管理员 DDL/DML 执行（需要 admin/write 角色）

| 方法 | 路径 | 说明 | 请求体 |
|------|------|------|--------|
| POST | `/admin/execute` | 执行 DDL/DML（自动备份） | `{"sql":"DROP TABLE x","database":"test_db"}` |

### 3.4 备份管理（需要 admin 角色）

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/admin/backups` | 列出备份文件 | `?database=test_db&limit=50` |
| POST | `/admin/backups/restore` | 恢复备份 | `{"filename":"xxx.sql","target_database":"test_db"}` |

### 3.5 审计日志

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/audit/logs` | 查询审计日志 | `?username=u&action=EXECUTE_SQL&start_date=2026-01-01&end_date=2026-06-30&limit=50&offset=0` |
| GET | `/audit/stats` | 审计统计概览 | `?days=7` |
| GET | `/audit/export` | 导出审计日志 CSV | `?start_date=2026-01-01&end_date=2026-06-30&action=EXECUTE_SQL` |

### 3.6 AI 对话与工具

| 方法 | 路径 | 说明 | 请求体 |
|------|------|------|--------|
| POST | `/chat/stream` | SSE 流式对话 | `{"session_id":"可选","message":"帮我查...","database":"可选"}` |
| POST | `/session/create` | 创建新会话 | `{"database":"可选"}` |
| GET | `/session/{id}/history` | 获取会话历史 | — |
| DELETE | `/session/{id}` | 删除会话 | — |

### 3.7 数据库查询工具（所有登录用户）

| 方法 | 路径 | 说明 | 请求体 |
|------|------|------|--------|
| GET | `/databases` | 列出所有数据库 | — |
| POST | `/metadata` | 获取表元数据 | `{"database":"test_db","table":"可选"}` |
| GET | `/metadata` | 同上（GET兼容） | `?database=test_db&table=users` |
| POST | `/execute` | 执行只读 SQL | `{"database":"test_db","sql":"SELECT * FROM users LIMIT 10","limit":100}` |
| POST | `/explain` | EXPLAIN 分析 | `{"database":"test_db","sql":"SELECT * FROM users"}` |
| GET | `/inspect` | 表结构巡检 | `?database=test_db` |
| POST | `/generate-data` | 生成测试数据 | `{"database":"test_db","table":"users","scenario":"通用数据","row_count":50}` |
| POST | `/execute-test-data` | 执行测试数据 | `{"database":"test_db","insert_statements":["INSERT..."]}` |

### 3.8 数据库对象浏览器

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/objects` | 获取表/视图树 | `?database=test_db` |
| GET | `/objects/{db}/{table}/columns` | 获取列详情 | — |
| GET | `/objects/{db}/{table}/indexes` | 获取索引信息 | — |

### 3.9 数据导出

| 方法 | 路径 | 说明 | 请求体 |
|------|------|------|--------|
| POST | `/export/csv` | 导出 CSV | `{"database":"test_db","sql":"SELECT ...","limit":500}` |
| POST | `/export/json` | 导出 JSON | 同上 |

### 3.10 知识库管理

| 方法 | 路径 | 说明 | 参数/请求体 |
|------|------|------|------------|
| POST | `/knowledge/init` | 初始化知识库 | `?force=false` |
| GET | `/knowledge/search` | 搜索知识 | `?query=索引优化&top_k=3` |
| GET | `/knowledge/list` | 列出所有知识 | — |
| POST | `/knowledge/add` | 添加知识（管理员） | `{"content":"...","metadata":{"category":"SQL优化","title":"xxx"}}` |
| DELETE | `/knowledge/{id}` | 删除知识（管理员） | — |

### 3.11 系统信息与健康检查

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/system/info` | 系统信息 | admin |
| GET | `/system/config` | 运行时配置 | admin |
| GET | `/health` | 健康检查（MySQL + ChromaDB） | 公开 |

---

## 四、默认管理员创建逻辑（代码备份）

```python
# 在 init_auth_db() 中，第 75-95 行
import bcrypt
try:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", ("admin",))
        if not cur.fetchone():
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            pwd = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
            cur.execute(
                "INSERT INTO users (username, password_hash, role, display_name, created_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("admin", pwd, "admin", "系统管理员", now),
            )
            cur.execute(
                "INSERT INTO users (username, password_hash, role, display_name, created_at) "
                "VALUES (%s, %s, %s, %s, %s)",
                ("reader", bcrypt.hashpw(b"reader123", bcrypt.gensalt()).decode(), "reader", "只读用户", now),
            )
            conn.commit()
except Exception as e:
    print(f"[Auth] 默认用户创建失败: {e}")
```

---

## 五、数据库迁移/重建步骤

如果 `agent_auth` 数据库丢失或需要重建：

```bash
# 1. 连接 MySQL
mysql -u root -p

# 2. 手动创建数据库和表（或直接启动后端自动创建）
CREATE DATABASE IF NOT EXISTS agent_auth CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 3. 重启后端，自动完成 init_auth_db()
cd backend && python main.py