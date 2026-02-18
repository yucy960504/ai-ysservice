"""安全工具单元测试"""
import pytest
from tools import HashTool, DataMasker, Validator


class TestHashTool:
    """哈希工具测试"""

    def test_md5(self):
        result = HashTool.md5("hello")
        assert result == "5d41402abc4b2a76b9719d911017c592"

    def test_sha256(self):
        result = HashTool.sha256("hello")
        assert len(result) == 64


class TestDataMasker:
    """数据脱敏测试"""

    def test_mask_phone(self):
        phone = "13812345678"
        result = DataMasker.mask_phone(phone)
        assert result == "138****5678"

    def test_mask_id_card(self):
        id_card = "110101199001011234"
        result = DataMasker.mask_id_card(id_card)
        assert result.startswith("110101")
        assert result.endswith("1234")

    def test_mask_name(self):
        assert DataMasker.mask_name("张三") == "张*"
        assert DataMasker.mask_name("李四") == "李*"


class TestValidator:
    """验证器测试"""

    def test_valid_phone(self):
        assert Validator.is_valid_phone("13812345678") is True
        assert Validator.is_valid_phone("12345678901") is False

    def test_valid_email(self):
        assert Validator.is_valid_email("test@example.com") is True
        assert Validator.is_valid_email("invalid") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
