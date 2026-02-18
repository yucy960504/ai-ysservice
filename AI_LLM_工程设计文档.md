# 物业公司大模型应用开发工程设计文档

## 1. 项目概述

### 1.1 项目目标
为物业公司建立一个统一的大模型应用开发工程，统一管理API Key、提供标准化的工具类、支持多种业务场景开发，便于团队协作和代码复用。

### 1.2 项目定位
- **定位**：物业行业大模型应用开发基础平台
- **目标用户**：物业公司大模型开发工程师
- **核心能力**：多模型接入、工具封装、业务场景模板、团队协作规范

---

## 2. 技术架构设计

### 2.1 项目目录结构

```
ai-ysservice/
├── config/                    # 配置文件目录
│   ├── model_config.py       # 模型配置（模型类型、参数等）
│   ├── key_config.py         # API Key配置（敏感信息）
│   └── app_config.py         # 应用配置
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── base.py               # 基础抽象类
│   ├── llm_client.py         # 大模型客户端封装
│   ├── prompt_manager.py     # 提示词管理
│   └── token_counter.py      # Token计数器
├── tools/                    # 工具类模块
│   ├── __init__.py
│   ├── http_tools.py         # HTTP请求工具
│   ├── file_tools.py         # 文件处理工具
│   ├── text_tools.py         # 文本处理工具
│   ├── date_tools.py         # 日期时间工具
│   └── security_tools.py     # 安全相关工具
├── services/                 # 业务服务层
│   ├── __init__.py
│   ├── chat_service.py       # 对话服务
│   ├── embedding_service.py  # 向量化服务
│   └── rag_service.py        # RAG检索增强服务
├── scenarios/                # 业务场景模块
│   ├── __init__.py
│   ├── property_chatbot/    # 智能客服场景
│   ├── work_order_ai/       # 工单智能处理场景
│   ├── contract_audit/       # 合同审核场景
│   ├── data_analysis/        # 数据分析场景
│   └── knowledge_qa/         # 知识库问答场景
├── utils/                    # 工具函数
│   ├── __init__.py
│   ├── logger.py             # 日志工具
│   ├── cache.py              # 缓存工具
│   └── validators.py         # 数据验证工具
├── chain/                    # Chain链式调用
│   ├── __init__.py
│   ├── base_chain.py         # 基础链
│   ├── property_chain.py     # 物业业务链
│   └── router.py             # 路由链
├── tests/                    # 测试目录
│   ├── unit/                 # 单元测试
│   └── integration/          # 集成测试
├── docs/                     # 文档目录
├── scripts/                  # 脚本目录
├── requirements.txt          # 依赖
├── .env.example              # 环境变量示例
├── .gitignore                # Git忽略配置
└── README.md                 # 项目说明
```

---

## 3. Key管理方案

### 3.1 设计原则
- **敏感信息分离**：API Key等敏感信息不写入代码
- **环境隔离**：不同环境使用不同的Key
- **权限控制**：Key按角色/场景分配
- **审计追溯**：记录Key使用情况

### 3.2 Key管理架构

```
config/
├── key_config.py             # Key配置（从环境变量加载）
└── .env                      # 本地开发Key（不提交）
.env.production               # 生产环境Key（不提交）
.env.staging                  # 测试环境Key（不提交）
```

### 3.3 Key配置示例

```python
# config/key_config.py
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class KeyManager:
    """Key管理器"""

    # 模型Provider配置
    PROVIDERS = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "organization": os.getenv("OPENAI_ORG"),
        },
        "deepseek": {
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        },
        "qianwen": {
            "api_key": os.getenv("QIANWEN_API_KEY"),
            "base_url": os.getenv("QIANWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        },
        "wenxin": {
            "api_key": os.getenv("WENXIN_API_KEY"),
            "secret_key": os.getenv("WENXIN_SECRET_KEY"),
        },
    }

    @classmethod
    def get_provider_config(cls, provider: str) -> Dict:
        """获取指定Provider的配置"""
        config = cls.PROVIDERS.get(provider)
        if not config:
            raise ValueError(f"Unknown provider: {provider}")
        if not config.get("api_key"):
            raise ValueError(f"API key not configured for provider: {provider}")
        return config

    @classmethod
    def get_available_providers(cls) -> list:
        """获取已配置的Provider列表"""
        return [
            name for name, config in cls.PROVIDERS.items()
            if config.get("api_key")
        ]


# 便捷访问
def get_key(provider: str) -> str:
    """获取指定Provider的API Key"""
    return KeyManager.get_provider_config(provider)["api_key"]
```

### 3.4 环境变量文件示例

```bash
# .env.example - 复制此文件为 .env 并填入真实Key

# OpenAI
OPENAI_API_KEY=sk-xxxxx
OPENAI_ORG=org-xxxxx
# 可选：使用代理或自定义端点
OPENAI_BASE_URL=https://api.openai.com/v1

# DeepSeek
DEEPSEEK_API_KEY=sk-xxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 阿里云通义千问
QIANWEN_API_KEY=sk-xxxxx
QIANWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 百度文心一言
WENXIN_API_KEY=xxxxx
WENXIN_SECRET_KEY=xxxxx

# 应用配置
APP_ENV=development  # development / staging / production
LOG_LEVEL=INFO
```

### 3.5 .gitignore配置

```gitignore
# Key和敏感配置
.env
.env.local
.env.production
.env.staging
*.pem
*.key

# 日志和缓存
logs/
*.log
__pycache__/
*.pyc
.cache/
```

### 3.6 云端Key管理（阿里云KMS）

系统支持从阿里云KMS获取API Key，实现密钥的集中管理和安全存储。

#### 3.6.1 开启云端模式

```bash
# 在 .env 中设置
USE_CLOUD_KEY=1
```

#### 3.6.2 KMS环境变量配置

```bash
# KMS访问凭证
KMS_REGION_ID=cn-hangzhou
KMS_ACCESS_KEY_ID=your-access-key-id
KMS_ACCESS_KEY_SECRET=your-access-key-secret
KMS_ENDPOINT=kms.cn-hangzhou.aliyuncs.com

# 密钥名称映射（格式：provider:SecretName）
KMS_SECRET_NAMES=deepseek:deepseek-api-key,openai:openai-api-key,qianwen:qianwen-api-key
```

#### 3.6.3 工作原理

- **每次请求获取**：KMS客户端会在每次调用时从阿里云KMS获取最新的Key
- **本地缓存**：内置60秒缓存，避免频繁请求KMS（可在cloud_key_manager.py中调整）
- **自动降级**：如果KMS不可用，会自动回退到环境变量获取

#### 3.6.4 KMS密钥创建

在阿里云KMS控制台创建普通密钥，密钥名称需与配置对应：
- `deepseek-api-key`：DeepSeek API Key
- `openapi-api-key`：OpenAI API Key
- `qianwen-api-key`：通义千问 API Key

---

## 4. 工具类分类设计

### 4.1 工具类架构

```
tools/
├── __init__.py              # 导出所有工具
├── base_tool.py             # 工具基类
├── http_tools.py             # HTTP请求工具
├── file_tools.py             # 文件处理工具
├── text_tools.py             # 文本处理工具
├── date_tools.py             # 日期时间工具
├── security_tools.py         # 安全相关工具
├── property_tools/          # 物业专用工具
│   ├── __init__.py
│   ├── property_api.py       # 物业API调用工具
│   ├── user_tools.py         # 业主信息工具
│   ├── fee_tools.py          # 费用查询工具
│   ├── work_order_tools.py   # 工单工具
│   └── device_tools.py       # 设备管理工具
└── llm_tools/               # 大模型专用工具
    ├── __init__.py
    ├── embedding.py          # 向量化工具
    ├── tokenizer.py         # 分词工具
    └── output_parser.py     # 输出解析工具
```

### 4.2 基础工具类示例

```python
# tools/base_tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """工具输入模型"""
    tool_name: str = Field(description="工具名称")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")


class BaseTool(ABC):
    """工具基类"""

    name: str
    description: str
    parameters: Optional[Dict] = None

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        pass

    def get_schema(self) -> Dict:
        """获取工具的JSON Schema"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
```

```python
# tools/text_tools.py
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


class TextSplitter(BaseTool):
    """文本分割工具"""

    name = "text_splitter"
    description = "将长文本分割为小块"

    @staticmethod
    def split_by_chars(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """按字符数分割"""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    @staticmethod
    def split_by_sentences(text: str, max_chars: int = 1000) -> List[str]:
        """按句子分割"""
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
```

```python
# tools/property_tools/property_api.py
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
from ...config.key_config import get_key


class PropertyAPITool:
    """物业系统API调用工具"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or "http://property-api.internal"
        self.timeout = 30

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
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
```

---

## 5. 大模型客户端封装

### 5.1 统一客户端设计

```python
# core/llm_client.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Generator
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """大模型响应"""
    content: str
    model: str
    usage: Dict[str, int]
    raw_response: Any


class BaseLLMClient(ABC):
    """大模型客户端基类"""

    @abstractmethod
    def chat(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """聊天接口"""
        pass

    @abstractmethod
    def stream_chat(self, messages: List[Dict], **kwargs) -> Generator[str, None, None]:
        """流式聊天接口"""
        pass


class LLMFactory:
    """大模型工厂"""

    _clients = {}

    @classmethod
    def register(cls, name: str, client_class: type):
        cls._clients[name] = client_class

    @classmethod
    def create(cls, provider: str, model: str = None, **kwargs) -> BaseLLMClient:
        """创建大模型客户端"""
        if provider not in cls._clients:
            raise ValueError(f"Unknown provider: {provider}")

        client_cls = cls._clients[provider]
        return client_cls(model=model, **kwargs)

    @classmethod
    def get_providers(cls) -> List[str]:
        return list(cls._clients.keys())


# 注册各个Provider的实现
from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient
from .qianwen_client import QianwenClient

LLMFactory.register("openai", OpenAIClient)
LLMFactory.register("deepseek", DeepSeekClient)
LLMFactory.register("qianwen", QianwenClient)
```

### 5.2 具体Provider实现示例

```python
# core/deepseek_client.py
from typing import List, Dict, Generator
import requests
from .llm_client import BaseLLMClient, LLMResponse, LLMFactory
from ..config.key_config import KeyManager


class DeepSeekClient(BaseLLMClient):
    """DeepSeek大模型客户端"""

    def __init__(self, model: str = "deepseek-chat", **kwargs):
        self.model = model
        config = KeyManager.get_provider_config("deepseek")
        self.api_key = config["api_key"]
        self.base_url = config.get("base_url", "https://api.deepseek.com/v1")
        self.default_params = {
            "model": model,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }

    def chat(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """发送聊天请求"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        params = {**self.default_params, **kwargs}
        params["messages"] = messages

        response = requests.post(url, headers=headers, json=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]["message"]
        return LLMResponse(
            content=choice["content"],
            model=self.model,
            usage=data.get("usage", {}),
            raw_response=data
        )

    def stream_chat(self, messages: List[Dict], **kwargs) -> Generator[str, None, None]:
        """流式聊天"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        params = {**self.default_params, **kwargs}
        params["messages"] = messages
        params["stream"] = True

        response = requests.post(url, headers=headers, json=params, stream=True, timeout=60)
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
LLMFactory.register("deepseek", DeepSeekClient)
```

---

## 6. 业务场景模块

### 6.1 场景目录结构

```
scenarios/
├── __init__.py
├── base.py                   # 场景基类
├── property_chatbot/        # 智能客服场景
│   ├── __init__.py
│   ├── prompt.py             # 提示词配置
│   ├── chain.py              # 对话链
│   └── service.py            # 服务实现
├── work_order_ai/           # 工单智能处理
│   ├── __init__.py
│   ├── prompt.py
│   ├── chain.py
│   └── service.py
├── contract_audit/          # 合同审核
│   ├── __init__.py
│   ├── prompt.py
│   ├── chain.py
│   └── service.py
└── knowledge_qa/            # 知识库问答
        ├── __init__.py
        ├── prompt.py
        ├── chain.py
        └── service.py
```

### 6.2 场景基类设计

```python
# scenarios/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from core.llm_client import LLMFactory


@dataclass
class ScenarioConfig:
    """场景配置"""
    name: str
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: Optional[str] = None


class BaseScenario(ABC):
    """业务场景基类"""

    def __init__(self, config: ScenarioConfig):
        self.config = config
        self.llm = LLMFactory.create(config.provider, config.model)

    @abstractmethod
    def process(self, user_input: Any) -> Dict:
        """处理用户输入"""
        pass

    def build_messages(self, user_input: Any, history: List[Dict] = None) -> List[Dict]:
        """构建消息列表"""
        messages = []

        # 系统提示词
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})

        # 历史对话
        if history:
            messages.extend(history)

        # 当前输入
        messages.append({"role": "user", "content": str(user_input)})

        return messages
```

---

## 7. 日志与监控

### 7.1 日志工具

```python
# utils/logger.py
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, level: str = None) -> logging.Logger:
    """配置日志"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(getattr(logging, log_level))

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件输出
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = RotatingFileHandler(
        f"{log_dir}/{name}_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger


# 使用示例
logger = setup_logger(__name__)
```

---

## 8. 开发规范

### 8.1 代码提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试相关
chore: 构建或辅助工具变动

示例:
feat: 添加工单智能分类功能
fix: 修复DeepSeek客户端超时问题
```

### 8.2 开发流程

1. **分支管理**
   - `main`: 生产分支
   - `develop`: 开发分支
   - `feature/xxx`: 功能分支
   - `fix/xxx`: 修复分支

2. **代码审查**
   - 所有PR需经过至少一人review
   - 敏感配置（Key）变更需额外审批

### 8.3 环境管理

```
开发环境 (local)     -> 本地调试
测试环境 (staging)   -> 集成测试
生产环境 (production)-> 正式上线
```

---

## 9. 依赖管理

### requirements.txt

```
# 核心依赖
openai>=1.0.0
requests>=2.28.0
python-dotenv>=1.0.0
pydantic>=2.0.0

# 国产模型SDK
dashscope>=1.10.0  # 阿里云
ernie>=4.0.0       # 百度文心

# 向量存储
chromadb>=0.4.0
pymilvus>=2.3.0

# 工具库
python-dateutil>=2.8.0
aiohttp>=3.8.0
tiktoken>=0.5.0

# 监控
sentry-sdk>=1.30.0

# 开发工具
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=23.0.0
ruff>=0.1.0
```

---

## 10. API接口层

### 10.1 启动API服务

```bash
# 方式1: 直接运行
python -m api.main

# 方式2: 使用uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 方式3: 使用启动脚本
python scripts/run_api.py
```

### 10.2 API接口文档

服务启动后，访问 `http://localhost:8000/docs` 查看完整API文档（Swagger UI）

#### 10.2.1 通用接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 根路径，返回服务信息 |
| `/health` | GET | 健康检查 |
| `/providers` | GET | 获取可用的模型提供商 |

#### 10.2.2 智能客服接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/chat` | POST | 智能客服对话 |
| `/chat/stream` | POST | 流式对话 |
| `/chat/session/{session_id}` | DELETE | 清除会话 |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "我想查询物业费怎么缴",
    "session_id": "user123"
  }'
```

**响应示例:**
```json
{
  "success": true,
  "message": "您好！物业费可以通过以下方式缴纳：...",
  "session_id": "user123",
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

#### 10.2.3 工单处理接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/workorder/process` | POST | 工单智能处理 |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/workorder/process" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "业主报修：3号楼2单元电梯故障，电梯门无法关闭"
  }'
```

**响应示例:**
```json
{
  "success": true,
  "result": {
    "type": "维修",
    "urgency": "高",
    "key_info": {
      "location": "3号楼2单元",
      "description": "电梯故障，电梯门无法关闭"
    },
    "suggestion": "立即通知电梯维修人员上门检修"
  }
}
```

#### 10.2.4 合同审核接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/contract/audit` | POST | 合同审核 |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/contract/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "合同内容..."
  }'
```

#### 10.2.5 知识库问答接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/knowledge/query` | POST | 知识库问答 |
| `/knowledge/add` | POST | 添加知识 |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/knowledge/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "小区停车费收费标准是什么？",
    "knowledge": [
      "小区停车费标准：地面停车位每月150元，地下停车位每月300元"
    ]
  }'
```

#### 10.2.6 通用LLM接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/llm/chat` | POST | 通用LLM对话 |

**请求示例:**
```bash
curl -X POST "http://localhost:8000/llm/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "provider": "deepseek",
    "model": "deepseek-chat",
    "temperature": 0.7
  }'
```

---

## 11. 使用指南

### 11.1 快速开始

#### 步骤1: 克隆并安装依赖

```bash
# 克隆项目
git clone <repo-url>
cd ai-ysservice

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 步骤2: 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入您的API Key
nano .env
```

`.env` 文件内容示例:
```bash
# 至少配置一个模型Provider
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx

# 可选：配置其他Provider
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
QIANWEN_API_KEY=sk-xxxxxxxxxxxxxxxx

# 应用配置
APP_ENV=development
LOG_LEVEL=INFO
```

#### 步骤3: 运行示例

```bash
# 运行示例脚本
python scripts/example.py
```

#### 步骤4: 启动API服务

```bash
# 启动API服务（默认端口8000）
python -m api.main

# 或使用uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 11.2 代码调用示例

#### 11.2.1 使用智能客服

```python
from scenarios import PropertyChatbotService

# 创建服务
chatbot = PropertyChatbotService()

# 对话
result = chatbot.chat("我想查询物业费", session_id="user001")
print(result["message"])
```

#### 11.2.2 使用工单处理

```python
from scenarios import WorkOrderAIService

service = WorkOrderAIService()
result = service.process("业主报修：厨房水管漏水")
print(result["result"])
```

#### 11.2.3 使用知识库问答

```python
from scenarios import KnowledgeQAService

# 创建服务并添加知识
qa = KnowledgeQAService(knowledge_base=[
    "物业费标准：住宅2.5元/平米/月",
    "停车费标准：地面150元/月，地下300元/月"
])

# 问答
result = qa.query("物业费多少钱一平米？")
print(result["answer"])
```

#### 11.2.4 直接使用LLM

```python
from core import LLMFactory

# 创建客户端
llm = LLMFactory.create("deepseek", "deepseek-chat")

# 调用
response = llm.chat([
    {"role": "user", "content": "你好"}
])

print(response.content)
```

### 11.3 添加新的业务场景

1. 在 `scenarios/` 目录下创建新场景文件夹
2. 创建 `service.py` 实现业务逻辑
3. 创建 `prompt.py` 配置提示词
4. 在 `__init__.py` 中导出服务

示例:
```python
# scenarios/my_scenario/service.py
from services import ChatService

class MyScenarioService:
    def __init__(self):
        self.chat_service = ChatService(
            provider="deepseek",
            model="deepseek-chat",
            system_prompt="你的系统提示词"
        )

    def process(self, input_data: str):
        # 业务逻辑
        return self.chat_service.chat(input_data)
```

### 11.4 添加新的Provider

1. 在 `core/` 目录下创建新的Client类
2. 继承 `BaseLLMClient`
3. 实现 `chat` 和 `stream_chat` 方法
4. 在 `LLMFactory` 中注册

---

## 12. 部署指南

### 12.1 开发环境

```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env
python -m api.main
```

### 12.2 生产环境

```bash
# 使用gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app

# 或使用Docker
docker build -t ai-ysservice .
docker run -d -p 8000:8000 --env-file .env ai-ysservice
```

### 12.3 环境变量配置

| 变量 | 说明 | 示例 |
|------|------|------|
| `APP_ENV` | 运行环境 | development/staging/production |
| `LOG_LEVEL` | 日志级别 | DEBUG/INFO/WARNING/ERROR |
| `*_API_KEY` | 各Provider的API Key | sk-xxx |

---

*文档版本: v1.1*
*创建时间: 2026-02-18*
