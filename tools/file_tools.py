"""文件处理工具"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from .base_tool import BaseTool


class FileReader(BaseTool):
    """文件读取工具"""

    name = "file_reader"
    description = "读取文件内容"

    @staticmethod
    def read_text(file_path: str, encoding: str = "utf-8") -> str:
        """读取文本文件"""
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()

    @staticmethod
    def read_json(file_path: str, encoding: str = "utf-8") -> Any:
        """读取JSON文件"""
        with open(file_path, "r", encoding=encoding) as f:
            return json.load(f)

    @staticmethod
    def read_lines(file_path: str, encoding: str = "utf-8") -> List[str]:
        """读取文件行"""
        with open(file_path, "r", encoding=encoding) as f:
            return f.readlines()

    def execute(self, file_path: str, file_type: str = "text", **kwargs) -> Any:
        if file_type == "json":
            return self.read_json(file_path, **kwargs)
        elif file_type == "lines":
            return self.read_lines(file_path, **kwargs)
        else:
            return self.read_text(file_path, **kwargs)


class FileWriter(BaseTool):
    """文件写入工具"""

    name = "file_writer"
    description = "写入文件内容"

    @staticmethod
    def write_text(file_path: str, content: str, encoding: str = "utf-8") -> bool:
        """写入文本文件"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        return True

    @staticmethod
    def write_json(file_path: str, data: Any, encoding: str = "utf-8", indent: int = 2) -> bool:
        """写入JSON文件"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True

    def execute(self, file_path: str, content: str, file_type: str = "text", **kwargs) -> bool:
        if file_type == "json":
            return self.write_json(file_path, content, **kwargs)
        else:
            return self.write_text(file_path, content, **kwargs)


class FileLister(BaseTool):
    """文件列表工具"""

    name = "file_lister"
    description = "列出目录文件"

    @staticmethod
    def list_files(
        directory: str,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[str]:
        """列出目录下的文件"""
        path = Path(directory)
        if not path.exists():
            return []

        if recursive:
            return [str(f) for f in path.rglob(pattern) if f.is_file()]
        else:
            return [str(f) for f in path.glob(pattern) if f.is_file()]

    def execute(self, directory: str, pattern: str = "*", recursive: bool = False, **kwargs) -> List[str]:
        return self.list_files(directory, pattern, recursive)


__all__ = ["FileReader", "FileWriter", "FileLister"]
