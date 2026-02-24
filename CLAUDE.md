# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **物业大模型应用开发平台** (Property LLM Application Development Platform) - a Python FastAPI-based service that provides LLM capabilities for property management scenarios including intelligent customer service, work order processing, contract auditing, and knowledge base Q&A.

## Common Commands

### Development Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### Run the API Server
```bash
# Method 1: Using the startup script (recommended)
python scripts/run_api.py

# Method 2: Direct module execution
python -m api.main

# Method 3: Using uvicorn directly
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing and Code Quality
```bash
# Run all tests
pytest tests/

# Run a single test file
pytest tests/unit/test_specific.py

# Code formatting
black .

# Linting
ruff check .
```

### Example Usage
```bash
# Run example script
python scripts/example.py
```

## Architecture Overview

### Layered Architecture
The codebase follows a layered architecture pattern:

1. **API Layer** (`api/`): FastAPI routes, request/response models, CORS middleware. Entry point is `api/main.py`.

2. **Core Layer** (`core/`): LLM client abstractions and provider implementations. Uses **factory pattern** - `LLMFactory.create(provider, model)` instantiates the appropriate client (OpenAI, DeepSeek, Qianwen, Wenxin).

3. **Service Layer** (`services/`): Business logic services (`chat_service.py`, `embedding_service.py`, `rag_service.py`) that orchestrate LLM calls.

4. **Scenario Layer** (`scenarios/`): Domain-specific implementations for property management business scenarios. Each scenario (property_chatbot, work_order_ai, contract_audit, knowledge_qa) contains its own prompts, chains, and service logic.

5. **Tool Layer** (`tools/`): Reusable utilities organized by purpose - text processing, file handling, HTTP requests, date/time, security, property-specific tools, and LLM-specific tools.

### Key Management Architecture
The system supports dual-mode key management (see `config/key_config.py` and `config/cloud_key_manager.py`):

- **Local mode** (`USE_CLOUD_KEY=0`): API keys loaded from `.env` file via environment variables.
- **Cloud mode** (`USE_CLOUD_KEY=1`): API keys fetched from Alibaba Cloud KMS with 60-second local caching and automatic fallback to environment variables if KMS is unavailable.

KMS secret names are mapped via `KMS_SECRET_NAMES` env var in format: `provider:SecretName,provider2:SecretName2`

### LLM Client Factory Pattern
All LLM clients inherit from `BaseLLMClient` (in `core/base.py`) and implement:
- `chat(messages, **kwargs)` → returns `LLMResponse`
- `stream_chat(messages, **kwargs)` → yields text chunks

Providers are registered with `LLMFactory` in their respective client files. Supported providers: openai, deepseek, qianwen, wenxin.

### Configuration Hierarchy
- `config/app_config.py`: Application settings (environment, debug mode, logging)
- `config/model_config.py`: LLM model parameters and defaults
- `config/key_config.py`: API key management (local/cloud)
- `.env`: Environment variables (not committed)

### Important File Locations
- API routes: `api/main.py`
- LLM factory: `core/llm_client.py`
- Base LLM client: `core/base.py`
- Key management: `config/key_config.py`, `config/cloud_key_manager.py`
- Scenario base class: `scenarios/base.py`
- Tool base class: `tools/base_tool.py`

### API Endpoints
Service runs on port 8000. Key endpoints:
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `POST /chat` - Intelligent customer service
- `POST /workorder/process` - Work order processing
- `POST /contract/audit` - Contract auditing
- `POST /knowledge/query` - Knowledge base Q&A
- `POST /llm/chat` - Generic LLM chat

### Dependencies
Key dependencies in `requirements.txt`:
- FastAPI + Uvicorn for web framework
- openai, dashscope (Qianwen) for LLM providers
- chromadb for vector storage
- pytest, black, ruff for dev tools
