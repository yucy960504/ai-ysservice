"""DeepSeek客户端实现"""
from .openai_compatible_client import OpenAICompatibleClient, LLMFactory


class DeepSeekClient(OpenAICompatibleClient):
    """DeepSeek大模型客户端"""

    def __init__(self, model: str = "deepseek-chat", **kwargs):
        super().__init__(model, **kwargs)


# 注册到工厂
LLMFactory.register("deepseek", DeepSeekClient)
