"""工单智能处理服务"""
import json
from typing import Dict, Optional
from services import ChatService
from .prompt import SYSTEM_PROMPT
from utils import default_logger


class WorkOrderAIService:
    """工单智能处理服务"""

    def __init__(
        self,
        provider: str = "deepseek",
        model: str = "deepseek-chat"
    ):
        self.chat_service = ChatService(
            provider=provider,
            model=model,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3
        )

    def process(self, work_order_content: str) -> Dict:
        """处理工单"""
        try:
            response = self.chat_service.chat(
                user_message=f"请分析以下工单：\n{work_order_content}"
            )

            # 尝试解析JSON
            result = self._parse_response(response.content)

            return {
                "success": True,
                "result": result,
                "raw_response": response.content
            }

        except Exception as e:
            default_logger.error(f"Work order processing error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_response(self, response: str) -> Dict:
        """解析响应"""
        # 尝试提取JSON
        try:
            # 查找JSON块
            start = response.find("{")
            end = response.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # 如果无法解析，返回原始内容
        return {
            "type": "unknown",
            "urgency": "unknown",
            "raw_content": response
        }


__all__ = ["WorkOrderAIService"]
