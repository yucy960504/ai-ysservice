"""大模型专用工具"""

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


class TokenCounter:
    """Token计数工具"""

    @staticmethod
    def count(text: str, model: str = "gpt-3.5-turbo") -> int:
        """计算文本的token数量"""
        if not HAS_TIKTOKEN:
            # 简单估算
            return len(text) // 4

        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))


class EmbeddingHelper:
    """向量化辅助工具"""

    @staticmethod
    def truncate_for_embedding(text: str, max_tokens: int = 8000) -> str:
        """截断文本以适应embedding模型"""
        tokens = text.split()
        if len(tokens) <= max_tokens * 0.75:  # 估算
            return text

        # 简单截断
        chars = int(max_tokens * 4)
        return text[:chars]


__all__ = ["TokenCounter", "EmbeddingHelper"]
