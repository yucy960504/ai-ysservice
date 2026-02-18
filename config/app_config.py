"""应用配置模块"""
import os
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class AppEnv(str, Enum):
    """应用环境"""
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class AppConfig:
    """应用配置"""
    env: AppEnv
    debug: bool
    log_level: str
    api_timeout: int = 60
    max_retries: int = 3
    cache_ttl: int = 3600

    @classmethod
    def load(cls) -> "AppConfig":
        """从环境变量加载配置"""
        env_str = os.getenv("APP_ENV", "development").lower()
        env = AppEnv(env_str) if env_str in [e.value for e in AppEnv] else AppEnv.DEVELOPMENT

        debug = env in [AppEnv.LOCAL, AppEnv.DEVELOPMENT]
        log_level = os.getenv("LOG_LEVEL", "DEBUG" if debug else "INFO")

        return cls(
            env=env,
            debug=debug,
            log_level=log_level,
        )


# 全局配置实例
config = AppConfig.load()
