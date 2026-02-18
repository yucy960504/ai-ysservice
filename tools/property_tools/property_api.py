"""物业专用API工具"""
from typing import Optional, Dict, Any, List
import requests
from ....tools.base_tool import BaseTool


class PropertyAPITool(BaseTool):
    """物业系统API调用工具"""

    name = "property_api"
    description = "调用物业系统API"

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or "http://property-api.internal"
        self.api_key = api_key
        self.timeout = 30

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.request(
                method, url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "success": False}

    def get_owner_info(self, room_number: str) -> Optional[Dict]:
        """获取业主信息"""
        return self._request("GET", f"/api/owner/info?room={room_number}")

    def get_fee_detail(self, owner_id: str, year: int = None) -> List[Dict]:
        """获取费用明细"""
        params = {"owner_id": owner_id}
        if year:
            params["year"] = year
        return self._request("GET", "/api/fee/detail", params=params)

    def get_work_orders(self, status: str = None, page: int = 1, size: int = 20) -> Dict:
        """获取工单列表"""
        params = {"page": page, "size": size}
        if status:
            params["status"] = status
        return self._request("GET", "/api/workorder/list", params=params)

    def create_work_order(self, data: Dict) -> Dict:
        """创建工单"""
        return self._request("POST", "/api/workorder/create", json=data)

    def get_device_info(self, device_id: str) -> Optional[Dict]:
        """获取设备信息"""
        return self._request("GET", f"/api/device/{device_id}")

    def get_notices(self, page: int = 1, size: int = 20) -> Dict:
        """获取通知公告"""
        params = {"page": page, "size": size}
        return self._request("GET", "/api/notice/list", params=params)

    def execute(self, action: str, **kwargs) -> Any:
        actions = {
            "get_owner_info": self.get_owner_info,
            "get_fee_detail": self.get_fee_detail,
            "get_work_orders": self.get_work_orders,
            "create_work_order": self.create_work_order,
            "get_device_info": self.get_device_info,
            "get_notices": self.get_notices,
        }
        action_func = actions.get(action)
        if action_func:
            return action_func(**kwargs)
        return {"error": f"Unknown action: {action}"}


__all__ = ["PropertyAPITool"]
