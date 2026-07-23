"""RAG 知识库模块 —— 向量存储、检索、知识管理（支持模型下载失败的优雅降级）"""
import os
from typing import List, Optional

import chromadb
from sentence_transformers import SentenceTransformer

from config import settings

# ── 预置知识库内容 ────────────────────────────────
DEFAULT_KNOWLEDGE = [
    {
        "id": "sql_opt_001",
        "doc": (
            "复合索引遵循最左前缀原则。例如索引 (a, b, c)，"
            "WHERE 条件必须包含 a 才能命中索引，单独查 b 或 c 不走索引。"
        ),
        "metadata": {"category": "索引优化", "title": "最左前缀原则"},
    },
    {
        "id": "sql_opt_002",
        "doc": (
            "EXPLAIN 输出中 type=ALL 表示全表扫描，性能最差，需要添加索引。"
            "type=index 表示索引全扫描，type=range 表示范围扫描，"
            "type=ref 表示非唯一索引查找，type=eq_ref 表示唯一索引查找，"
            "type=const 表示主键等值查找（最优）。"
        ),
        "metadata": {"category": "EXPLAIN 解读", "title": "访问类型 type 含义"},
    },
    {
        "id": "sql_opt_003",
        "doc": (
            "Extra=Using filesort 表示 MySQL 需要额外排序操作，"
            "通常因为 ORDER BY 的列没有索引覆盖。解决方案：创建包含 ORDER BY 列的复合索引。"
            "Extra=Using temporary 表示使用了临时表，通常因为 GROUP BY 或 DISTINCT，"
            "性能开销大，应优化查询或添加覆盖索引。"
        ),
        "metadata": {"category": "EXPLAIN 解读", "title": "Using filesort 与 Using temporary"},
    },
    {
        "id": "sql_opt_004",
        "doc": (
            "覆盖索引：当查询的所有列都在索引中时，MySQL 可以直接从索引树获取数据，"
            "无需回表查询，性能大幅提升。例如 SQL: SELECT a, b FROM t WHERE a = 1，"
            "索引 (a, b) 即为覆盖索引。"
        ),
        "metadata": {"category": "索引优化", "title": "覆盖索引"},
    },
    {
        "id": "sql_opt_005",
        "doc": (
            "SELECT * 在大表中应避免使用，只选择需要的列。"
            "全表扫描 + SELECT * 会导致大量 IO 开销。同时应始终添加 LIMIT 限制返回行数。"
        ),
        "metadata": {"category": "SQL 优化", "title": "避免 SELECT *"},
    },
    {
        "id": "sql_opt_006",
        "doc": (
            "隐式类型转换会使索引失效。例如 WHERE phone = 13800138000，"
            "如果 phone 是 VARCHAR 类型，数字 13800138000 会触发隐式转换，"
            "导致全表扫描。正确的写法是 WHERE phone = '13800138000'。"
        ),
        "metadata": {"category": "SQL 优化", "title": "隐式类型转换导致索引失效"},
    },
    {
        "id": "schema_001",
        "doc": (
            "每个表必须有主键，推荐使用 BIGINT UNSIGNED AUTO_INCREMENT 作为主键。"
            "不要使用 UUID 作为聚簇索引主键，因为 UUID 的随机性会导致大量页分裂和碎片。"
            "如果业务需要 UUID，可以作为二级索引的唯一键。"
        ),
        "metadata": {"category": "表设计规范", "title": "主键设计原则"},
    },
    {
        "id": "schema_002",
        "doc": (
            "字段命名使用 snake_case 全小写下划线格式（如 created_at，order_id），"
            "与 MySQL 风格一致。避免使用 SQL 保留关键字（如 order、group、key）作为列名。"
            "布尔类型字段建议以 is_ 或 has_ 开头（如 is_deleted, has_paid）。"
            "日期时间字段建议以 _at 结尾（如 created_at, updated_at）。"
        ),
        "metadata": {"category": "表设计规范", "title": "字段命名规范"},
    },
    {
        "id": "schema_003",
        "doc": (
            "VARCHAR 列应设置合理的长度：名称类 50-100，地址类 200-500，"
            "描述类 500-2000。超过 2000 的场景评估使用 TEXT，但 TEXT 不能有默认值且会影响排序性能。"
            "对于超长 JSON，建议使用 JSON 类型而非 TEXT。"
        ),
        "metadata": {"category": "表设计规范", "title": "VARCHAR 长度规范"},
    },
    {
        "id": "schema_004",
        "doc": (
            "建议为以下字段添加索引：1) WHERE 条件中的列；2) JOIN 关联列；3) ORDER BY / GROUP BY 列；"
            "4) 外键列；5) 区分度高的字段。区分度低（如性别、状态枚举 < 5 种值）不建议单独建索引。"
        ),
        "metadata": {"category": "索引优化", "title": "索引添加原则"},
    },
    {
        "id": "security_001",
        "doc": (
            "SQL 注入是最常见的安全漏洞之一。永远不要拼接用户输入到 SQL 语句中。"
            "使用参数化查询（Prepared Statement）传递用户输入值。"
            "只读查询使用最小权限账号，只授予 SELECT 权限。"
            "对数据库操作进行严格的 SQL 审计和敏感关键字拦截。"
        ),
        "metadata": {"category": "SQL 安全", "title": "SQL 注入防护原则"},
    },
    {
        "id": "perf_001",
        "doc": (
            "INNER JOIN 应优先于子查询。复杂子查询可能导致重复扫描。"
            "JOIN 的表数量建议控制在 5 个以内。超过 5 个表关联时，"
            "考虑数据仓库方案或拆分为多步查询。"
        ),
        "metadata": {"category": "SQL 优化", "title": "JOIN 优化原则"},
    },
    {
        "id": "perf_002",
        "doc": (
            "MySQL 索引下推（Index Condition Pushdown, ICP）：MySQL 5.6+ 支持将 WHERE 条件中"
            "可以使用索引的部分推到存储引擎层过滤，减少回表次数。在 EXPLAIN 的 Extra 列中"
            "看到 'Using index condition' 说明 ICP 生效。"
        ),
        "metadata": {"category": "索引优化", "title": "索引下推 ICP"},
    },
]

# ── 全局单例 ───────────────────────────────────────
_embed_model = None       # None=未加载, False=加载失败, SentenceTransformer=可用
_chroma_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None


def get_embed_model() -> Optional[SentenceTransformer]:
    """获取或初始化 Embedding 模型（懒加载，失败时返回 None）"""
    global _embed_model
    if _embed_model is None:
        try:
            print(f"[RAG] 加载 Embedding 模型: {settings.embedding_model} on {settings.embedding_device}")
            _embed_model = SentenceTransformer(
                settings.embedding_model,
                device=settings.embedding_device,
            )
            print("[RAG] Embedding 模型加载成功")
        except Exception as e:
            print(f"[RAG] Embedding 模型加载失败（RAG 功能暂不可用，对话功能不受影响）: {e}")
            _embed_model = False
    return _embed_model if isinstance(_embed_model, SentenceTransformer) else None


def _model_available() -> bool:
    return get_embed_model() is not None


def get_chroma_client() -> chromadb.PersistentClient:
    """获取或初始化 ChromaDB 客户端"""
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(settings.chroma_persist_path, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_path)
    return _chroma_client


def get_collection() -> chromadb.Collection:
    """获取或初始化知识库集合"""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        try:
            _collection = client.get_collection("sql_knowledge")
        except Exception:
            _collection = client.create_collection(
                "sql_knowledge",
                metadata={"description": "MySQL 优化知识、表设计规范、EXPLAIN 解读"},
            )
    return _collection


def init_knowledge_base(force: bool = False) -> int:
    """
    初始化知识库，导入预置知识（模型不可用时优雅跳过）

    Returns:
        导入的知识条目数（0 表示跳过或失败）
    """
    if not _model_available():
        print("[RAG] Embedding 模型不可用，跳过知识库初始化")
        return 0

    collection = get_collection()

    if not force:
        existing = collection.count()
        if existing > 0:
            print(f"[RAG] 知识库已有 {existing} 条知识，跳过初始化")
            return existing

    # 清空重建
    try:
        client = get_chroma_client()
        client.delete_collection("sql_knowledge")
    except Exception:
        pass

    global _collection
    _collection = None
    collection = get_collection()

    model = get_embed_model()
    docs = [item["doc"] for item in DEFAULT_KNOWLEDGE]

    print(f"[RAG] 向量化 {len(docs)} 条知识...")
    embeddings = model.encode(docs, normalize_embeddings=True, show_progress_bar=True)

    collection.add(
        ids=[item["id"] for item in DEFAULT_KNOWLEDGE],
        documents=docs,
        metadatas=[item["metadata"] for item in DEFAULT_KNOWLEDGE],
        embeddings=embeddings.tolist(),
    )

    count = collection.count()
    print(f"[RAG] 知识库初始化完成，共 {count} 条")
    return count


def retrieve_knowledge(query: str, top_k: int = None, threshold: float = None) -> List[dict]:
    """
    检索相关知识（模型不可用时返回空列表）

    Args:
        query: 查询文本
        top_k: 返回条数，默认 3
        threshold: 相似度阈值 0-1，默认 0.6

    Returns:
        [{"document": str, "metadata": dict, "score": float}]
    """
    if top_k is None:
        top_k = settings.retrieval_top_k
    if threshold is None:
        threshold = settings.retrieval_threshold

    if not _model_available():
        return []

    collection = get_collection()
    if collection.count() == 0:
        return []

    model = get_embed_model()
    query_embedding = model.encode(
        [query], normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    items = []
    if results["ids"] and results["ids"][0]:
        for i, doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i] if results["distances"] else 1.0
            similarity = 1.0 - min(distance, 1.0)

            if similarity >= threshold:
                items.append({
                    "id": doc_id,
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": round(similarity, 4),
                })

    return items


def remove_knowledge(knowledge_id: str) -> bool:
    """从知识库中删除一条知识"""
    if not _model_available():
        return False

    collection = get_collection()
    try:
        # 检查是否存在
        result = collection.get(ids=[knowledge_id])
        if not result["ids"]:
            return False
        collection.delete(ids=[knowledge_id])
        return True
    except Exception:
        return False


def list_all_knowledge() -> list[dict]:
    """列出知识库中的所有条目"""
    if not _model_available():
        return []

    collection = get_collection()
    if collection.count() == 0:
        return []

    result = collection.get(include=["documents", "metadatas"])
    items = []
    for i, doc_id in enumerate(result["ids"]):
        items.append({
            "id": doc_id,
            "document": result["documents"][i] if result["documents"] else "",
            "metadata": result["metadatas"][i] if result["metadatas"] else {},
        })
    return items


def add_knowledge(document: str, metadata: dict = None) -> str:
    """添加单条知识到知识库"""
    import uuid

    if not _model_available():
        return ""

    collection = get_collection()
    model = get_embed_model()

    doc_id = metadata.get("id") if metadata else None
    doc_id = doc_id or f"user_{uuid.uuid4().hex[:8]}"

    embedding = model.encode(
        [document], normalize_embeddings=True
    ).tolist()

    collection.add(
        ids=[doc_id],
        documents=[document],
        metadatas=[metadata or {}],
        embeddings=embedding,
    )

    return doc_id