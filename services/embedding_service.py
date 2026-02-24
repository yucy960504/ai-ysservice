"""向量化服务模块"""
import time
from typing import List, Optional
from config import KeyManager
from utils import default_logger


class EmbeddingService:
    """向量化服务"""

    # OpenAI embedding 限制
    MAX_TEXT_LENGTH = 8000  # 字符数限制（约 2000 tokens）
    MAX_BATCH_SIZE = 100    # 批量请求最大数量

    def __init__(
        self,
        provider: str = "openai",
        model: str = "text-embedding-3-small",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.provider = provider
        self.model = model
        self._client = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay

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
                raise ValueError(f"Unsupported embedding provider: {self.provider}")

        return self._client

    def _validate_text(self, text: str) -> str:
        """验证并截断文本"""
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        # 截断超长文本
        if len(text) > self.MAX_TEXT_LENGTH:
            default_logger.warning(f"Text truncated from {len(text)} to {self.MAX_TEXT_LENGTH} chars")
            text = text[:self.MAX_TEXT_LENGTH]

        return text

    def _validate_texts(self, texts: List[str]) -> List[str]:
        """验证文本列表"""
        if not texts:
            return []

        if len(texts) > self.MAX_BATCH_SIZE:
            default_logger.warning(f"Batch size {len(texts)} exceeds max {self.MAX_BATCH_SIZE}, truncating")
            texts = texts[:self.MAX_BATCH_SIZE]

        return [self._validate_text(text) for text in texts if text]

    def embed(self, text: str) -> List[float]:
        """获取文本向量（带重试机制）"""
        text = self._validate_text(text)
        client = self._get_client()

        last_error = None
        for attempt in range(self.max_retries):
            try:
                if self.provider == "openai":
                    response = client.embeddings.create(
                        model=self.model,
                        input=text
                    )
                    return response.data[0].embedding
            except Exception as e:
                last_error = e
                default_logger.warning(f"Embedding attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # 指数退避

        default_logger.error(f"Embedding failed after {self.max_retries} attempts: {last_error}")
        raise last_error or RuntimeError("Embedding failed")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量获取文本向量（带重试机制）"""
        texts = self._validate_texts(texts)
        if not texts:
            return []

        client = self._get_client()
        last_error = None

        for attempt in range(self.max_retries):
            try:
                if self.provider == "openai":
                    response = client.embeddings.create(
                        model=self.model,
                        input=texts
                    )
                    return [item.embedding for item in response.data]
            except Exception as e:
                last_error = e
                default_logger.warning(f"Batch embedding attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))

        default_logger.error(f"Batch embedding failed after {self.max_retries} attempts: {last_error}")
        raise last_error or RuntimeError("Batch embedding failed")


__all__ = ["EmbeddingService"]
