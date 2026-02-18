"""大模型客户端封装模块"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Generator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """大模型响应"""
    content: str
    model: str
    usage: Dict[str, int]
    raw_response: Any
    finish_reason: Optional[str] = None


@dataclass
class Message:
    """消息模型"""
    role: str
    content: str

    def to_dict(self) -> Dict:
        return {"role": self.role, "content": self.content}

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        return cls(role=data["role"], content=data["content"])

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls(role="assistant", content=content)

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role="system", content=content)


class BaseLLMClient(ABC):
    """大模型客户端基类"""

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str = "",
        timeout: int = 60,
        **kwargs
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.extra_params = kwargs

    @abstractmethod
    def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求"""
        pass

    @abstractmethod
    def stream_chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Generator[str, None, None]:
        """流式聊天"""
        pass

    def chat_with_system(
        self,
        user_message: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        history: List[Dict] = None
    ) -> LLMResponse:
        """带系统提示词的聊天"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        return self.chat(messages, temperature, max_tokens)


class LLMFactory:
    """大模型工厂 - 创建不同Provider的客户端"""

    _clients = {}

    @classmethod
    def register(cls, name: str, client_class: type):
        """注册客户端"""
        cls._clients[name] = client_class
        logger.info(f"Registered LLM client: {name}")

    @classmethod
    def create(cls, provider: str, model: str = None, **kwargs) -> BaseLLMClient:
        """创建大模型客户端"""
        from ..config.key_config import KeyManager

        if provider not in cls._clients:
            available = list(cls._clients.keys())
            raise ValueError(f"Unknown provider: {provider}. Available: {available}")

        # 获取配置
        provider_config = KeyManager.get_provider_config(provider)
        api_key = provider_config["api_key"]
        base_url = provider_config.get("base_url", "")

        # 如果没有指定模型，使用默认模型
        if not model:
            model = cls._get_default_model(provider)

        client_cls = cls._clients[provider]
        return client_cls(
            model=model,
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )

    @classmethod
    def _get_default_model(cls, provider: str) -> str:
        """获取Provider的默认模型"""
        defaults = {
            "openai": "gpt-3.5-turbo",
            "deepseek": "deepseek-chat",
            "qianwen": "qwen-turbo",
            "wenxin": "ernie-3.5-8k",
        }
        return defaults.get(provider, "gpt-3.5-turbo")

    @classmethod
    def get_providers(cls) -> List[str]:
        """获取已注册的Provider列表"""
        return list(cls._clients.keys())


# 导入并注册各Provider实现
from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient
from .qianwen_client import QianwenClient

LLMFactory.register("openai", OpenAIClient)
LLMFactory.register("deepseek", DeepSeekClient)
LLMFactory.register("qianwen", QianwenClient)

__all__ = [
    "LLMResponse",
    "Message",
    "BaseLLMClient",
    "LLMFactory",
]
