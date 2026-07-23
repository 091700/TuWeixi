"""JWT 令牌管理 + 密码哈希 + 权限依赖注入"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt

from .database import get_user_by_username

# ── JWT 配置 ───────────────────────────────────────
from config import settings

SECRET_KEY = settings.jwt_secret_key
if not SECRET_KEY:
    import secrets
    SECRET_KEY = secrets.token_hex(32)
    print("[Security] ⚠ JWT_SECRET_KEY 未设置，使用随机密钥（重启后所有登录态失效！）")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 小时

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """对密码进行 bcrypt 哈希"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成 JWT 访问令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """解析 JWT 令牌，返回 payload 或 None"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict:
    """
    FastAPI 依赖：从 Authorization Header 中解析当前用户。

    返回: {"username": str, "role": str, "display_name": str}
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="令牌格式错误")

    # 验证用户仍然存在且激活
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="用户已被禁用")

    return {
        "username": user["username"],
        "role": user["role"],
        "display_name": user.get("display_name") or user["username"],
    }


def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[dict]:
    """可选认证：有令牌则解析，无令牌返回 None"""
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        return None
    username = payload.get("sub")
    if not username:
        return None
    user = get_user_by_username(username)
    if not user or not user.get("is_active"):
        return None
    return {
        "username": user["username"],
        "role": user["role"],
        "display_name": user.get("display_name") or user["username"],
    }


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI 依赖：要求管理员角色。
    在 get_current_user 之后叠加调用。
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="此操作需要管理员权限")
    return current_user


def require_write(current_user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI 依赖：要求有写权限（admin 角色）。
    reader 只能读，admin 可读写。
    """
    if current_user.get("role") not in ("admin",):
        raise HTTPException(status_code=403, detail="此操作需要写入权限（admin 角色）")
    return current_user