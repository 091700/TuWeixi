"""数据库 AI 助手 —— FastAPI 应用入口（容错版）"""
import os
import sys
import logging
import traceback

if not os.environ.get("HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("db_agent")

# ── 安全启动：逐个导入，定位失败点 ──────────────
def safe_import(module_name):
    """导入模块并返回，失败时打印详细错误"""
    try:
        mod = __import__(module_name, fromlist=['*'])
        logger.info(f"  ✅ {module_name}")
        return mod
    except Exception as e:
        logger.error(f"  ❌ {module_name} 导入失败:")
        logger.error(traceback.format_exc())
        return None

logger.info("正在加载模块...")

# 按依赖顺序导入
auth_db = safe_import("auth.database")
if auth_db:
    init_auth_db = auth_db.init_auth_db
else:
    def init_auth_db(): pass

kb = safe_import("rag.knowledge_base")
if kb:
    init_knowledge_base = kb.init_knowledge_base
else:
    def init_knowledge_base(force=False): return 0

routes_mod = safe_import("api.routes")
if routes_mod is None:
    logger.error("❌ api.routes 导入失败，后端无法启动!")
    logger.error("请运行 python diagnose.py 查看详细错误")
    sys.exit(1)

router = routes_mod.router

logger.info("模块加载完成")

# ── 异步初始化 ──────────────────────────────────
_init_done = False

def do_init():
    global _init_done
    if _init_done:
        return
    _init_done = True
    try:
        init_auth_db()
        logger.info("[Init] 认证数据库就绪")
    except Exception as e:
        logger.warning(f"[Init] 认证数据库初始化失败: {e}")
    try:
        count = init_knowledge_base(force=False)
        logger.info(f"[Init] 知识库就绪，共 {count} 条")
    except Exception as e:
        logger.warning(f"[Init] 知识库初始化跳过: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    warnings = settings.validate()
    for w in warnings:
        logger.warning(w)
    logger.info(f"Database AI Agent v{settings.version} starting...")
    logger.info(f"MySQL: {settings.mysql_host}:{settings.mysql_port}")

    import threading
    threading.Thread(target=do_init, daemon=True).start()

    yield
    logger.info("Shutdown")

app = FastAPI(
    title="Database AI Agent",
    version=settings.version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"service": "Database AI Agent", "version": settings.version}

if __name__ == "__main__":
    import uvicorn
    print(f"\n{'='*50}")
    print(f"  Database AI Agent v{settings.version}")
    print(f"  Starting on http://0.0.0.0:8000")
    print(f"  APIs: /api/health, /api/auth/login, ...")
    print(f"{'='*50}\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")