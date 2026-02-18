"""向量化服务模块"""
from typing import List, Optional
import requests
from config import KeyManager
from utils import default_logger


class EmbeddingService:
    """向量化服务"""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "text-embedding-3-small"
    ):
        self.provider = provider
        self.model = model
        self._client = None

    def _get_client(self):
        """获取客户端"""
        if self._client is None:
            config = KeyManager.get_provider_config(self.provider)

            if self.provider == "openai":
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=config["api_key"],
                    base_url=config.get("base_url")
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        return self._client

    def embed(self, text: str) -> List[float]:
        """获取文本向量"""
        client = self._get_client()

        if self.provider == "openai":
            response = client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding

        return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量获取文本向量"""
        client = self._get_client()

        if self.provider == "openai":
            response = client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]

        return []


__all__ = ["EmbeddingService"]
