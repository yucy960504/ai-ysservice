"""模型配置模块"""
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ModelProvider(str, Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    QIANWEN = "qianwen"
    WENXIN = "wenxin"


# 各Provider支持的模型列表
MODEL_MAPPING = {
    "openai": {
        "gpt-4o": {"context_window": 128000, "supports_vision": True},
        "gpt-4o-mini": {"context_window": 128000, "supports_vision": True},
        "gpt-4-turbo": {"context_window": 128000, "supports_vision": True},
        "gpt-3.5-turbo": {"context_window": 16385, "supports_vision": False},
    },
    "deepseek": {
        "deepseek-chat": {"context_window": 64000, "supports_vision": False},
        "deepseek-coder": {"context_window": 64000, "supports_vision": False},
    },
    "qianwen": {
        "qwen-turbo": {"context_window": 10000, "supports_vision": False},
        "qwen-plus": {"context_window": 30000, "supports_vision": False},
        "qwen-max": {"context_window": 8000, "supports_vision": False},
    },
    "wenxin": {
        "ernie-4.0-8k": {"context_window": 8000, "supports_vision": False},
        "ernie-3.5-8k": {"context_window": 8000, "supports_vision": False},
        "ernie-speed-8k": {"context_window": 8000, "supports_vision": False},
    },
}


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0

    def to_dict(self) -> Dict:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }


# 默认场景配置
DEFAULT_SCENARIO_CONFIGS = {
    "property_chatbot": ModelConfig(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.7,
        max_tokens=1024,
    ),
    "work_order_ai": ModelConfig(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.3,
        max_tokens=2048,
    ),
    "contract_audit": ModelConfig(
        provider="qianwen",
        model="qwen-max",
        temperature=0.5,
        max_tokens=4096,
    ),
    "knowledge_qa": ModelConfig(
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.5,
        max_tokens=2048,
    ),
}


def get_model_info(provider: str, model: str) -> Optional[Dict]:
    """获取模型信息"""
    return MODEL_MAPPING.get(provider, {}).get(model)


def get_default_config(scenario: str) -> ModelConfig:
    """获取场景的默认配置"""
    return DEFAULT_SCENARIO_CONFIGS.get(scenario, ModelConfig(
        provider="deepseek",
        model="deepseek-chat",
    ))
