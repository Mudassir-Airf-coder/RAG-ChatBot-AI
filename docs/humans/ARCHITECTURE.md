# Architecture

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                             │
│  backend/static/index.html (HTML/CSS/JS, vanilla)          │
├─────────────────────────────────────────────────────────────┤
│                       API Layer                             │
│  FastAPI routers: provider, documents, query, chats, health│
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                        │
│  Services: Ingestion pipeline, Query orchestration,        │
│  Chat persistence, Provider config                          │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                           │
│  RAG Core: Parser, Chunker, Retriever, Generator,          │
│  Query Rewriter, Intent Classifier                          │
├─────────────────────────────────────────────────────────────┤
│                    Adapter Layer                            │
│  LLM: GroqProvider, OpenCodeZenProvider                    │
│  Embeddings: CohereEmbeddingProvider                       │
│  Vector DB: QdrantClient wrapper                            │
│  Storage: SQLite (chatbot.db)                               │
└─────────────────────────────────────────────────────────────┘
```

## Folder Structure

```
project_01/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers
│   │   │   ├── documents.py    # Upload, list, get, delete
│   │   │   ├── provider.py     # Provider config, test, models
│   │   │   ├── query.py        # Query endpoint + rewrite
│   │   │   ├── chats.py        # Chat history endpoints
│   │   │   └── health.py       # Health check
│   │   ├── embeddings/         # Embedding adapters
│   │   │   ├── base.py           # Abstract EmbeddingProvider
│   │   │   ├── cohere_cloud.py   # Cohere cloud implementation
│   │   │   └── __init__.py
│   │   ├── llm/                # LLM adapters
│   │   │   ├── base.py           # Abstract LLMProvider
│   │   │   ├── groq.py           # Groq implementation
│   │   │   ├── opencode_zen.py   # OpenCode Zen implementation
│   │   │   └── __init__.py       # get_provider() factory
│   │   ├── rag/                # RAG pipeline
│   │   │   ├── parser.py         # File → text extraction
│   │   │   ├── chunker.py        # Text → overlapping chunks
│   │   │   ├── retriever.py      # Vector search
│   │   │   ├── generator.py      # LLM answer generation
│   │   │   ├── query_rewriter.py # Query rewriting + intent
│   │   │   ├── vectorstore.py    # Qdrant client wrapper
│   │   │   └── intent.py         # Intent classification
│   │   ├── storage.py          # SQLite operations
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── logging.py          # Structured logging
│   │   ├── config.py           # Pydantic Settings
│   │   └── main.py             # FastAPI app + lifespan
│   ├── static/
│   │   └── index.html          # Single-file frontend
│   ├── tests/                  # Unit + API tests
│   ├── uploads/                # Runtime file storage (gitignored)
│   ├── data/                   # SQLite + sessions (gitignored)
│   ├── run.sh                  # One-command startup
│   ├── pyproject.toml
│   └── uv.lock
├── docs/
│   ├── agents/
│   └── humans/
├── .github/workflows/
├── .gitignore
├── README.md
├── LICENSE
└── .env.example
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Cohere for embeddings** | Cloud API, 1024-dim, high quality, generous free tier; no local model download |
| **Groq for LLM** | Fast inference, generous free tier, OpenAI-compatible API |
| **Qdrant (Docker)** | Local vector DB, HNSW index, filtering, REST + gRPC |
| **SQLite for metadata** | Zero-config, file-based, sufficient for single-user |
| **No streaming LLM** | Simpler implementation; Groq supports streaming but adds complexity |
| **Cohere cloud only** | No local embedding model (fastembed removed); avoids 66MB model download |
| **Session cookie + localStorage** | HttpOnly cookie for server session; localStorage for client state |
| **Single-file frontend** | Zero build step, easy to modify, no build tooling |
| **Background ingestion** | 202 Accepted + semaphore prevents Cohere 429 / Qdrant overload |
| **Cohere-only embeddings** | Removed fastembed; 1024-dim vectors only |

---

## Layer Boundaries & Rules

| Layer | Can Import From | Cannot Import From |
|-------|-----------------|-------------------|
| API | Application, Domain, Adapter | — |
| Application | Domain, Adapter | API |
| Domain | Adapter | Application, API |
| Adapter | (stdlib, 3rd party) | Domain, Application, API |

### Enforced by Code Structure

- API routers import from `app.rag.*`, `app.llm.*`, `app.embeddings.*`, `app.storage`
- Domain (`app.rag.*`) imports only from `app.llm.base`, `app.embeddings.base`, `app.exceptions`
- Adapters (`app.llm.*`, `app.embeddings.*`) import only stdlib/3rd-party

---

## Key Files & Responsibilities

### API Routes (`app/api/`)

| File | Responsibility |
|------|----------------|
| `documents.py` | Upload (202), list, get, delete; background ingestion |
| `provider.py` | Config CRUD, model fetch, connection test, session cookie |
| `query.py` | Intent → rewrite → retrieve → generate → citations |
| `chats.py` | Chat CRUD (if implemented) |
| `health.py` | `GET /health` → `{"status":"ok"}` |

### RAG Pipeline (`app/rag/`)

| File | Responsibility |
|------|----------------|
| `parser.py` | `parse_file()` → PDF/MD/TXT/DOCX → `[{text, metadata}]` |
| `chunker.py` | `chunk_text(text, 800, 100)` → `[{index, text}]` |
| `retriever.py` | `retrieve(query, top_k, embedder)` → `chunks[]` |
| `generator.py` | Per-intent prompts → LLM → answer + citations |
| `query_rewriter.py` | Intent-aware rewrite with typo fixing |
| `vectorstore.py` | Qdrant client + `upsert_chunks`, `delete_by_document_id` |
| `intent.py` | `classify_intent()` → `Intent` dataclass |

### LLM Adapters (`app/llm/`)

| File | Responsibility |
|------|----------------|
| `base.py` | Abstract `LLMProvider` with `chat()`, `get_models()` |
| `groq.py` | `GroqProvider` — OpenAI-compatible API |
| `opencode_zen.py` | `OpenCodeZenProvider` — OpenCode Zen endpoint |
| `__init__.py` | `get_provider(url, key)` factory |

### Embeddings (`app/embeddings/`)

| File | Responsibility |
|------|----------------|
| `base.py` | Abstract `EmbeddingProvider` |
| `cohere_cloud.py` | `CohereEmbeddingProvider` — 1024-dim, batch 96 |
| `__init__.py` | Exports |

### Storage (`app/storage.py`)

- SQLite operations: documents, chats, messages
- `init_db()` creates tables
- All functions accept `sqlite_path` for test isolation

### Exceptions (`app/exceptions.py`)

| Exception | Code | Status |
|-----------|------|--------|
| `ValidationError` | `VALIDATION_ERROR` | 400 |
| `NotFoundError` | `NOT_FOUND` | 404 |
| `ProviderError` | `PROVIDER_ERROR` | 502 |
| `StorageError` | `STORAGE_ERROR` | 500 |
| `ParsingError` | `PARSING_ERROR` | 400 |
| `VectorDBError` | `VECTOR_DB_ERROR` | 500 |

---

## Configuration (`app/config.py`)

```python
class Settings(BaseSettings):
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "rag_chatbot"
    sqlite_path: str = "./data/chatbot.db"
    upload_dir: str = "./uploads"
    groq_base_url: str = "https://api.groq.com/openai/v1"
    opencode_zen_base_url: str = "https://opencode.ai/zen/v1"
    max_upload_mb: int = 2048
    max_chunks_per_doc: int = 2000
    chunk_size: int = 800
    chunk_overlap: int = 100
    retrieval_top_k: int = 10
    max_context_chunks: int = 6
    max_tokens_concise: int = 400
    max_tokens_verbose: int = 1500
    default_temperature: float = 0.2
    log_level: str = "INFO"
```

### Environment Variables (`.env`)

```bash
QDRANT_URL=http://localhost:6333
SQLITE_PATH=./data/chatbot.db
UPLOAD_DIR=./uploads
GROQ_API_KEY=
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.1-8b-instant
COHERE_API_KEY=
COHERE_MODEL=embed-english-v3.0
MAX_UPLOAD_MB=2048
MAX_CHUNKS_PER_DOC=2000
CHUNK_SIZE=800
CHUNK_OVERLAP=100
RETRIEVAL_TOP_K=10
MAX_CONTEXT_CHUNKS=6
```

---

## Key Abstractions

### Provider Factory (`app/llm/__init__.py`)

```python
def get_provider(base_url: str, api_key: str) -> LLMProvider:
    if "opencode.ai" in base_url:
        return OpenCodeZenProvider(api_key)
    return GroqProvider(api_key)
```

### Embedding Provider Interface

```python
class EmbeddingProvider(ABC):
    @property
    def dimension(self) -> int: ...
    @property
    def collection_name(self) -> str: ...
    def embed_chunks(self, texts: list[str]) -> list[ndarray]: ...
    def embed_query(self, text: str) -> ndarray: ...
```

### LLM Provider Interface

```python
class LLMProvider(ABC):
    async def chat(self, model: str, messages: list[dict], **kwargs) -> str: ...
    async def get_models(self) -> list[str]: ...
```

### Session Config (Server-Side)

```python
# In-memory dict + JSON file persistence
sessions: dict[str, dict] = _load_sessions()

def get_session_config(req: Request) -> dict | None:
    session_id = req.cookies.get("rag_session")
    return sessions.get(session_id)
```

---

## Data Flow Summary

```
Upload
  ├─ Stream to disk (1MB chunks)
  ├─ Parse (fitz/docx/markdown/text)
  ├─ Chunk (800/100, global index)
  ├─ Embed (Cohere batch 96, 1024-dim)
  ├─ Qdrant upsert (deterministic UUID5)
  └─ SQLite: status=READY

Query
  ├─ Classify intent
  ├─ Rewrite (if vague)
  ├─ Retrieve top-K (10-15)
  ├─ Trim to max_context_chunks (6)
  ├─ Generate (intent-specific prompt)
  ├─ Extract used citations [N]
  └─ Return answer + citations

Chat
  ├─ localStorage: rag.chats.v1, rag.active_chat.v1
  ├─ rag.messages.{chat_id} per conversation
  └─ Provider config in localStorage + HttpOnly cookie
```

---

## Testing Architecture

- **Unit tests**: `tests/unit/` — pure functions, mocked dependencies
- **API tests**: `tests/api/` — FastAPI TestClient, mocked providers
- **Conftest**: Shared `TestClient` fixture
- **98 tests** passing (unit + API)

---

## Deployment Topology (Local)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Browser    │────▶│  FastAPI    │────▶│   Qdrant    │
│  (localhost)│     │  :8000      │     │  :6333      │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              ┌───────────┐ ┌───────────┐
              │  Cohere   │ │   Groq    │
              │ (embeddings)│  (LLM)    │
              └───────────┘ └───────────┘
```

All external calls are HTTPS. Local Qdrant is HTTP on localhost.