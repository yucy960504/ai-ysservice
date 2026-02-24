"""OpenAI客户端实现"""
from .openai_compatible_client import OpenAICompatibleClient, LLMFactory


class OpenAIClient(OpenAICompatibleClient):
    """OpenAI大模型客户端"""

    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(model, **kwargs)
        # 添加 OpenAI Organization 头（如果配置中有）
        if self.extra_params.get("organization"):
            self._extra_headers["OpenAI-Organization"] = self.extra_params["organization"]


# 注册到工厂
LLMFactory.register("openai", OpenAIClient)
