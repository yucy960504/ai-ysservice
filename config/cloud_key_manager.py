"""阿里云KMS密钥管理模块"""
import os
import time
import json
import hashlib
from typing import Dict, Optional, Any
from dataclasses import dataclass
import requests
import base64
import hmac
import hashlib
from datetime import datetime
from urllib.parse import quote


@dataclass
class KMSConfig:
    """KMS配置"""
    region_id: str
    access_key_id: str
    access_key_secret: str
    endpoint: str = "kms.cn-hangzhou.aliyuncs.com"
    version: str = "2016-01-20"


class AliyunKMSClient:
    """阿里云KMS客户端"""

    def __init__(self, config: KMSConfig):
        self.config = config
        self._cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self._cache_ttl = 60  # 缓存60秒，避免频繁请求

    def _sign(self, params: Dict, secret: str) -> str:
        """生成签名"""
        # 按参数名排序
        sorted_params = sorted(params.items())
        # 构造待签名字符串
        query_string = "&".join([
            f"{quote(k, safe='')}={quote(str(v), safe='')}"
            for k, v in sorted_params
        ])
        # HMAC-SHA1签名
        string_to_sign = f"GET&%2F&{quote(query_string, safe='')}"
        signature = hmac.new(
            (secret + "&").encode(),
            string_to_sign.encode(),
            hashlib.sha1
        ).digest()
        return base64.b64encode(signature).decode()

    def _request(self, action: str, params: Dict = None) -> Dict:
        """发起KMS请求"""
        params = params or {}

        # 公共参数
        common_params = {
            "Format": "JSON",
            "Version": self.config.version,
            "AccessKeyId": self.config.access_key_id,
            "SignatureMethod": "HMAC-SHA1",
            "Timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "SignatureVersion": "1.0",
            "SignatureNonce": str(int(time.time() * 1000000)),
            "Action": action,
            "RegionId": self.config.region_id,
        }
        common_params.update(params)

        # 生成签名
        signature = self._sign(common_params, self.config.access_key_secret)
        common_params["Signature"] = signature

        # 发起请求
        url = f"https://{self.config.endpoint}/"
        response = requests.get(url, params=common_params, timeout=10)
        data = response.json()

        if "Code" in data:
            raise Exception(f"KMS Error: {data['Code']} - {data['Message']}")

        return data

    def get_secret_value(self, secret_name: str, version_stage: str = "AK") -> str:
        """获取密钥值"""
        # 检查缓存
        cache_key = f"{secret_name}:{version_stage}"
        if cache_key in self._cache:
            value, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return value

        # 从KMS获取
        try:
            # 方式1：使用DescribeSecret获取密钥
            response = self._request("DescribeSecret", {
                "SecretName": secret_name
            })

            if "SecretData" in response:
                value = response["SecretData"]
            else:
                # 方式2：使用GetSecretValue
                response = self._request("GetSecretValue", {
                    "SecretName": secret_name,
                    "VersionStage": version_stage
                })
                value = response["SecretData"]

            # 更新缓存
            self._cache[cache_key] = (value, time.time())
            return value

        except Exception as e:
            # 如果KMS获取失败，尝试从环境变量获取
            env_key = secret_name.replace("-", "_").upper()
            env_value = os.getenv(env_key)
            if env_value:
                return env_value
            raise e

    def list_secrets(self) -> list:
        """列出所有密钥"""
        response = self._request("ListSecrets", {
            "PageSize": 100
        })
        return response.get("SecretList", [])


class CloudKeyManager:
    """云端Key管理器"""

    def __init__(self):
        self._kms_client: Optional[AliyunKMSClient] = None
        self._config: Dict[str, Any] = {}
        self._initialized = False

    def init(self, config: Dict = None):
        """初始化云端Key管理器"""
        if config is None:
            # 从环境变量加载配置
            config = {
                "region_id": os.getenv("KMS_REGION_ID", "cn-hangzhou"),
                "access_key_id": os.getenv("KMS_ACCESS_KEY_ID", ""),
                "access_key_secret": os.getenv("KMS_ACCESS_KEY_SECRET", ""),
                "endpoint": os.getenv("KMS_ENDPOINT", "kms.cn-hangzhou.aliyuncs.com"),
                "secret_names": self._parse_secret_names(os.getenv("KMS_SECRET_NAMES", "")),
            }

        self._config = config

        # 初始化KMS客户端
        if config.get("access_key_id") and config.get("access_key_secret"):
            kms_config = KMSConfig(
                region_id=config["region_id"],
                access_key_id=config["access_key_id"],
                access_key_secret=config["access_key_secret"],
                endpoint=config.get("endpoint", "kms.cn-hangzhou.aliyuncs.com")
            )
            self._kms_client = AliyunKMSClient(kms_config)

        self._initialized = True

    def _parse_secret_names(self, names_str: str) -> Dict[str, str]:
        """解析密钥名称配置"""
        # 格式: "openai:sk-xxx,deepseek:sk-xxx"
        result = {}
        if names_str:
            for item in names_str.split(","):
                if ":" in item:
                    provider, secret_name = item.split(":", 1)
                    result[provider.strip()] = secret_name.strip()
        return result

    def get_provider_config(self, provider: str) -> Dict:
        """获取指定Provider的配置"""
        # 优先从KMS获取
        if self._kms_client:
            secret_names = self._config.get("secret_names", {})
            if provider in secret_names:
                secret_name = secret_names[provider]
                api_key = self._kms_client.get_secret_value(secret_name)

                config = {"api_key": api_key}

                # 获取对应的base_url
                url_secret = f"{secret_name}_base_url"
                try:
                    base_url = self._kms_client.get_secret_value(url_secret)
                    config["base_url"] = base_url
                except:
                    pass

                return config

        # 回退到环境变量
        env_key = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_key)

        if not api_key:
            raise ValueError(f"API key not configured for provider: {provider}")

        config = {"api_key": api_key}

        # 获取base_url
        url_key = f"{provider.upper()}_BASE_URL"
        base_url = os.getenv(url_key)
        if base_url:
            config["base_url"] = base_url

        return config

    def get_available_providers(self) -> list:
        """获取已配置的Provider列表"""
        providers = []

        # 检查KMS配置
        if self._kms_client:
            secret_names = self._config.get("secret_names", {})
            providers.extend(secret_names.keys())

        # 检查环境变量
        for provider in ["openai", "deepseek", "qianwen", "wenxin"]:
            env_key = f"{provider.upper()}_API_KEY"
            if os.getenv(env_key) and provider not in providers:
                providers.append(provider)

        return providers

    def is_provider_available(self, provider: str) -> bool:
        """检查Provider是否可用"""
        try:
            config = self.get_provider_config(provider)
            return bool(config.get("api_key"))
        except:
            return False


# 全局实例
cloud_key_manager = CloudKeyManager()


def init_cloud_key_manager(config: Dict = None):
    """初始化云端Key管理器"""
    cloud_key_manager.init(config)


# 兼容旧接口
class KeyManager:
    """Key管理器 - 兼容旧接口"""

    PROVIDERS = {
        "openai": {"api_key": "", "base_url": ""},
        "deepseek": {"api_key": "", "base_url": ""},
        "qianwen": {"api_key": "", "base_url": ""},
        "wenxin": {"api_key": "", "base_url": ""},
    }

    @classmethod
    def get_provider_config(cls, provider: str) -> Dict:
        """获取指定Provider的配置"""
        return cloud_key_manager.get_provider_config(provider)

    @classmethod
    def get_available_providers(cls) -> list:
        """获取已配置的Provider列表"""
        return cloud_key_manager.get_available_providers()

    @classmethod
    def is_provider_available(cls, provider: str) -> bool:
        """检查Provider是否可用"""
        return cloud_key_manager.is_provider_available(provider)


def get_key(provider: str) -> str:
    """便捷函数：获取指定Provider的API Key"""
    return KeyManager.get_provider_config(provider)["api_key"]


def get_base_url(provider: str) -> str:
    """便捷函数：获取指定Provider的Base URL"""
    return KeyManager.get_provider_config(provider).get("base_url", "")
