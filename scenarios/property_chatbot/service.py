"""智能客服场景服务"""
from typing import Dict, List, Optional
from core import ScenarioConfig, LLMFactory
from services import ChatService, ConversationManager
from .prompt import SYSTEM_PROMPT
from utils import default_logger


class PropertyChatbotService:
    """物业智能客服服务"""

    def __init__(
        self,
        provider: str = "deepseek",
        model: str = "deepseek-chat",
        temperature: float = 0.7,
        max_history: int = 20
    ):
        self.config = ScenarioConfig(
            name="property_chatbot",
            provider=provider,
            model=model,
            temperature=temperature,
            system_prompt=SYSTEM_PROMPT
        )

        self.chat_service = ChatService(
            provider=provider,
            model=model,
            system_prompt=SYSTEM_PROMPT,
            temperature=temperature
        )

        self.conversation_manager = ConversationManager(max_history=max_history)

    def chat(self, user_message: str, session_id: str = "default") -> Dict:
        """处理用户对话"""
        # 获取历史
        history = self.conversation_manager.get_history(session_id)

        # 添加用户消息到历史
        self.conversation_manager.add_message(session_id, "user", user_message)

        try:
            # 调用LLM
            response = self.chat_service.chat(
                user_message=user_message,
                history=history
            )

            # 添加助手消息到历史
            self.conversation_manager.add_message(
                session_id,
                "assistant",
                response.content
            )

            return {
                "success": True,
                "message": response.content,
                "session_id": session_id,
                "usage": response.usage
            }

        except Exception as e:
            default_logger.error(f"Chat error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }

    def stream_chat(self, user_message: str, session_id: str = "default"):
        """流式对话"""
        history = self.conversation_manager.get_history(session_id)
        self.conversation_manager.add_message(session_id, "user", user_message)

        try:
            for chunk in self.chat_service.stream_chat(user_message, history):
                yield chunk
        except Exception as e:
            default_logger.error(f"Stream chat error: {str(e)}")
            yield f"Error: {str(e)}"

    def clear_session(self, session_id: str):
        """清除会话"""
        self.conversation_manager.clear_history(session_id)


__all__ = ["PropertyChatbotService"]
