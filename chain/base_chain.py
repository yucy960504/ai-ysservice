"""Chain链式调用模块"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ChainContext:
    """链上下文"""
    data: Dict[str, Any]
    step_name: str = ""
    step_result: Any = None


class BaseChain(ABC):
    """Chain基类"""

    def __init__(self, name: str = "base_chain"):
        self.name = name
        self.steps: List[str] = []

    @abstractmethod
    def execute(self, context: ChainContext) -> ChainContext:
        """执行链"""
        pass

    def add_step(self, step_name: str):
        """添加步骤"""
        self.steps.append(step_name)


class ChainRunner:
    """Chain运行器"""

    def __init__(self):
        self.chains: Dict[str, BaseChain] = {}

    def register(self, name: str, chain: BaseChain):
        """注册Chain"""
        self.chains[name] = chain

    def run(self, chain_name: str, input_data: Any) -> ChainContext:
        """运行Chain"""
        if chain_name not in self.chains:
            raise ValueError(f"Chain not found: {chain_name}")

        chain = self.chains[chain_name]
        context = ChainContext(data=input_data or {})

        return chain.execute(context)


__all__ = ["BaseChain", "ChainContext", "ChainRunner"]
