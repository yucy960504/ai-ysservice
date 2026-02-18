"""日志工具"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str,
    level: str = None,
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> logging.Logger:
    """配置日志"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(getattr(logging, log_level))

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件输出
    if log_dir:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = RotatingFileHandler(
            f"{log_dir}/{name}_{datetime.now().strftime('%Y%m%d')}.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


# 默认日志
default_logger = setup_logger("ai-ysservice")


__all__ = ["setup_logger", "default_logger"]
