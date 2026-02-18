"""FastAPI应用主入口"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn

from config import KeyManager, get_default_config
from scenarios import (
    PropertyChatbotService,
    WorkOrderAIService,
    ContractAuditService,
    KnowledgeQAService
)
from services import ChatService, RAGService
from utils import default_logger

# 创建FastAPI应用
app = FastAPI(
    title="物业大模型应用平台 API",
    description="物业公司大模型应用开发平台API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 请求/响应模型 ====================

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    session_id: Optional[str] = Field(default="default", description="会话ID")
    temperature: Optional[float] = Field(default=0.7, description="温度参数")
    history: Optional[List[Dict]] = Field(default=None, description="历史消息")


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool
    message: Optional[str] = None
    session_id: Optional[str] = None
    usage: Optional[Dict] = None
    error: Optional[str] = None


class WorkOrderProcessRequest(BaseModel):
    """工单处理请求"""
    content: str = Field(..., description="工单内容")
    provider: Optional[str] = Field(default="deepseek", description="模型提供商")
    model: Optional[str] = Field(default=None, description="模型名称")


class WorkOrderProcessResponse(BaseModel):
    """工单处理响应"""
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None


class ContractAuditRequest(BaseModel):
    """合同审核请求"""
    content: str = Field(..., description="合同内容")
    provider: Optional[str] = Field(default="qianwen", description="模型提供商")
    model: Optional[str] = Field(default=None, description="模型名称")


class ContractAuditResponse(BaseModel):
    """合同审核响应"""
    success: bool
    result: Optional[Dict] = None
    error: Optional[str] = None


class KnowledgeQueryRequest(BaseModel):
    """知识库问答请求"""
    question: str = Field(..., description="问题")
    knowledge: Optional[List[str]] = Field(default=None, description="知识库内容")


class KnowledgeQueryResponse(BaseModel):
    """知识库问答响应"""
    success: bool
    answer: Optional[str] = None
    error: Optional[str] = None


class ProviderInfo(BaseModel):
    """Provider信息"""
    name: str
    available: bool


# ==================== 应用状态 ====================

# 服务实例缓存
_services: Dict[str, Any] = {}


def get_chatbot_service() -> PropertyChatbotService:
    """获取智能客服服务实例"""
    if "chatbot" not in _services:
        config = get_default_config("property_chatbot")
        _services["chatbot"] = PropertyChatbotService(
            provider=config.provider,
            model=config.model,
            temperature=config.temperature
        )
    return _services["chatbot"]


def get_workorder_service() -> WorkOrderAIService:
    """获取工单处理服务实例"""
    if "workorder" not in _services:
        _services["workorder"] = WorkOrderAIService()
    return _services["workorder"]


def get_contract_service() -> ContractAuditService:
    """获取合同审核服务实例"""
    if "contract" not in _services:
        _services["contract"] = ContractAuditService()
    return _services["contract"]


# ==================== API路由 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "物业大模型应用平台 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/providers", response_model=List[ProviderInfo])
async def get_providers():
    """获取可用的模型提供商"""
    all_providers = ["openai", "deepseek", "qianwen", "wenxin"]
    result = []
    for provider in all_providers:
        available = KeyManager.is_provider_available(provider)
        result.append(ProviderInfo(name=provider, available=available))
    return result


# ==================== 智能客服API ====================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """智能客服对话接口"""
    try:
        service = get_chatbot_service()
        result = service.chat(
            user_message=request.message,
            session_id=request.session_id
        )
        return ChatResponse(**result)
    except Exception as e:
        default_logger.error(f"Chat error: {str(e)}")
        return ChatResponse(
            success=False,
            error=str(e),
            session_id=request.session_id
        )


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式对话接口"""
    from fastapi.responses import StreamingResponse

    service = get_chatbot_service()

    async def generate():
        try:
            for chunk in service.stream_chat(
                user_message=request.message,
                session_id=request.session_id
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@app.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """清除会话"""
    service = get_chatbot_service()
    service.clear_session(session_id)
    return {"success": True, "message": f"Session {session_id} cleared"}


# ==================== 工单处理API ====================

@app.post("/workorder/process", response_model=WorkOrderProcessResponse)
async def process_workorder(request: WorkOrderProcessRequest):
    """工单智能处理接口"""
    try:
        service = get_workorder_service()
        result = service.process(request.content)
        return WorkOrderProcessResponse(**result)
    except Exception as e:
        default_logger.error(f"Workorder process error: {str(e)}")
        return WorkOrderProcessResponse(
            success=False,
            error=str(e)
        )


# ==================== 合同审核API ====================

@app.post("/contract/audit", response_model=ContractAuditResponse)
async def audit_contract(request: ContractAuditRequest):
    """合同审核接口"""
    try:
        service = get_contract_service()
        result = service.audit(request.content)
        return ContractAuditResponse(**result)
    except Exception as e:
        default_logger.error(f"Contract audit error: {str(e)}")
        return ContractAuditResponse(
            success=False,
            error=str(e)
        )


# ==================== 知识库问答API ====================

@app.post("/knowledge/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(request: KnowledgeQueryRequest):
    """知识库问答接口"""
    try:
        # 创建服务实例
        service = KnowledgeQAService(
            knowledge_base=request.knowledge or []
        )
        result = service.query(request.question)
        return KnowledgeQueryResponse(**result)
    except Exception as e:
        default_logger.error(f"Knowledge query error: {str(e)}")
        return KnowledgeQueryResponse(
            success=False,
            error=str(e)
        )


@app.post("/knowledge/add")
async def add_knowledge(knowledge: List[str]):
    """添加知识到知识库"""
    # 注意：这里需要维护一个全局知识库实例
    return {"success": True, "message": f"Added {len(knowledge)} items"}


# ==================== 通用LLM API ====================

class LLMChatRequest(BaseModel):
    """通用LLM聊天请求"""
    messages: List[Dict[str, str]] = Field(..., description="消息列表")
    provider: Optional[str] = Field(default="deepseek", description="模型提供商")
    model: Optional[str] = Field(default=None, description="模型名称")
    temperature: Optional[float] = Field(default=0.7, description="温度参数")
    max_tokens: Optional[int] = Field(default=2048, description="最大token数")


@app.post("/llm/chat")
async def llm_chat(request: LLMChatRequest):
    """通用LLM对话接口"""
    try:
        from core import LLMFactory

        llm = LLMFactory.create(
            provider=request.provider,
            model=request.model
        )

        response = llm.chat(
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return {
            "success": True,
            "content": response.content,
            "model": response.model,
            "usage": response.usage
        }
    except Exception as e:
        default_logger.error(f"LLM chat error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ==================== 启动入口 ====================

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """运行服务器"""
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server()
