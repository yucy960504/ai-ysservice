# 物业大模型应用开发平台

物业行业大模型应用开发基础平台，支持多模型接入、工具封装、业务场景开发、统一API服务、云端Key管理。

## 功能特性

- **多模型支持**：OpenAI、DeepSeek、通义千问、文心一言
- **统一API封装**：工厂模式，灵活切换模型
- **物业业务场景**：智能客服、工单处理、合同审核、知识库问答
- **完整工具类**：文本处理、文件处理、日期时间、安全工具等
- **RESTful API**：FastAPI实现，完整接口文档
- **Key安全管理**：支持本地环境变量和阿里云KMS云端管理
- **云端Key管理**：每次请求从KMS获取，自动降级

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

#### 方式一：本地模式（仅本地开发使用）

编辑 `.env`，填入您的API Key：

```bash
# 关闭云端模式（默认）
USE_CLOUD_KEY=0

# 配置API Key
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

#### 方式二：云端模式（生产环境推荐）

```bash
# 开启云端模式
USE_CLOUD_KEY=1

# 阿里云KMS配置
KMS_REGION_ID=cn-hangzhou
KMS_ACCESS_KEY_ID=your-access-key-id
KMS_ACCESS_KEY_SECRET=your-access-key-secret

# 密钥名称映射
KMS_SECRET_NAMES=deepseek:deepseek-api-key,qianwen:qianwen-api-key
```

### 3. 启动API服务

```bash
# 方式1: 使用启动脚本（推荐）
python scripts/run_api.py

# 方式2: 直接运行
python -m api.main

# 方式3: 使用uvicorn
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问API文档

服务启动后访问：
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 使用示例

### 代码调用

```python
# 智能客服
from scenarios import PropertyChatbotService
chatbot = PropertyChatbotService()
result = chatbot.chat("我想查询物业费怎么缴", session_id="user001")
print(result["message"])

# 工单处理
from scenarios import WorkOrderAIService
service = WorkOrderAIService()
result = service.process("业主报修：厨房水管漏水")

# 知识库问答
from scenarios import KnowledgeQAService
qa = KnowledgeQAService(knowledge_base=["物业费标准：2.5元/平米/月"])
result = qa.query("物业费多少钱？")

# 直接使用LLM
from core import LLMFactory
llm = LLMFactory.create("deepseek", "deepseek-chat")
response = llm.chat([{"role": "user", "content": "你好"}])
print(response.content)
```

### API调用

```bash
# 智能客服对话
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "我想查询物业费", "session_id": "user001"}'

# 工单处理
curl -X POST "http://localhost:8000/workorder/process" \
  -H "Content-Type: application/json" \
  -d '{"content": "业主报修：电梯故障"}'

# 合同审核
curl -X POST "http://localhost:8000/contract/audit" \
  -H "Content-Type: application/json" \
  -d '{"content": "合同内容..."}'
```

## 项目结构

```
ai-ysservice/
├── api/                     # API接口层
│   └── main.py             # FastAPI应用
├── config/                  # 配置文件
│   ├── key_config.py       # Key管理（支持本地/云端）
│   ├── cloud_key_manager.py # 阿里云KMS客户端
│   ├── model_config.py     # 模型配置
│   └── app_config.py       # 应用配置
├── core/                    # 核心模块
│   ├── llm_client.py       # 大模型客户端
│   ├── openai_client.py
│   ├── deepseek_client.py
│   └── qianwen_client.py
├── tools/                   # 工具类
│   ├── text_tools.py       # 文本处理
│   ├── http_tools.py       # HTTP请求
│   ├── file_tools.py       # 文件处理
│   ├── date_tools.py       # 日期时间
│   ├── security_tools.py   # 安全工具
│   ├── property_tools/     # 物业专用工具
│   └── llm_tools/          # 大模型工具
├── services/                # 业务服务层
│   ├── chat_service.py     # 对话服务
│   ├── embedding_service.py
│   └── rag_service.py      # RAG服务
├── scenarios/               # 业务场景
│   ├── property_chatbot/  # 智能客服
│   ├── work_order_ai/      # 工单处理
│   ├── contract_audit/     # 合同审核
│   └── knowledge_qa/       # 知识库问答
├── chain/                   # Chain链
├── utils/                   # 工具函数
├── tests/                   # 测试
├── scripts/                 # 脚本
│   ├── example.py          # 使用示例
│   └── run_api.py         # 启动API
├── prompts/                 # 提示词文件
├── logs/                    # 日志目录
├── requirements.txt         # 依赖
├── .env.example             # 环境变量示例
└── README.md               # 项目说明
```

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 根路径 |
| `/health` | GET | 健康检查 |
| `/providers` | GET | 可用模型列表 |
| `/chat` | POST | 智能客服对话 |
| `/chat/stream` | POST | 流式对话 |
| `/workorder/process` | POST | 工单处理 |
| `/contract/audit` | POST | 合同审核 |
| `/knowledge/query` | POST | 知识库问答 |
| `/llm/chat` | POST | 通用LLM对话 |

详细接口文档请访问 http://localhost:8000/docs

## 云端Key管理配置

### 阿里云KMS配置

1. 在阿里云KMS控制台创建普通密钥
2. 配置环境变量：

```bash
# 开启云端模式
USE_CLOUD_KEY=1

# KMS访问凭证
KMS_REGION_ID=cn-hangzhou
KMS_ACCESS_KEY_ID=LTAI5t**********
KMS_ACCESS_KEY_SECRET=your-secret

# 密钥名称映射（格式：provider:SecretName）
KMS_SECRET_NAMES=deepseek:deepseek-key,qianwen:qianwen-key
```

3. KMS密钥名称对应：
   - `deepseek-key` → DeepSeek API Key
   - `qianwen-key` → 通义千问 API Key
   - `openai-key` → OpenAI API Key

## 开发指南

详见 [AI_LLM_工程设计文档.md](AI_LLM_工程设计文档.md)

## License

MIT
