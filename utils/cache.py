"""缓存工具"""
import time
from typing import Any, Optional, Callable
from functools import wraps


class SimpleCache:
    """简单内存缓存"""

    def __init__(self, ttl: int = 3600):
        self._cache = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            value, expire_time = self._cache[key]
            if time.time() < expire_time:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存"""
        expire_time = time.time() + (ttl or self._ttl)
        self._cache[key] = (value, expire_time)

    def delete(self, key: str):
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """清空缓存"""
        self._cache.clear()

    def has(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self.get(key) is not None


def cached(ttl: int = 3600, key_func: Callable = None):
    """缓存装饰器"""
    cache = SimpleCache(ttl)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数并缓存
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        wrapper.cache = cache
        return wrapper

    return decorator


# 全局缓存实例
default_cache = SimpleCache()


__all__ = ["SimpleCache", "cached", "default_cache"]
