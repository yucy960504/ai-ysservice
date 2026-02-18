"""合同审核服务"""
import json
from typing import Dict
from services import ChatService
from .prompt import SYSTEM_PROMPT
from utils import default_logger


class ContractAuditService:
    """合同审核服务"""

    def __init__(
        self,
        provider: str = "qianwen",
        model: str = "qwen-max"
    ):
        self.chat_service = ChatService(
            provider=provider,
            model=model,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.5
        )

    def audit(self, contract_content: str) -> Dict:
        """审核合同"""
        try:
            response = self.chat_service.chat(
                user_message=f"请审核以下合同：\n{contract_content}"
            )

            result = self._parse_response(response.content)

            return {
                "success": True,
                "result": result,
                "raw_response": response.content
            }

        except Exception as e:
            default_logger.error(f"Contract audit error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_response(self, response: str) -> Dict:
        """解析响应"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            pass

        return {"summary": response, "raw": True}


__all__ = ["ContractAuditService"]
