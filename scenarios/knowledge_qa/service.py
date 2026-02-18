"""知识库问答服务"""
from typing import Dict, List
from services import ChatService, RAGService
from .prompt import SYSTEM_PROMPT
from utils import default_logger


class KnowledgeQAService:
    """知识库问答服务"""

    def __init__(
        self,
        provider: str = "deepseek",
        model: str = "deepseek-chat",
        knowledge_base: List[str] = None
    ):
        self.chat_service = ChatService(
            provider=provider,
            model=model,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.5
        )

        # 初始化RAG服务
        self.rag_service = RAGService(
            knowledge_base=knowledge_base,
            chat_service=self.chat_service
        )

    def add_knowledge(self, knowledge: str):
        """添加知识"""
        self.rag_service.add_document(knowledge)

    def query(self, question: str) -> Dict:
        """问答查询"""
        try:
            answer = self.rag_service.query(question)
            return {
                "success": True,
                "answer": answer,
                "question": question
            }
        except Exception as e:
            default_logger.error(f"Knowledge QA error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


__all__ = ["KnowledgeQAService"]
