"""Key配置管理模块

支持两种模式：
1. 云端模式：优先从阿里云KMS获取Key（每次请求获取）
2. 本地模式：从环境变量获取Key

通过 USE_CLOUD_KEY=1 开启云端模式
"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# 加载本地环境变量（用于本地开发备选）
load_dotenv()

# 是否使用云端Key管理
USE_CLOUD_KEY = os.getenv("USE_CLOUD_KEY", "0") == "1"

# 云端Key管理器（延迟初始化）
_cloud_key_manager = None


def _get_cloud_key_manager():
    """获取云端Key管理器实例"""
    global _cloud_key_manager
    if _cloud_key_manager is None:
        from .cloud_key_manager import cloud_key_manager, init_cloud_key_manager
        # 初始化云端Key管理器
        init_cloud_key_manager()
        _cloud_key_manager = cloud_key_manager
    return _cloud_key_manager


class KeyManager:
    """Key管理器 - 统一管理各Provider的API Key

    支持云端和本地两种模式：
    - 云端模式（USE_CLOUD_KEY=1）：从阿里云KMS获取Key
    - 本地模式：从环境变量获取Key
    """

    # 本地模式下的Provider配置
    LOCAL_PROVIDERS = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "organization": os.getenv("OPENAI_ORG"),
        },
        "deepseek": {
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        },
        "qianwen": {
            "api_key": os.getenv("QIANWEN_API_KEY"),
            "base_url": os.getenv("QIANWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        },
        "wenxin": {
            "api_key": os.getenv("WENXIN_API_KEY"),
            "secret_key": os.getenv("WENXIN_SECRET_KEY"),
            "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1",
        },
    }

    @classmethod
    def get_provider_config(cls, provider: str) -> Dict:
        """获取指定Provider的配置"""
        if USE_CLOUD_KEY:
            # 云端模式：从KMS获取
            cloud_manager = _get_cloud_key_manager()
            return cloud_manager.get_provider_config(provider)
        else:
            # 本地模式：从环境变量获取
            config = cls.LOCAL_PROVIDERS.get(provider)
            if not config:
                raise ValueError(f"Unknown provider: {provider}")
            if not config.get("api_key"):
                raise ValueError(f"API key not configured for provider: {provider}")
            return config

    @classmethod
    def get_available_providers(cls) -> list:
        """获取已配置的Provider列表"""
        if USE_CLOUD_KEY:
            cloud_manager = _get_cloud_key_manager()
            return cloud_manager.get_available_providers()
        else:
            return [
                name for name, config in cls.LOCAL_PROVIDERS.items()
                if config.get("api_key")
            ]

    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """检查Provider是否可用"""
        if USE_CLOUD_KEY:
            cloud_manager = _get_cloud_key_manager()
            return cloud_manager.is_provider_available(provider)
        else:
            config = cls.LOCAL_PROVIDERS.get(provider)
            return bool(config and config.get("api_key"))


def get_key(provider: str) -> str:
    """便捷函数：获取指定Provider的API Key"""
    return KeyManager.get_provider_config(provider)["api_key"]


def get_base_url(provider: str) -> str:
    """便捷函数：获取指定Provider的Base URL"""
    return KeyManager.get_provider_config(provider).get("base_url", "")


def get_secret_key(provider: str) -> str:
    """便捷函数：获取指定Provider的Secret Key（如百度文心）"""
    return KeyManager.get_provider_config(provider).get("secret_key", "")
