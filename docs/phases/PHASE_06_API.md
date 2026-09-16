# Phase 06 — API

## Goal
Wire all endpoints: auth, documents, query, chats. Combine the RAG pipeline, storage, and LLM adapters into request handlers.

## Files to create or modify
- `backend/app/api/__init__.py` — Package init
- `backend/app/api/auth.py` — `/api/v1/auth/*` endpoints
- `backend/app/api/documents.py` — `/api/v1/documents/*` endpoints
- `backend/app/api/query.py` — `/api/v1/query` endpoint
- `backend/app/api/chats.py` — `/api/v1/chats/*` endpoints
- `backend/app/main.py` — Update to include routers
- `backend/tests/api/test_auth.py` — Auth endpoint tests
- `backend/tests/api/test_documents.py` — Document endpoint tests
- `backend/tests/api/test_query.py` — Query endpoint tests
- `backend/tests/api/test_chats.py` — Chat endpoint tests

## Interfaces to define

### `backend/app/api/auth.py`
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/models")
async def get_models(request: AuthRequest) -> ModelsResponse:
    """Validate API key and return available models."""
    ...
```

### `backend/app/api/documents.py`
```python
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

@router.post("/upload", status_code=201)
async def upload_document(file: UploadFile) -> DocumentResponse:
    """Upload a file for ingestion."""
    ...

@router.get("")
async def list_documents() -> DocumentsListResponse:
    """List all documents."""
    ...

@router.delete("/{id}", status_code=204)
async def delete_document(id: str) -> None:
    """Delete a document."""
    ...

@router.get("/{id}/chunks/{chunk_id}")
async def get_chunk(id: str, chunk_id: str) -> ChunkResponse:
    """Get full chunk text + metadata."""
    ...
```

### `backend/app/api/query.py`
```python
router = APIRouter(prefix="/api/v1", tags=["query"])

@router.post("/query")
async def query(request: QueryRequest) -> QueryResponse:
    """Answer a question using document context."""
    ...
```

### `backend/app/api/chats.py`
```python
router = APIRouter(prefix="/api/v1/chats", tags=["chats"])

@router.get("")
async def list_chats() -> ChatsListResponse:
    """List all chats."""
    ...

@router.post("", status_code=201)
async def create_chat(request: CreateChatRequest) -> ChatResponse:
    """Create a new chat."""
    ...

@router.get("/{id}/messages")
async def get_messages(id: str) -> MessagesResponse:
    """Get messages for a chat."""
    ...

@router.delete("/{id}", status_code=204)
async def delete_chat(id: str) -> None:
    """Delete a chat and its messages."""
    ...
```

## Tests required
- `backend/tests/api/test_auth.py`
  - Test: POST /api/v1/auth/models with valid key returns model list
  - Test: POST /api/v1/auth/models with invalid key returns 401
- `backend/tests/api/test_documents.py`
  - Test: POST /api/v1/documents/upload returns 201 with document id
  - Test: GET /api/v1/documents returns list
  - Test: DELETE /api/v1/documents/{id} returns 204
  - Test: GET /api/v1/documents/{id}/chunks/{chunk_id} returns chunk
- `backend/tests/api/test_query.py`
  - Test: POST /api/v1/query returns answer + citations
  - Test: POST /api/v1/query with no documents returns error
- `backend/tests/api/test_chats.py`
  - Test: GET /api/v1/chats returns list
  - Test: POST /api/v1/chats returns 201
  - Test: GET /api/v1/chats/{id}/messages returns messages
  - Test: DELETE /api/v1/chats/{id} returns 204

## Manual verification
```bash
# Health
curl -s http://localhost:8000/api/v1/health

# Auth
curl -s -X POST http://localhost:8000/api/v1/auth/models \
  -H 'Content-Type: application/json' \
  -d '{"provider":"groq","api_key":"..."}'

# Documents
curl -s http://localhost:8000/api/v1/documents

# Chats
curl -s http://localhost:8000/api/v1/chats

# Query
curl -s -X POST http://localhost:8000/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"chat_id":"...","question":"...","provider":"groq","api_key":"...","model":"..."}'
```

## Definition of Done
- [ ] All routers wired into FastAPI app
- [ ] Auth endpoint validates key and returns models
- [ ] Document endpoints handle upload, list, delete, chunk inspection
- [ ] Query endpoint orchestrates RAG pipeline
- [ ] Chat endpoints handle list, create, messages, delete
- [ ] All API tests pass

## Evidence to record
- Paste curl output in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: which endpoint fails, which request/response shape is wrong
- Report to: human

## Do NOT
- Do not create frontend files yet
- Do not add streaming
- Do not add OAuth or password auth
