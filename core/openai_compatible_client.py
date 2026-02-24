"""OpenAI 兼容 API 客户端基类

所有使用 OpenAI 兼容 API 格式的 LLM 提供商（OpenAI、DeepSeek、通义千问等）
都可以继承此基类，只需配置少量参数即可。
"""
import json
import requests
from typing import List, Dict, Generator, Optional
from .llm_client import BaseLLMClient, LLMResponse, LLMFactory


class OpenAICompatibleClient(BaseLLMClient):
    """OpenAI 兼容 API 客户端

    支持所有使用 OpenAI API 格式的 LLM 提供商。

    Args:
        model: 模型名称
        provider: 提供商标识（用于获取配置）
        extra_headers: 额外的请求头（如 OpenAI 的 Organization）
        **kwargs: 其他参数传递给基类
    """

    def __init__(
        self,
        model: str,
        provider: str = None,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        super().__init__(model, **kwargs)
        self._provider = provider or self._get_provider_name()
        self._extra_headers = extra_headers or {}

    def _get_provider_name(self) -> str:
        """获取提供商名称（子类可覆盖）"""
        return self.__class__.__name__.lower().replace("client", "")

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        headers.update(self._extra_headers)
        return headers

    def _build_payload(
        self,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
        stream: bool = False,
        **kwargs
    ) -> Dict:
        """构建请求体"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        if stream:
            payload["stream"] = True
        return payload

    def _parse_response(self, data: Dict) -> LLMResponse:
        """解析响应数据"""
        choice = data["choices"][0]["message"]
        return LLMResponse(
            content=choice["content"],
            model=self.model,
            usage=data.get("usage", {}),
            raw_response=data,
            finish_reason=data["choices"][0].get("finish_reason")
        )

    def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            LLMResponse: 响应对象
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._build_headers()
        payload = self._build_payload(messages, temperature, max_tokens, **kwargs)

        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        return self._parse_response(data)

    def stream_chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Generator[str, None, None]:
        """流式聊天

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Yields:
            str: 文本片段
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._build_headers()
        payload = self._build_payload(messages, temperature, max_tokens, stream=True, **kwargs)

        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=self.timeout)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_str)
                        content = chunk["choices"][0].get("delta", {}).get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError):
                        # 忽略解析错误的行
                        continue
