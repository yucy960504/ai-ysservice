"""Token计数器模块"""
from typing import Optional

# 简单估算：平均1个token约等于4个中文字符或0.75个英文单词
CHARS_PER_TOKEN = 4
WORDS_PER_TOKEN = 0.75


class TokenCounter:
    """Token计数器"""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """估算token数量（基于字符）"""
        if not text:
            return 0
        # 简单估算
        return len(text) // CHARS_PER_TOKEN

    @staticmethod
    def estimate_tokens_by_words(text: str) -> int:
        """估算token数量（基于单词）"""
        if not text:
            return 0
        words = len(text.split())
        return int(words / WORDS_PER_TOKEN)

    @staticmethod
    def count_messages_tokens(messages: list) -> int:
        """估算消息列表的总token数"""
        total = 0
        for msg in messages:
            # 消息格式开销
            total += 4
            # role
            total += len(msg.get("role", ""))
            # content
            total += TokenCounter.estimate_tokens(msg.get("content", ""))
        # 消息结束标记
        total += 2
        return total

    @staticmethod
    def truncate_messages(
        messages: list,
        max_tokens: int,
        keep_system: bool = True
    ) -> list:
        """截断消息列表以适应token限制"""
        result = []
        total_tokens = 0

        # 从后向前保留消息
        for msg in reversed(messages):
            role = msg.get("role", "")
            # 跳过系统消息（如果keep_system为True）
            if role == "system" and keep_system:
                result.insert(0, msg)
                total_tokens += TokenCounter.estimate_tokens(msg.get("content", ""))
                continue

            msg_tokens = TokenCounter.estimate_tokens(msg.get("content", ""))
            if total_tokens + msg_tokens <= max_tokens:
                result.insert(0, msg)
                total_tokens += msg_tokens
            else:
                break

        return result
