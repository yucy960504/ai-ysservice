"""文本工具单元测试"""
import pytest
from tools import TextCleaner, TextSplitter, TextExtractor


class TestTextCleaner:
    """文本清洗测试"""

    def test_clean_basic(self):
        text = "  hello   world  "
        result = TextCleaner.clean(text)
        assert result == "hello world"

    def test_clean_empty(self):
        assert TextCleaner.clean("") == ""
        assert TextCleaner.clean(None) == ""

    def test_clean_special_chars(self):
        text = "hello\x00world\x1f"
        result = TextCleaner.clean(text)
        assert "\x00" not in result


class TestTextSplitter:
    """文本分割测试"""

    def test_split_by_chars(self):
        text = "a" * 2000
        chunks = TextSplitter.split_by_chars(text, chunk_size=1000, overlap=100)
        assert len(chunks) == 3

    def test_split_empty(self):
        assert TextSplitter.split_by_chars("") == []


class TestTextExtractor:
    """文本提取测试"""

    def test_extract_phone(self):
        text = "我的手机号是13812345678，请联系我"
        result = TextExtractor.extract_phone(text)
        assert "13812345678" in result

    def test_extract_email(self):
        text = "邮箱: test@example.com"
        result = TextExtractor.extract_email(text)
        assert "test@example.com" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
