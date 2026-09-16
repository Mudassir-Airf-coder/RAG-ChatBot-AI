# Phase 01 — Foundation

## Goal
Set up the project skeleton: dependencies, FastAPI app, health endpoint, logging with redaction, structured exceptions, and Pydantic config.

## Files to create or modify
- `backend/pyproject.toml` — Project metadata and dependencies
- `backend/.env.example` — Example environment variables (no secrets)
- `backend/app/__init__.py` — Package init
- `backend/app/main.py` — FastAPI app with static mount and health endpoint
- `backend/app/config.py` — Pydantic Settings (Qdrant URL, SQLite path, upload dir)
- `backend/app/logging.py` — Structured JSON logger with API key redaction
- `backend/app/exceptions.py` — Structured error classes
- `backend/tests/conftest.py` — Shared fixtures

## Interfaces to define

### `backend/app/main.py`
```python
from fastapi import FastAPI

app = FastAPI(title="RAG Chatbot")

@app.get("/api/v1/health")
async def health() -> dict:
    ...
```

### `backend/app/config.py`
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "rag_chatbot"
    sqlite_path: str = "./data/chatbot.db"
    upload_dir: str = "./uploads"
```

### `backend/app/logging.py`
```python
import structlog

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    ...
```

### `backend/app/exceptions.py`
```python
class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 500):
        ...
```

## Tests required
- `backend/tests/unit/test_config.py`
  - Assert `Settings` loads defaults correctly
  - Assert env vars override defaults
- `backend/tests/unit/test_logging.py`
  - Assert API key is redacted in log output
  - Assert other fields are preserved
- `backend/tests/unit/test_exceptions.py`
  - Assert `AppError` produces correct JSON shape
  - Assert different status codes are correct

## Manual verification
```bash
curl http://localhost:8000/api/v1/health
```
Expected:
```json
{"status":"ok"}
```

## Definition of Done
- [ ] `pyproject.toml` created with correct dependencies
- [ ] `backend/.env.example` created with QDRANT_URL, QDRANT_COLLECTION, SQLITE_PATH, UPLOAD_DIR, LOG_LEVEL
- [ ] FastAPI app starts with `uvicorn app.main:app`
- [ ] `GET /api/v1/health` returns `{"status":"ok"}`
- [ ] Structured JSON logs are emitted
- [ ] API key redaction works
- [ ] All tests pass

## Evidence to record
- Paste curl output in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRacker.md` with DONE status

## If blocked
- Report: which dependency is missing or which config is wrong
- Report to: human

## Do NOT
- Do not implement RAG pipeline yet
- Do not create SQLite tables yet
- Do not create LLM adapters yet
- Do not create frontend files yet
