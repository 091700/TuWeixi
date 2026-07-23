import os
import json
import logging
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader

logger = logging.getLogger(__name__)

class InterviewRAG:
    def __init__(self):
        # 初始化嵌入模型
        self.embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
        self.vector_store = None
        self.raw_data = []
        
        # 加载题库并构建混合知识库
        self.load_question_bank()
        self.build_hybrid_knowledge_base()
        
    def load_question_bank(self):
        """加载JSON格式面试题库，用于随机出题"""
        dataset_path = "interview_dataset.json"
        if os.path.exists(dataset_path):
            with open(dataset_path, "r", encoding="utf-8") as f:
                self.raw_data = json.load(f)
            logger.info(f"成功加载JSON题库，共 {len(self.raw_data)} 条")
        else:
            logger.warning("未找到interview_dataset.json文件，出题功能将受影响")

    def build_hybrid_knowledge_base(self):
        """构建混合知识库：整合JSON题库与PDF/TXT文档，生成向量库"""
        kb_dir = "knowledge_base"
        persist_dir = "./chroma_db"
        
        docs = []
        
        # 处理JSON结构化题库数据
        for item in self.raw_data:
            content = f"【面试题】：{item.get('question', '')}\n【标准参考】：{item.get('answer', '')}"
            docs.append(Document(
                page_content=content,
                metadata={"role": item.get("role", "general"), "source_type": "json"}
            ))
            
        # 处理PDF/TXT非结构化文档
        if not os.path.exists(kb_dir):
            os.makedirs(kb_dir)
            logger.warning(f"知识库目录'{kb_dir}'已创建，请添加PDF/TXT资料")
        else:
            pdf_loader = DirectoryLoader(kb_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
            txt_loader = DirectoryLoader(kb_dir, glob="**/*.txt", loader_cls=TextLoader,loader_kwargs={"encoding": "utf-8"})
            
            raw_pdfs = pdf_loader.load()
            raw_txts = txt_loader.load()
            
            if raw_pdfs or raw_txts:
                # 文本分块处理
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=600, 
                    chunk_overlap=100,
                    separators=["\n\n", "\n", "。", "！", "？", "；", ""]
                )
                split_docs = text_splitter.split_documents(raw_pdfs + raw_txts)
                
                for doc in split_docs:
                    doc.metadata["source_type"] = "pdf_txt"
                    doc.metadata["role"] = "global" 
                docs.extend(split_docs)

        # 构建并持久化Chroma向量库
        if docs:
            self.vector_store = Chroma.from_documents(
                documents=docs,
                embedding=self.embeddings,
                persist_directory=persist_dir
            )
            logger.info(f"混合RAG知识库构建完成，共加载 {len(docs)} 个知识切片")

    def get_random_question(self, job_role, difficulty="medium"):
        """根据岗位随机获取面试题，无匹配数据时返回默认问题"""
        import random
        questions = [item["question"] for item in self.raw_data if item.get("role") == job_role]
        if not questions:
            return f"请简单介绍一下你对 {job_role} 的理解。"
        return random.choice(questions)

    def retrieve_standard_answer(self, question, job_role, top_k=2):
        """
        双轨检索逻辑：优先检索PDF/TXT文档，无结果时检索JSON题库兜底
        返回截断后的参考内容，避免超出模型上下文限制
        """
        if not self.vector_store:
            return "未加载任何本地知识库。"

        retrieved_text = ""
        try:
            # 优先检索PDF/TXT文档
            pdf_results = self.vector_store.similarity_search(
                query=question,
                k=top_k,
                filter={"source_type": "pdf_txt"}
            )
            
            if pdf_results:
                retrieved_text += "【深度参考文档】：\n" + "\n---\n".join([doc.page_content for doc in pdf_results])
            
            # 无文档结果时，检索JSON题库
            if not pdf_results:
                json_results = self.vector_store.similarity_search(
                    query=question,
                    k=1,
                    filter={"source_type": "json", "role": job_role}
                )
                if json_results:
                    retrieved_text += "【标准题库参考】：\n" + "\n---\n".join([doc.page_content for doc in json_results])

            if not retrieved_text:
                return "（检索知识库未找到匹配点，请基于你的技术储备客观评判）"
                
            # 截断超长文本
            return retrieved_text[:1500]

        except Exception as e:
            logger.error(f"RAG检索异常: {e}")
            return "检索核心资料库失败。"

# 实例化RAG系统
rag_system = InterviewRAG()