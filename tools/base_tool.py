"""工具基类"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """工具输入模型"""
    tool_name: str = Field(description="工具名称")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")


class BaseTool(ABC):
    """工具基类"""

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        pass

    def get_schema(self) -> Dict:
        """获取工具的JSON Schema"""
        return {
            "name": self.name,
            "description": self.description,
        }

    def validate_params(self, **kwargs) -> bool:
        """验证参数"""
        return True


__all__ = ["BaseTool", "ToolInput"]
