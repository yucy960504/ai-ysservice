"""文本处理工具"""
import re
from typing import List, Optional
from .base_tool import BaseTool


class TextCleaner(BaseTool):
    """文本清洗工具"""

    name = "text_cleaner"
    description = "清洗文本中的特殊字符和多余空白"

    @staticmethod
    def clean(text: str, remove_extra_spaces: bool = True) -> str:
        """清洗文本"""
        if not text:
            return ""

        # 移除多余空白
        if remove_extra_spaces:
            text = re.sub(r'\s+', ' ', text)

        # 移除特殊控制字符
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        return text.strip()

    def execute(self, text: str, **kwargs) -> str:
        return self.clean(text, **kwargs)


class TextSplitter(BaseTool):
    """文本分割工具"""

    name = "text_splitter"
    description = "将长文本分割为小块"

    @staticmethod
    def split_by_chars(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """按字符数分割"""
        if not text:
            return []

        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    @staticmethod
    def split_by_sentences(text: str, max_chars: int = 1000) -> List[str]:
        """按句子分割"""
        if not text:
            return []

        # 简单的句子分割
        sentences = re.split(r'[。！？\n]', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + "。"

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def execute(self, text: str, chunk_size: int = 1000, overlap: int = 100, **kwargs) -> List[str]:
        return self.split_by_chars(text, chunk_size, overlap)


class TextExtractor(BaseTool):
    """文本提取工具"""

    name = "text_extractor"
    description = "从文本中提取指定信息"

    @staticmethod
    def extract_phone(text: str) -> List[str]:
        """提取手机号"""
        pattern = r'1[3-9]\d{9}'
        return re.findall(pattern, text)

    @staticmethod
    def extract_id_card(text: str) -> List[str]:
        """提取身份证号"""
        pattern = r'[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]'
        return re.findall(pattern, text)

    @staticmethod
    def extract_email(text: str) -> List[str]:
        """提取邮箱"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(pattern, text)

    @staticmethod
    def extract_url(text: str) -> List[str]:
        """提取URL"""
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(pattern, text)

    def execute(self, text: str, extract_type: str = "phone", **kwargs) -> List[str]:
        extractors = {
            "phone": self.extract_phone,
            "id_card": self.extract_id_card,
            "email": self.extract_email,
            "url": self.extract_url,
        }
        extractor = extractors.get(extract_type)
        if extractor:
            return extractor(text)
        return []


__all__ = ["TextCleaner", "TextSplitter", "TextExtractor"]
