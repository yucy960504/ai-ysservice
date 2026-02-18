"""HTTP请求工具"""
import requests
from typing import Dict, Any, Optional
from .base_tool import BaseTool


class HTTPTool(BaseTool):
    """HTTP请求工具"""

    name = "http_tool"
    description = "发起HTTP请求"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def get(
        self,
        url: str,
        params: Dict = None,
        headers: Dict = None,
        **kwargs
    ) -> Dict[str, Any]:
        """GET请求"""
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers),
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
            }

    def post(
        self,
        url: str,
        data: Any = None,
        json: Dict = None,
        headers: Dict = None,
        **kwargs
    ) -> Dict[str, Any]:
        """POST请求"""
        try:
            response = requests.post(
                url,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers),
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": str(e),
            }

    def execute(
        self,
        url: str,
        method: str = "GET",
        **kwargs
    ) -> Dict[str, Any]:
        """执行HTTP请求"""
        if method.upper() == "GET":
            return self.get(url, **kwargs)
        elif method.upper() == "POST":
            return self.post(url, **kwargs)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}


__all__ = ["HTTPTool"]
