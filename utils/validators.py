"""数据验证工具"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ValidationError, Field


class BaseValidator:
    """基础验证器"""

    @staticmethod
    def required(value: Any, field_name: str = "field") -> Any:
        """必填验证"""
        if value is None or value == "":
            raise ValueError(f"{field_name} is required")
        return value

    @staticmethod
    def min_length(value: str, min_len: int, field_name: str = "field") -> str:
        """最小长度验证"""
        if len(value) < min_len:
            raise ValueError(f"{field_name} must be at least {min_len} characters")
        return value

    @staticmethod
    def max_length(value: str, max_len: int, field_name: str = "field") -> str:
        """最大长度验证"""
        if len(value) > max_len:
            raise ValueError(f"{field_name} must be at most {max_len} characters")
        return value

    @staticmethod
    def range(value: int, min_val: int, max_val: int, field_name: str = "field") -> int:
        """范围验证"""
        if not min_val <= value <= max_val:
            raise ValueError(f"{field_name} must be between {min_val} and {max_val}")
        return value


class RequestValidator(BaseValidator):
    """请求验证器"""

    @staticmethod
    def validate_chat_request(data: Dict) -> Dict:
        """验证聊天请求"""
        if not data.get("messages"):
            raise ValueError("messages is required")

        for msg in data["messages"]:
            if "role" not in msg or "content" not in msg:
                raise ValueError("Each message must have role and content")

        return data

    @staticmethod
    def validate_scenario_request(data: Dict, required_fields: List[str]) -> Dict:
        """验证场景请求"""
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Field '{field}' is required")

        return data


class ResponseValidator(BaseValidator):
    """响应验证器"""

    @staticmethod
    def validate_llm_response(response: Any) -> bool:
        """验证LLM响应"""
        if not response:
            return False

        if hasattr(response, "content"):
            return bool(response.content)

        if isinstance(response, dict):
            return bool(response.get("content"))

        return False

    @staticmethod
    def format_success_response(data: Any, message: str = "success") -> Dict:
        """格式化成功响应"""
        return {
            "success": True,
            "message": message,
            "data": data
        }

    @staticmethod
    def format_error_response(error: str, code: int = 400) -> Dict:
        """格式化错误响应"""
        return {
            "success": False,
            "error": error,
            "code": code
        }


__all__ = ["BaseValidator", "RequestValidator", "ResponseValidator"]
