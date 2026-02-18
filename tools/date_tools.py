"""日期时间工具"""
from datetime import datetime, timedelta
from typing import Optional
from dateutil import parser
from .base_tool import BaseTool


class DateParser(BaseTool):
    """日期解析工具"""

    name = "date_parser"
    description = "解析日期字符串"

    @staticmethod
    def parse(text: str) -> Optional[datetime]:
        """解析日期字符串"""
        try:
            return parser.parse(text)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def parse_safe(text: str, default: datetime = None) -> datetime:
        """安全解析日期字符串"""
        result = DateParser.parse(text)
        return result if result else (default or datetime.now())

    def execute(self, text: str, **kwargs) -> Optional[datetime]:
        return self.parse(text)


class DateFormatter(BaseTool):
    """日期格式化工具"""

    name = "date_formatter"
    description = "格式化日期"

    @staticmethod
    def format(
        dt: datetime = None,
        format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """格式化日期"""
        if dt is None:
            dt = datetime.now()
        return dt.strftime(format_str)

    @staticmethod
    def format_date(dt: datetime = None) -> str:
        """格式化日期（年-月-日）"""
        return DateFormatter.format(dt, "%Y-%m-%d")

    @staticmethod
    def format_time(dt: datetime = None) -> str:
        """格式化时间（时:分:秒）"""
        return DateFormatter.format(dt, "%H:%M:%S")

    @staticmethod
    def format_chinese(dt: datetime = None) -> str:
        """格式化中文日期"""
        if dt is None:
            dt = datetime.now()
        return f"{dt.year}年{dt.month}月{dt.day}日 {dt.hour}时{dt.minute}分{dt.second}秒"

    def execute(self, dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S", **kwargs) -> str:
        return self.format(dt, format_str)


class DateCalculator(BaseTool):
    """日期计算工具"""

    name = "date_calculator"
    description = "日期计算"

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """加/减天数"""
        return dt + timedelta(days=days)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """加/减小时"""
        return dt + timedelta(hours=hours)

    @staticmethod
    def diff_days(dt1: datetime, dt2: datetime) -> int:
        """计算日期差（天）"""
        return (dt2 - dt1).days

    @staticmethod
    def is_weekend(dt: datetime) -> bool:
        """是否周末"""
        return dt.weekday() >= 5

    def execute(self, dt: datetime, operation: str = "add_days", value: int = 0, **kwargs) -> datetime:
        operations = {
            "add_days": self.add_days,
            "add_hours": self.add_hours,
        }
        op = operations.get(operation)
        if op:
            return op(dt, value)
        return dt


__all__ = ["DateParser", "DateFormatter", "DateCalculator"]
