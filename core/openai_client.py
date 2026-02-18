"""OpenAI客户端实现"""
import requests
from typing import List, Dict, Generator
from .llm_client import BaseLLMClient, LLMResponse, LLMFactory


class OpenAIClient(BaseLLMClient):
    """OpenAI大模型客户端"""

    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(model, **kwargs)

    def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """发送聊天请求"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if self.extra_params.get("organization"):
            headers["OpenAI-Organization"] = self.extra_params["organization"]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]["message"]
        return LLMResponse(
            content=choice["content"],
            model=self.model,
            usage=data.get("usage", {}),
            raw_response=data,
            finish_reason=data["choices"][0].get("finish_reason")
        )

    def stream_chat(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Generator[str, None, None]:
        """流式聊天"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }

        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=self.timeout)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    import json
                    chunk = json.loads(data)
                    content = chunk["choices"][0].get("delta", {}).get("content", "")
                    if content:
                        yield content


# 注册到工厂
LLMFactory.register("openai", OpenAIClient)
