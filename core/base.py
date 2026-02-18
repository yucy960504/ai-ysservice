"""基础抽象类模块"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ScenarioConfig:
    """场景配置"""
    name: str
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: Optional[str] = None


class BaseScenario(ABC):
    """业务场景基类"""

    def __init__(self, config: ScenarioConfig):
        self.config = config
        from .llm_client import LLMFactory
        self.llm = LLMFactory.create(config.provider, config.model)

    @abstractmethod
    def process(self, user_input: Any) -> Dict:
        """处理用户输入"""
        pass

    def build_messages(
        self,
        user_input: Any,
        history: List[Dict] = None,
        system_prompt: str = None
    ) -> List[Dict]:
        """构建消息列表"""
        messages = []

        # 系统提示词
        prompt = system_prompt or self.config.system_prompt
        if prompt:
            messages.append({"role": "system", "content": prompt})

        # 历史对话
        if history:
            messages.extend(history)

        # 当前输入
        messages.append({"role": "user", "content": str(user_input)})

        return messages


class BaseTool(ABC):
    """工具基类"""

    name: str
    description: str

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


__all__ = ["ScenarioConfig", "BaseScenario", "BaseTool"]
