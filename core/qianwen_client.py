"""阿里云通义千问客户端实现"""
from .openai_compatible_client import OpenAICompatibleClient, LLMFactory


class QianwenClient(OpenAICompatibleClient):
    """通义千问大模型客户端"""

    def __init__(self, model: str = "qwen-turbo", **kwargs):
        super().__init__(model, **kwargs)


# 注册到工厂
LLMFactory.register("qianwen", QianwenClient)
