"""RAG检索增强服务"""
from typing import List, Dict, Any, Optional
from .embedding_service import EmbeddingService
from .chat_service import ChatService
from tools import TextSplitter
from utils import default_logger


class RAGService:
    """RAG检索增强服务"""

    def __init__(
        self,
        knowledge_base: List[str] = None,
        embedding_service: EmbeddingService = None,
        chat_service: ChatService = None,
        top_k: int = 3
    ):
        self.knowledge_base = knowledge_base or []
        self.embedding_service = embedding_service or EmbeddingService()
        self.chat_service = chat_service or ChatService()
        self.top_k = top_k
        self._chunks = []
        self._chunk_embeddings = []

        if self.knowledge_base:
            self._process_knowledge_base()

    def _process_knowledge_base(self):
        """处理知识库"""
        self._chunks = []
        splitter = TextSplitter()

        for doc in self.knowledge_base:
            chunks = splitter.split_by_chars(doc, chunk_size=500, overlap=50)
            self._chunks.extend(chunks)

        default_logger.info(f"Knowledge base processed: {len(self._chunks)} chunks")

    def add_document(self, document: str):
        """添加文档"""
        splitter = TextSplitter()
        chunks = splitter.split_by_chars(document, chunk_size=500, overlap=50)
        self._chunks.extend(chunks)
        default_logger.info(f"Document added: {len(chunks)} chunks")

    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """检索相关文档"""
        if not self._chunks:
            return []

        k = top_k or self.top_k

        # 获取查询向量
        query_embedding = self.embedding_service.embed(query)

        # 简单相似度计算
        similarities = []
        for i, chunk in enumerate(self._chunks):
            chunk_embedding = self.embedding_service.embed(chunk)
            similarity = self._cosine_similarity(query_embedding, chunk_embedding)
            similarities.append((i, similarity))

        # 排序并取top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in similarities[:k]]

        results = []
        for idx in top_indices:
            results.append({
                "chunk": self._chunks[idx],
                "score": similarities[idx][1],
                "index": idx
            })

        return results

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0

        return dot_product / (magnitude1 * magnitude2)

    def query(self, query: str) -> str:
        """RAG查询"""
        # 检索相关文档
        retrieved = self.retrieve(query)

        if not retrieved:
            return "抱歉，知识库中没有找到相关信息。"

        # 构建上下文
        context = "\n\n".join([item["chunk"] for item in retrieved])

        # 构建提示词
        prompt = f"""根据以下知识库内容回答用户的问题。如果知识库中没有相关信息，请如实说明。

知识库内容：
{context}

用户问题：{query}

回答："""

        # 调用LLM
        response = self.chat_service.chat(prompt)

        return response.content


__all__ = ["RAGService"]
