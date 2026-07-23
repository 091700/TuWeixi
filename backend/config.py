"""应用配置模块，从环境变量加载配置"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# 加载 .env 文件
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=False)


class Settings:
    """全局配置单例（启动时校验必要配置）"""

    # ── DeepSeek API ────────────────────────────────────
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # ── MySQL ────────────────────────────────────────────
    mysql_host: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "agent_readonly")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "test_db")

    # 管理员写操作用独立账号
    mysql_admin_user: Optional[str] = os.getenv("MYSQL_ADMIN_USER") or None
    mysql_admin_password: Optional[str] = os.getenv("MYSQL_ADMIN_PASSWORD") or None

    # ── JWT 配置 ─────────────────────────────────────────
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")

    # ── 元数据缓存 ──────────────────────────────────────
    metadata_cache_ttl: int = int(os.getenv("METADATA_CACHE_TTL", "300"))

    # ── ChromaDB ─────────────────────────────────────────
    chroma_persist_path: str = os.getenv("CHROMA_PERSIST_PATH", "./chroma_data")

    # ── Embedding ────────────────────────────────────────
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    embedding_device: str = os.getenv("EMBEDDING_DEVICE", "cpu")

    # ── 认证数据库 ────────────────────────────────────────
    auth_mysql_database: str = os.getenv("AUTH_MYSQL_DATABASE", "agent_auth")

    # ── 安全限制 ─────────────────────────────────────────
    query_timeout: int = int(os.getenv("QUERY_TIMEOUT", "10"))
    result_row_limit: int = int(os.getenv("RESULT_ROW_LIMIT", "100"))
    result_row_max: int = int(os.getenv("RESULT_ROW_MAX", "500"))
    session_ttl: int = int(os.getenv("SESSION_TTL", "1800"))
    session_max_messages: int = int(os.getenv("SESSION_MAX_MESSAGES", "20"))

    # ── CORS ──────────────────────────────────────────────
    cors_origins: list[str] = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if o.strip()
    ]

    # ── 向量检索 ─────────────────────────────────────────
    retrieval_top_k: int = 3
    retrieval_threshold: float = 0.6

    # ── 速率限制 ─────────────────────────────────────────
    rate_limit_login: str = os.getenv("RATE_LIMIT_LOGIN", "5/minute")
    rate_limit_api: str = os.getenv("RATE_LIMIT_API", "60/minute")

    # ── 版本号（唯一来源）─────────────────────────────────
    version: str = "2.0.0"

    def validate(self) -> list[str]:
        """启动时校验必要配置，返回警告列表"""
        warnings = []

        if not self.deepseek_api_key:
            warnings.append("⚠ DEEPSEEK_API_KEY 未设置，AI 对话功能将不可用")

        if not self.mysql_password:
            warnings.append("⚠ MYSQL_PASSWORD 未设置，数据库连接将失败")

        if not self.jwt_secret_key:
            warnings.append(
                "⚠ JWT_SECRET_KEY 未设置！将使用随机密钥，"
                "所有用户登录态在重启后全部失效！"
            )

        if self.mysql_user == "root":
            warnings.append(
                "⚠ MYSQL_USER=root 存在安全风险，建议使用只读账号"
            )

        try:
            _ = int(self.mysql_port)
        except (ValueError, TypeError):
            warnings.append(f"⚠ MYSQL_PORT 值无效: {self.mysql_port}")

        return warnings


settings = Settings()

# ── 启动时打印配置校验结果 ──────────────────────────────
# （仅在直接运行或通过 main.py 导入时输出）
_warnings = settings.validate()
for w in _warnings:
    print(w)