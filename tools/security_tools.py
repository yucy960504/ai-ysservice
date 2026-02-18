"""安全相关工具"""
import hashlib
import hmac
import base64
import re
from typing import Optional
from .base_tool import BaseTool


class HashTool(BaseTool):
    """哈希工具"""

    name = "hash_tool"
    description = "生成哈希值"

    @staticmethod
    def md5(text: str) -> str:
        """MD5哈希"""
        return hashlib.md5(text.encode()).hexdigest()

    @staticmethod
    def sha256(text: str) -> str:
        """SHA256哈希"""
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def hmac_sha256(key: str, text: str) -> str:
        """HMAC-SHA256"""
        return hmac.new(
            key.encode(),
            text.encode(),
            hashlib.sha256
        ).hexdigest()

    def execute(self, text: str, algorithm: str = "sha256", key: str = None, **kwargs) -> str:
        if algorithm == "md5":
            return self.md5(text)
        elif algorithm == "hmac_sha256" and key:
            return self.hmac_sha256(key, text)
        else:
            return self.sha256(text)


class DataMasker(BaseTool):
    """数据脱敏工具"""

    name = "data_masker"
    description = "敏感数据脱敏"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """手机号脱敏"""
        if len(phone) == 11:
            return phone[:3] + "****" + phone[7:]
        return phone

    @staticmethod
    def mask_id_card(id_card: str) -> str:
        """身份证号脱敏"""
        if len(id_card) == 18:
            return id_card[:6] + "********" + id_card[-4:]
        return id_card

    @staticmethod
    def mask_name(name: str) -> str:
        """姓名脱敏"""
        if len(name) == 2:
            return name[0] + "*"
        elif len(name) > 2:
            return name[0] + "*" * (len(name) - 2) + name[-1]
        return name

    @staticmethod
    def mask_email(email: str) -> str:
        """邮箱脱敏"""
        parts = email.split("@")
        if len(parts) == 2:
            username = parts[0]
            if len(username) > 3:
                return username[:3] + "***@" + parts[1]
            return "***@" + parts[1]
        return email

    def execute(self, text: str, mask_type: str = "phone", **kwargs) -> str:
        maskers = {
            "phone": self.mask_phone,
            "id_card": self.mask_id_card,
            "name": self.mask_name,
            "email": self.mask_email,
        }
        masker = maskers.get(mask_type)
        if masker:
            return masker(text)
        return text


class Validator(BaseTool):
    """数据验证工具"""

    name = "validator"
    description = "数据格式验证"

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """验证手机号"""
        return bool(re.match(r'^1[3-9]\d{9}$', phone))

    @staticmethod
    def is_valid_id_card(id_card: str) -> bool:
        """验证身份证号"""
        return bool(re.match(
            r'^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$',
            id_card
        ))

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """验证邮箱"""
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

    def execute(self, text: str, validate_type: str = "phone", **kwargs) -> bool:
        validators = {
            "phone": self.is_valid_phone,
            "id_card": self.is_valid_id_card,
            "email": self.is_valid_email,
        }
        validator = validators.get(validate_type)
        if validator:
            return validator(text)
        return False


__all__ = ["HashTool", "DataMasker", "Validator"]
