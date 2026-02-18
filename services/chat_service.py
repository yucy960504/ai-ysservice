"""对话服务模块"""
from typing import Dict, List, Optional, Any
from core import LLMFactory, LLMResponse, Message
from utils import default_logger


class ChatService:
    """对话服务"""

    def __init__(
        self,
        provider: str = "deepseek",
        model: str = None,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ):
        self.llm = LLMFactory.create(provider, model)
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens

    def chat(
        self,
        user_message: str,
        history: List[Dict] = None,
        **kwargs
    ) -> LLMResponse:
        """发送对话"""
        messages = self._build_messages(user_message, history)

        default_logger.info(f"Sending chat request: {user_message[:50]}...")

        response = self.llm.chat(
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens)
        )

        default_logger.info(f"Chat response: {response.content[:50]}...")

        return response

    def stream_chat(
        self,
        user_message: str,
        history: List[Dict] = None,
        **kwargs
    ):
        """流式对话"""
        messages = self._build_messages(user_message, history)

        for chunk in self.llm.stream_chat(
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens)
        ):
            yield chunk

    def _build_messages(
        self,
        user_message: str,
        history: List[Dict] = None
    ) -> List[Dict]:
        """构建消息列表"""
        messages = []

        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_message})

        return messages


class ConversationManager:
    """对话管理器 - 管理会话历史"""

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.sessions: Dict[str, List[Dict]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到会话"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append({"role": role, "content": content})

        # 限制历史长度
        if len(self.sessions[session_id]) > self.max_history:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history:]

    def get_history(self, session_id: str) -> List[Dict]:
        """获取会话历史"""
        return self.sessions.get(session_id, [])

    def clear_history(self, session_id: str):
        """清除会话历史"""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def list_sessions(self) -> List[str]:
        """列出所有会话ID"""
        return list(self.sessions.keys())


__all__ = ["ChatService", "ConversationManager"]
