# Architecture — RAG Chatbot

## Diagram (ASCII)

```
Browser (plain HTML/CSS/JS)
  |
  |  POST /api/v1/query
  |  GET  /api/v1/auth/models
  |  POST /api/v1/documents/upload
  |  DELETE /api/v1/documents/{id}
  |  GET  /api/v1/documents/{id}/chunks/{chunk_id}
  v
FastAPI Backend (Pydantic v2)
  |
  | 1) Embed query (fastembed)
  | 2) Dense search in Qdrant
  | 3) Build context (top-K chunks)
  | 4) Call LLM provider (Groq or OpenCode Zen)
  | 5) Store chat + message history in SQLite
  |
  v
Storage / Services
  - Qdrant (Docker): document chunk vectors + payload
  - SQLite (file): documents, chats, messages
  - Disk: uploaded files (per document)
```

## Layer responsibilities

### Frontend (backend/app/static)
- `login.html` / `login.js`
  - Collect API key and provider selection
  - Fetch available models via `/api/v1/auth/models`
  - Redirect to `index.html` after successful connection
- `index.html` / `app.js`
  - Render chat UI (user vs assistant bubbles)
  - Call `/api/v1/query` for answers
  - Render citations beneath each assistant message
  - Allow document upload/list/delete in the sidebar
  - Allow history sidebar: new chat, load chat, delete chat
- No build step, no framework.

### Backend (backend/app)
- `main.py`
  - Create FastAPI app
  - Mount static files at `/`
- `config.py`
  - Pydantic settings (Qdrant URL, Qdrant collection name, SQLite path, upload dir)
- `logging.py`
  - Structured JSON logs with API-key redaction
- `exceptions.py`
  - Structured errors with stable error codes

Submodules:
- `llm/`
  - `base.py`: LLMProvider interface
  - `groq.py`: Groq chat completions adapter
  - `.py`: OpenCode Zen chat completions adapter
- `rag/`
  - `parser.py`: parse PDF/MD/TXT/DOCX into raw text with basic metadata
  - `chunker.py`: recursive chunking (500 chars, 50 overlap)
  - `embedder.py`: fastembed embeddings wrapper
  - `vectorstore.py`: Qdrant collection create/upsert/delete
  - `retriever.py`: dense retrieval (top-K) returning chunk IDs + payload
  - `generator.py`: grounded answer construction via LLM
- `storage.py`
  - SQLite tables: documents, chats, messages
- `api/`
  - `auth.py`: provider/model validation
  - `documents.py`: upload/list/delete + chunk inspection
  - `query.py`: embed → retrieve → generate → persist
  - `chats.py`: chat list/create/load/delete

### Storage
- Qdrant
  - Holds vectors per chunk and payload to map back to SQLite/disk metadata
- SQLite
  - Documents: upload metadata and status
  - Chats: per conversation
  - Messages: per chat, including citations metadata
- Disk
  - Uploaded files stored for chunk source inspection

## Data flow

### Upload (Flow 3)
1. Frontend posts file to `POST /api/v1/documents/upload`
2. Backend:
   - Parse file (`rag/parser.py`)
   - Chunk into 500 chars with 50 overlap (`rag/chunker.py`)
   - Embed each chunk (`rag/embedder.py`)
   - Upsert vectors + payload into Qdrant (`rag/vectorstore.py`)
   - Store document record in SQLite (`storage.py`)
   - Set status to `READY` or `FAILED`
3. Frontend polls/refreshes the list via documents endpoint (no background push in v1)

### Query (Flow 2)
1. Frontend posts user question and chat context to `POST /api/v1/query`
2. Backend:
   - Embed question (`rag/embedder.py`)
   - Dense search Qdrant for top-K chunks (`rag/retriever.py`)
   - Build context from returned chunks (`rag/generator.py`)
   - Call selected LLM provider with the prompt + context (`llm/`)
   - Persist message + citations to SQLite
3. Frontend renders answer and citations

### Delete (Flow 3)
1. Frontend posts to `DELETE /api/v1/documents/{id}`
2. Backend:
   - Delete vectors from Qdrant (by document id)
   - Delete document + related chat/message links in SQLite
   - Delete uploaded disk content for that document

### Source inspection (Flow 4)
1. Frontend calls `GET /api/v1/documents/{id}/chunks/{chunk_id}`
2. Backend returns full chunk text + metadata for modal display

## Folder/module mapping
- `backend/app/llm/`: provider adapters only; no RAG logic
- `backend/app/rag/`: parsing, chunking, embeddings, Qdrant operations, retrieval, context building, and LLM prompt assembly
- `backend/app/storage.py`: SQLite schema and CRUD helpers
- `backend/app/api/`: request/response wiring and orchestration across `rag/`, `storage.py`, and `llm/`
- `backend/app/static/`: plain frontend assets served at `/`
