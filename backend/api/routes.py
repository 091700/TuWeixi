"""FastAPI 路由定义 —— 速率限制 + Body参数 + 审计 + 新增API"""
import json
import uuid
import csv
import io
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from agent.scheduler import chat_stream_generator, session_manager
from tools.metadata_tool import get_table_metadata
from tools.execute_sql_tool import execute_readonly_sql
from tools.explain_tool import explain_sql
from tools.schema_inspector import inspect_table_schema
from tools.test_data_generator import generate_test_data
from tools.admin_execute_tool import execute_admin_sql
from rag.knowledge_base import (
    init_knowledge_base,
    retrieve_knowledge,
    add_knowledge,
    remove_knowledge,
    list_all_knowledge,
)
from auth.security import (
    get_current_user,
    get_optional_user,
    require_admin,
    require_write,
    hash_password,
    verify_password,
    create_access_token,
)
from auth.database import (
    get_user_by_username,
    update_last_login,
    create_user,
    list_users,
    add_audit_log,
    query_audit_logs,
    update_user_status,
    update_user_role,
    update_user_password,
)
from security.backup_manager import list_backups, restore_backup
from security.connection_pool import pool_manager

logger = logging.getLogger("db_agent")

router = APIRouter(prefix="/api", tags=["Database AI Agent"])


# ══════════════════════════════════════════════════════
# 请求/响应模型
# ══════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    display_name: Optional[str] = Field(None, max_length=50)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    display_name: str


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="会话 ID")
    message: str = Field(..., min_length=1, max_length=4000)
    database: Optional[str] = Field(None)
    model: Optional[str] = Field(None, description="LLM 模型选择")


class AdminSQLRequest(BaseModel):
    sql: str = Field(..., min_length=1, max_length=5000)
    database: Optional[str] = Field(None)


class ExecuteRequest(BaseModel):
    database: str = Field(..., min_length=1)
    sql: str = Field(..., min_length=1, max_length=8000)
    limit: Optional[int] = Field(None, ge=1, le=settings.result_row_max)


class MetadataRequest(BaseModel):
    database: str = Field(..., min_length=1)
    table: Optional[str] = Field(None)


class ExplainRequest(BaseModel):
    database: str = Field(..., min_length=1)
    sql: str = Field(..., min_length=1, max_length=5000)


class GenerateDataRequest(BaseModel):
    database: str = Field(..., min_length=1)
    table: str = Field(..., min_length=1)
    scenario: str = Field("通用业务数据", max_length=200)
    row_count: int = Field(50, ge=1, le=500)


class ExecuteTestDataRequest(BaseModel):
    database: str = Field(..., min_length=1)
    insert_statements: list = Field(..., min_items=1, max_items=500)


class KnowledgeAddRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    metadata: Optional[dict] = Field(None)


class KnowledgeRemoveRequest(BaseModel):
    knowledge_id: str = Field(..., min_length=1)


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field("reader", pattern="^(admin|reader)$")
    display_name: Optional[str] = Field(None, max_length=50)


class UserStatusRequest(BaseModel):
    username: str = Field(..., min_length=1)
    is_active: bool


class UserRoleRequest(BaseModel):
    username: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(admin|reader)$")


class UserPasswordRequest(BaseModel):
    username: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=100)


class SessionCreateRequest(BaseModel):
    database: Optional[str] = Field(None)


class BackupRestoreRequest(BaseModel):
    filename: str = Field(..., min_length=1)
    target_database: Optional[str] = Field(None)


# ══════════════════════════════════════════════════════
# 认证路由（无需登录，带速率限制）
# ══════════════════════════════════════════════════════

@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, req: Request):
    """用户登录，返回 JWT 令牌"""
    user = get_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="用户已被禁用")
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    update_last_login(request.username)

    token = create_access_token(data={
        "sub": user["username"],
        "role": user["role"],
    })

    logger.info(f"用户登录: {request.username} (角色: {user['role']})")

    return TokenResponse(
        access_token=token,
        username=user["username"],
        role=user["role"],
        display_name=user.get("display_name") or user["username"],
    )


@router.post("/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest, req: Request):
    """用户注册（默认 reader 角色）"""
    existing = get_user_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    success = create_user(
        username=request.username,
        password_hash=hash_password(request.password),
        role="reader",
        display_name=request.display_name or request.username,
    )
    if not success:
        raise HTTPException(status_code=500, detail="注册失败")

    token = create_access_token(data={
        "sub": request.username,
        "role": "reader",
    })

    logger.info(f"新用户注册: {request.username}")

    return TokenResponse(
        access_token=token,
        username=request.username,
        role="reader",
        display_name=request.display_name or request.username,
    )


@router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


# ══════════════════════════════════════════════════════
# 管理员：用户管理路由
# ══════════════════════════════════════════════════════

@router.get("/admin/users")
async def admin_list_users(admin: dict = Depends(require_admin)):
    return {"success": True, "users": list_users()}


@router.post("/admin/users/create")
async def admin_create_user(
    request: UserCreateRequest,
    admin: dict = Depends(require_admin),
):
    existing = get_user_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    success = create_user(
        username=request.username,
        password_hash=hash_password(request.password),
        role=request.role,
        display_name=request.display_name or request.username,
    )
    if not success:
        raise HTTPException(status_code=500, detail="创建失败")

    logger.info(f"管理员 {admin['username']} 创建用户 {request.username} (角色: {request.role})")

    return {"success": True, "message": f"用户 {request.username} 创建成功", "role": request.role}


@router.post("/admin/users/status")
async def admin_set_user_status(
    request: UserStatusRequest,
    admin: dict = Depends(require_admin),
):
    """启用/禁用用户"""
    if request.username == admin["username"]:
        raise HTTPException(status_code=400, detail="不能修改自己的状态")

    success = update_user_status(request.username, request.is_active)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    action = "启用" if request.is_active else "禁用"
    logger.info(f"管理员 {admin['username']} {action} 用户 {request.username}")

    return {"success": True, "message": f"用户 {request.username} 已{action}"}


@router.post("/admin/users/role")
async def admin_set_user_role(
    request: UserRoleRequest,
    admin: dict = Depends(require_admin),
):
    """修改用户角色"""
    if request.username == admin["username"]:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")

    success = update_user_role(request.username, request.role)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    logger.info(f"管理员 {admin['username']} 修改用户 {request.username} 角色为 {request.role}")

    return {"success": True, "message": f"用户 {request.username} 角色已更新为 {request.role}"}


@router.post("/admin/users/password")
async def admin_reset_password(
    request: UserPasswordRequest,
    admin: dict = Depends(require_admin),
):
    """重置用户密码"""
    success = update_user_password(request.username, hash_password(request.new_password))
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")

    logger.info(f"管理员 {admin['username']} 重置用户 {request.username} 密码")

    return {"success": True, "message": f"用户 {request.username} 密码已重置"}


# ══════════════════════════════════════════════════════
# 审计日志路由
# ══════════════════════════════════════════════════════

@router.get("/audit/logs")
async def get_audit_logs(
    username: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """
    查询操作审计日志。
    reader 角色只能看自己的；admin 可看所有人并支持筛选
    """
    if current_user["role"] == "reader":
        username = current_user["username"]

    logs, total = query_audit_logs(
        username=username,
        action=action,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return {
        "success": True,
        "logs": logs,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/audit/stats")
async def get_audit_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: dict = Depends(get_current_user),
):
    """获取审计日志统计概览（最近 N 天）"""
    from datetime import datetime, timedelta
    start = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    logs, total = query_audit_logs(
        username=None if current_user["role"] == "admin" else current_user["username"],
        start_date=start,
        limit=10000,
    )

    actions_count = {}
    users_count = {}
    for log_item in logs:
        a = log_item.get("action", "UNKNOWN")
        u = log_item.get("username", "unknown")
        actions_count[a] = actions_count.get(a, 0) + 1
        users_count[u] = users_count.get(u, 0) + 1

    return {
        "success": True,
        "total_operations": total,
        "by_action": actions_count,
        "by_user": users_count,
        "period_days": days,
    }


@router.get("/audit/export")
async def export_audit_csv(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    current_user: dict = Depends(require_admin),
):
    """导出审计日志为 CSV"""
    logs, _ = query_audit_logs(
        username=None,
        action=action,
        start_date=start_date,
        end_date=end_date,
        limit=50000,
        offset=0,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "用户名", "角色", "操作", "目标", "时间", "结果", "IP"])
    for log_item in logs:
        writer.writerow([
            log_item.get("id", ""),
            log_item.get("username", ""),
            log_item.get("role", ""),
            log_item.get("action", ""),
            log_item.get("target", ""),
            log_item.get("created_at", ""),
            log_item.get("result", ""),
            log_item.get("ip_address", ""),
        ])

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_log.csv"},
    )


# ══════════════════════════════════════════════════════
# 管理员：高危 SQL 执行
# ══════════════════════════════════════════════════════

@router.post("/admin/execute")
async def admin_execute_sql(
    request: AdminSQLRequest,
    req: Request,
    admin: dict = Depends(require_write),
):
    """【管理员专用】执行 DDL/DML 操作（自动备份+审计）"""
    client_ip = req.client.host if req.client else ""

    result = execute_admin_sql(
        sql=request.sql,
        database=request.database,
        username=admin["username"],
        role=admin["role"],
        ip_address=client_ip,
    )

    return result


# ══════════════════════════════════════════════════════
# 备份管理路由
# ══════════════════════════════════════════════════════

@router.get("/admin/backups")
async def admin_list_backups(
    database: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    admin: dict = Depends(require_admin),
):
    """列出备份文件"""
    backups = list_backups(database=database, limit=limit)
    return {"success": True, "backups": backups, "backup_dir": str(list_backups.__globals__["BACKUP_DIR"])}


@router.post("/admin/backups/restore")
async def admin_restore_backup(
    request: BackupRestoreRequest,
    admin: dict = Depends(require_admin),
):
    """从备份恢复"""
    result = restore_backup(request.filename, request.target_database)

    add_audit_log(
        username=admin["username"],
        role=admin["role"],
        action="RESTORE_BACKUP",
        target=request.target_database or request.filename,
        detail=f"从备份 {request.filename} 恢复",
        result="SUCCESS" if result["success"] else "FAILED",
    )

    return result


# ══════════════════════════════════════════════════════
# 核心对话接口 (SSE 流式)
# ══════════════════════════════════════════════════════

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    req: Request,
    current_user: dict = Depends(get_current_user),
):
    """SSE 流式对话接口"""
    session_id = request.session_id or uuid.uuid4().hex[:16]

    return StreamingResponse(
        chat_stream_generator(
            session_id=session_id,
            user_message=request.message,
            database=request.database,
            user_role=current_user["role"],
            username=current_user["username"],
            model=request.model,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Session-Id": session_id,
        },
    )


# ══════════════════════════════════════════════════════
# 会话管理
# ══════════════════════════════════════════════════════

@router.post("/session/create")
async def create_session(
    request: SessionCreateRequest = SessionCreateRequest(),
    current_user: dict = Depends(get_current_user),
):
    """创建新会话"""
    sid = session_manager.create_session()
    if request.database:
        session_manager.set_database(sid, request.database)
    return {"session_id": sid}


@router.get("/session/{session_id}/history")
async def get_session_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {
        "session_id": session_id,
        "messages": session["messages"],
        "database": session.get("database"),
        "created_at": session.get("created_at"),
        "summary": session.get("summary"),
    }


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    session_manager._sessions.pop(session_id, None)
    return {"success": True, "message": "会话已删除"}


# ══════════════════════════════════════════════════════
# 数据库列表接口
# ══════════════════════════════════════════════════════

@router.get("/databases")
async def api_list_databases(current_user: dict = Depends(get_current_user)):
    """列出 MySQL 服务器上所有可访问的数据库"""
    try:
        conn = pool_manager.get_connection()

        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            dbs = [
                list(row.values())[0] if isinstance(row, dict) else row[0]
                for row in cursor.fetchall()
            ]
        conn.close()

        system_dbs = {"information_schema", "mysql", "performance_schema", "sys"}
        result = [{"name": db, "system": db in system_dbs} for db in dbs]
        return {"success": True, "databases": result}
    except Exception as e:
        logger.error(f"获取数据库列表失败: {e}")
        return {"success": False, "error": "无法连接数据库", "databases": []}


# ══════════════════════════════════════════════════════
# 数据库对象浏览器接口
# ══════════════════════════════════════════════════════

@router.get("/objects")
async def api_get_database_objects(
    database: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    """获取数据库对象树（表、视图）"""
    try:
        conn = pool_manager.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW FULL TABLES FROM `%s`" % database)
            rows = cursor.fetchall()

        tables = []
        views = []
        for row in rows:
            values = list(row.values())
            name, obj_type = values[0], values[1] if len(values) > 1 else "BASE TABLE"
            if obj_type == "VIEW":
                views.append({"name": name, "type": "view"})
            else:
                tables.append({"name": name, "type": "table"})

        conn.close()
        return {"success": True, "database": database, "tables": tables, "views": views}
    except Exception as e:
        logger.error(f"获取数据库对象失败: {e}")
        return {"success": False, "error": str(e)}


@router.get("/objects/{database}/{table}/columns")
async def api_get_table_columns(
    database: str,
    table: str,
    current_user: dict = Depends(get_current_user),
):
    """获取表列信息"""
    try:
        conn = pool_manager.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW FULL COLUMNS FROM `%s`.`%s`" % (database, table))
            columns = cursor.fetchall()
        conn.close()

        result = []
        for col in columns:
            result.append({
                "name": col.get("Field", ""),
                "type": col.get("Type", ""),
                "nullable": col.get("Null", "YES") == "YES",
                "key": col.get("Key", ""),
                "default": col.get("Default"),
                "extra": col.get("Extra", ""),
                "comment": col.get("Comment", ""),
            })
        return {"success": True, "database": database, "table": table, "columns": result}
    except Exception as e:
        logger.error(f"获取列信息失败: {e}")
        return {"success": False, "error": str(e)}


@router.get("/objects/{database}/{table}/indexes")
async def api_get_table_indexes(
    database: str,
    table: str,
    current_user: dict = Depends(get_current_user),
):
    """获取表索引信息"""
    try:
        conn = pool_manager.get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW INDEX FROM `%s`.`%s`" % (database, table))
            indexes = cursor.fetchall()
        conn.close()

        result = []
        for idx in indexes:
            result.append({
                "key_name": idx.get("Key_name", ""),
                "column_name": idx.get("Column_name", ""),
                "non_unique": idx.get("Non_unique", 1) == 1,
                "index_type": idx.get("Index_type", ""),
                "cardinality": idx.get("Cardinality", 0),
            })
        return {"success": True, "database": database, "table": table, "indexes": result}
    except Exception as e:
        logger.error(f"获取索引信息失败: {e}")
        return {"success": False, "error": str(e)}


# ══════════════════════════════════════════════════════
# 只读工具接口（Body 参数）
# ══════════════════════════════════════════════════════

@router.post("/metadata")
async def api_get_metadata(
    request: MetadataRequest,
    current_user: dict = Depends(get_current_user),
):
    """获取数据库元数据"""
    return get_table_metadata(request.database, request.table)


# 向后兼容：GET 请求也支持
@router.get("/metadata")
async def api_get_metadata_get(
    database: str = Query(..., min_length=1),
    table: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """获取数据库元数据（GET兼容）"""
    return get_table_metadata(database, table)


@router.post("/execute")
async def api_execute(
    request: ExecuteRequest,
    current_user: dict = Depends(get_current_user),
):
    """执行只读 SQL 查询"""
    result = execute_readonly_sql(request.database, request.sql, request.limit)

    # 审计日志（仅在此处记录，避免与 Agent 工具重复）
    add_audit_log(
        username=current_user["username"],
        role=current_user["role"],
        action="EXECUTE_SQL",
        target=f"{request.database}: {request.sql[:100]}",
        detail=request.sql[:2000],
        result="SUCCESS" if result.get("success") else "FAILED",
    )

    return result


@router.post("/explain")
async def api_explain(
    request: ExplainRequest,
    current_user: dict = Depends(get_current_user),
):
    """EXPLAIN 分析"""
    return explain_sql(request.database, request.sql)


@router.get("/inspect")
async def api_inspect(
    database: str = Query(..., min_length=1),
    current_user: dict = Depends(get_current_user),
):
    """表结构巡检"""
    return inspect_table_schema(database)


@router.post("/generate-data")
async def api_generate_data(
    request: GenerateDataRequest,
    current_user: dict = Depends(get_current_user),
):
    """生成测试数据 SQL"""
    return generate_test_data(
        request.database, request.table, request.scenario, request.row_count
    )


@router.post("/execute-test-data")
async def api_execute_test_data(
    request: ExecuteTestDataRequest,
    req: Request,
    current_user: dict = Depends(get_current_user),
):
    """执行测试数据 INSERT（需要写权限）"""
    import pymysql

    inserted = 0
    errors = []
    conn = None

    logger.info(f"[ExecuteTestData] {len(request.insert_statements)} 条 SQL, 目标库: {request.database}")

    try:
        conn = pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=request.database,
            charset="utf8mb4",
            autocommit=True,
            read_timeout=30,
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
        )

        with conn.cursor() as cursor:
            for i, sql in enumerate(request.insert_statements):
                try:
                    cursor.execute(sql)
                    inserted += cursor.rowcount
                except Exception as e:
                    errors.append(str(e)[:500])
                    logger.warning(f"[ExecuteTestData] SQL #{i + 1} 失败: {e}")

    except Exception as conn_err:
        logger.error(f"[ExecuteTestData] 连接失败: {conn_err}")
        return {"success": False, "inserted": 0, "error": "数据库连接失败"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    # 审计日志
    if inserted > 0 or errors:
        try:
            add_audit_log(
                username=current_user["username"],
                role=current_user["role"],
                action="INSERT_INTO",
                target=f"{request.database}: 测试数据",
                detail=f"共 {len(request.insert_statements)} 条 SQL, 成功 {inserted} 条",
                result="SUCCESS" if len(errors) == 0 else "PARTIAL",
                ip_address=req.client.host if req.client else "",
            )
        except Exception:
            pass

    return {"success": len(errors) == 0, "inserted": inserted, "errors": errors[:10]}


# ══════════════════════════════════════════════════════
# 数据导出接口
# ══════════════════════════════════════════════════════

@router.post("/export/csv")
async def export_csv(
    request: ExecuteRequest,
    current_user: dict = Depends(get_current_user),
):
    """导出查询结果为 CSV"""
    result = execute_readonly_sql(request.database, request.sql, request.limit or settings.result_row_max)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "查询失败"))

    rows = result.get("rows", [])
    columns = result.get("columns", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)

    for row in rows:
        writer.writerow([row.get(c, "") for c in columns])

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=export.csv"},
    )


@router.post("/export/json")
async def export_json(
    request: ExecuteRequest,
    current_user: dict = Depends(get_current_user),
):
    """导出查询结果为 JSON"""
    result = execute_readonly_sql(request.database, request.sql, request.limit or settings.result_row_max)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "查询失败"))

    return {
        "success": True,
        "columns": result.get("columns", []),
        "rows": result.get("rows", []),
        "row_count": result.get("row_count", 0),
    }


# ══════════════════════════════════════════════════════
# 知识库管理接口
# ══════════════════════════════════════════════════════

@router.post("/knowledge/init")
async def api_init_knowledge(
    force: bool = Query(False),
    current_user: dict = Depends(get_current_user),
):
    """初始化/重建知识库"""
    count = init_knowledge_base(force=force)
    return {"success": True, "knowledge_count": count}


@router.get("/knowledge/search")
async def api_search_knowledge(
    query: str = Query(..., min_length=1),
    top_k: int = Query(3, ge=1, le=10),
    current_user: dict = Depends(get_current_user),
):
    """搜索知识库"""
    items = retrieve_knowledge(query, top_k=top_k)
    return {"success": True, "query": query, "results": items}


@router.get("/knowledge/list")
async def api_list_knowledge(
    current_user: dict = Depends(get_current_user),
):
    """列出所有知识条目"""
    items = list_all_knowledge()
    return {"success": True, "total": len(items), "items": items}


@router.post("/knowledge/add")
async def api_add_knowledge(
    request: KnowledgeAddRequest,
    admin: dict = Depends(require_admin),
):
    """添加知识条目（管理员）"""
    kid = add_knowledge(request.content, request.metadata or {})
    logger.info(f"管理员 {admin['username']} 添加知识条目: {kid}")
    return {"success": True, "knowledge_id": kid, "message": "知识条目已添加"}


@router.delete("/knowledge/{knowledge_id}")
async def api_remove_knowledge(
    knowledge_id: str,
    admin: dict = Depends(require_admin),
):
    """删除知识条目（管理员）"""
    success = remove_knowledge(knowledge_id)
    if not success:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    logger.info(f"管理员 {admin['username']} 删除知识条目: {knowledge_id}")
    return {"success": True, "message": "知识条目已删除"}


# ══════════════════════════════════════════════════════
# 系统信息
# ══════════════════════════════════════════════════════

@router.get("/system/info")
async def system_info(admin: dict = Depends(require_admin)):
    """系统信息（管理员可见）"""
    return {
        "version": settings.version,
        "mysql_host": f"{settings.mysql_host}:{settings.mysql_port}",
        "deepseek_model": settings.deepseek_model,
        "embedding_model": settings.embedding_model,
        "query_timeout": settings.query_timeout,
        "result_row_limit": settings.result_row_limit,
        "session_ttl": settings.session_ttl,
    }


@router.get("/system/config")
async def system_config(admin: dict = Depends(require_admin)):
    """运行时配置（可动态修改的）"""
    return {
        "query_timeout": settings.query_timeout,
        "result_row_limit": settings.result_row_limit,
        "result_row_max": settings.result_row_max,
        "session_ttl": settings.session_ttl,
        "session_max_messages": settings.session_max_messages,
        "rate_limit_login": settings.rate_limit_login,
        "rate_limit_api": settings.rate_limit_api,
    }


# ══════════════════════════════════════════════════════
# 健康检查
# ══════════════════════════════════════════════════════

@router.get("/health")
async def health_check():
    """服务健康检查（检查所有依赖）"""
    mysql_ok = False
    chroma_ok = False

    try:
        conn = pool_manager.get_connection()
        with conn.cursor() as c:
            c.execute("SELECT 1")
        conn.close()
        mysql_ok = True
    except Exception:
        pass

    try:
        from rag.knowledge_base import _collection
        if _collection:
            _collection.count()
            chroma_ok = True
    except Exception:
        pass

    return {
        "status": "ok" if (mysql_ok) else "degraded",
        "service": "Database AI Agent",
        "version": settings.version,
        "checks": {
            "mysql": "ok" if mysql_ok else "failed",
            "chromadb": "ok" if chroma_ok else "unavailable",
        },
        "features": [
            "auth", "rbac", "audit_log", "auto_backup",
            "rate_limit", "knowledge_base",
        ],
    }