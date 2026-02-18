"""提示词管理模块"""
from typing import Dict, List, Optional
from pathlib import Path
import json


class PromptManager:
    """提示词管理器"""

    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            # 默认 prompts 目录
            self.prompts_dir = Path(__file__).parent.parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)

        self._prompts: Dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self):
        """加载提示词文件"""
        if not self.prompts_dir.exists():
            return

        for file_path in self.prompts_dir.glob("*.txt"):
            key = file_path.stem
            self._prompts[key] = file_path.read_text(encoding="utf-8")

        for file_path in self.prompts_dir.glob("*.json"):
            key = file_path.stem
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._prompts[key] = data

    def get(self, key: str, **kwargs) -> str:
        """获取提示词，支持变量替换"""
        prompt = self._prompts.get(key, "")
        if not prompt:
            return ""

        # 变量替换
        if kwargs:
            try:
                prompt = prompt.format(**kwargs)
            except KeyError as e:
                pass  # 忽略缺失的变量

        return prompt

    def set(self, key: str, value: str):
        """设置提示词"""
        self._prompts[key] = value

    def has(self, key: str) -> bool:
        """检查提示词是否存在"""
        return key in self._prompts

    def list_prompts(self) -> List[str]:
        """列出所有提示词key"""
        return list(self._prompts.keys())


# 全局实例
prompt_manager = PromptManager()


# 常用提示词模板
SYSTEM_PROMPTS = {
    "property_chatbot": """你是一个物业智能助手，专门帮助业主解答关于物业服务的问题。
请用友好、专业的语气回答业主的问题。
如果遇到不确定的问题，请建议业主拨打物业服务中心电话咨询。""",

    "work_order_ai": """你是一个工单智能处理助手，负责分析和处理物业工单。
请根据工单内容提取关键信息，并给出处理建议。
工单类型包括：维修、投诉、建议、咨询等。""",

    "contract_audit": """你是一个合同审核助手，负责审核物业合同。
请从合法性、完整性、风险性等角度进行审核。
请给出具体的审核意见和改进建议。""",

    "knowledge_qa": """你是一个知识库问答助手，根据给定的知识库内容回答用户问题。
请基于提供的知识内容进行回答，不要随意发挥。
如果知识库中没有相关信息，请如实说明。""",
}


def get_system_prompt(scenario: str) -> str:
    """获取场景系统提示词"""
    return SYSTEM_PROMPTS.get(scenario, "你是一个AI助手。")
