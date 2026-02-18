"""场景基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseScenario(ABC):
    """业务场景基类"""

    name: str = "base"

    @abstractmethod
    def process(self, input_data: Any) -> Dict:
        """处理输入，返回结果"""
        pass

    def get_info(self) -> Dict:
        """获取场景信息"""
        return {
            "name": self.name,
            "description": self.__doc__ or ""
        }


__all__ = ["BaseScenario"]
