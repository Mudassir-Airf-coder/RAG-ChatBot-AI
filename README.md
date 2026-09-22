# RAG Chatbot

Local-first RAG chatbot with two providers:
- **Groq** for LLM (answers)
- **Cohere** for embeddings (vector search)

## What it does

Upload documents → ask questions → get answers with citations from your docs.

## Stack

- **Backend**: FastAPI + Python 3.11+
- **Vector DB**: Qdrant (Docker)
- **Metadata**: SQLite
- **Embeddings**: Cohere embed-english-v3.0 (1024-dim, cloud)
- **LLM**: Groq (llama-3.1-8b-instant and others)
- **Frontend**: plain HTML/CSS/JS (served by FastAPI)

## Requirements

- Python 3.11+
- uv
- Docker
- Groq API key (free): https://console.groq.com/keys
- Cohere API key (free trial): https://dashboard.cohere.com/api-keys

## Quick start

```bash
git clone <repo>
cd rag-chatbot
./run.sh
```

This starts Qdrant, runs the FastAPI server on http://localhost:8000, and opens the UI.

## Usage

1. Open http://localhost:8000 in browser
2. Click the gear icon (top right) to open provider panel
3. **LLM Provider** section:
   - Select Groq (or OpenCode Zen)
   - Enter your API key
   - Click "Fetch Models", select one, click "Test" → "Saved"
4. **Embedding Provider (Cohere)** section:
   - Enter your Cohere API key
   - Click "Test Connection" → "Saved"
5. Upload documents (PDF, TXT, MD, DOCX) via left panel
6. Wait for "READY" status
7. Ask questions in chat

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Upload    │────▶│  Parser      │────▶│  Chunker     │
│  (PDF/MD/   │     │  (pymupdf,   │     │  (800 chars,  │
│   TXT/DOCX) │     │   docx, OCR) │     │   100 overlap)│
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
┌─────────────┐     ┌──────────────┐     ┌──────▼───────┐
│   Query     │◀───│  Retriever   │◀───│  Cohere      │
│  (chat)     │     │  (Qdrant)    │     │  Embeddings  │
└──────┬──────┘     └──────────────┘     └──────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  Generator  │────▶│  Groq LLM    │
│  (citations)│     │  (answers)   │
└─────────────┘     └──────────────┘
```

### Key Features

- **Cohere-only embeddings**: No local fastembed — completely removed. Uses Cohere embed-english-v3.0 (1024-dim, batch 96)
- **Intent-aware retrieval**: 5 intent types (verbatim, teach, summarize, compare, knowledge) with per-intent prompts
- **Query rewriting**: Typo fixing, synonym expansion, question normalization
- **Background ingestion**: Async document processing with status tracking
- **Inline citations**: Clickable citation chips in answers linking to source chunks
- **Chat history**: Persistent sidebar with session-based storage
- **Two-section provider panel**: Separate LLM and Embedding provider configs

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/documents` | List documents |
| POST | `/api/v1/documents/upload` | Upload file (multipart) |
| GET | `/api/v1/documents/{id}` | Get document status |
| DELETE | `/api/v1/documents/{id}` | Delete document |
| POST | `/api/v1/query` | Ask question |
| POST | `/api/v1/provider/models` | List models for provider |
| POST | `/api/v1/provider/test` | Test LLM connection |
| POST | `/api/v1/provider/test/cohere` | Test Cohere connection |
| POST | `/api/v1/provider/config` | Save provider config |

### Example: Query Request

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```

### Example: Upload Document

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@document.pdf"
```

## Configuration

Environment variables (optional, in `.env`):

```bash
# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=rag_chatbot_cohere

# SQLite Storage
SQLITE_PATH=./data/chatbot.db
UPLOAD_DIR=./uploads

# LLM Providers
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
OPENCODE_ZEN_BASE_URL=https://api.opencode.ai/v1
OPENCODE_ZEN_API_KEY=sk_your_opencode_zen_api_key_here

# Embedding Provider (required)
COHERE_API_KEY=sk_your_cohere_api_key_here

# Document Processing
CHUNK_SIZE=800
CHUNK_OVERLAP=100
MAX_CHUNKS_PER_DOC=2000

# Retrieval
RETRIEVAL_TOP_K=10
MAX_CONTEXT_CHUNKS=6

# Logging
LOG_LEVEL=INFO
```

See `backend/.env.example` for template.

## Project Structure

```
rag-chatbot/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI routes
│   │   │   ├── documents.py    # Document CRUD + ingestion
│   │   │   ├── provider.py     # Provider config + session
│   │   │   └── query.py        # Query + intent + rewrite
│   │   ├── embeddings/
│   │   │   ├── __init__.py     # EmbeddingProvider ABC
│   │   │   ├── base.py         # Abstract base class
│   │   │   └── cohere_cloud.py # Cohere embed-english-v3.0
│   │   ├── llm/
│   │   │   ├── __init__.py     # get_provider factory
│   │   │   ├── base.py         # LLMProvider ABC
│   │   │   ├── groq.py         # Groq API client
│   │   │   └── opencode_zen.py # OpenCode Zen client
│   │   ├── rag/
│   │   │   ├── parser.py       # Multi-format parser + OCR
│   │   │   ├── chunker.py      # Text chunking (global index)
│   │   │   ├── retriever.py    # Vector search + scoring
│   │   │   ├── generator.py    # Per-intent prompts + citations
│   │   │   ├── query_rewriter.py # Intent-aware rewriting
│   │   │   ├── intent.py       # Intent classification (5 types)
│   │   │   ├── vectorstore.py  # Qdrant operations
│   │   │   └── storage.py      # SQLite metadata
│   │   ├── config.py           # Settings (pydantic)
│   │   ├── exceptions.py       # Error codes
│   │   ├── logging.py          # Structured logging
│   │   └── main.py             # FastAPI app + lifespan
│   ├── static/
│   │   └── index.html          # Frontend (single file)
│   ├── tests/
│   │   ├── unit/               # 13 unit test files
│   │   ├── api/                # 5 API test files
│   │   └── conftest.py         # TestClient fixture
│   ├── data/                   # SQLite DB (gitignored)
│   ├── uploads/                # Uploaded files (gitignored)
│   ├── run.sh                  # Start Qdrant + uvicorn
│   ├── pyproject.toml
│   └── .env.example
├── docs/
│   └── screenshots/            # UI screenshots
├── .gitignore
├── LICENSE                     # MIT
└── README.md
```

## Tests

```bash
cd backend
uv run pytest -q
# 98 passed, 2 warnings in ~2s
```

### Test Categories

| Category | Files | Tests | Coverage |
|----------|-------|-------|----------|
| Unit | 13 | 51 | Core logic, pure functions |
| API | 5 | 47 | Full request/response cycle |

### Running Tests

```bash
# All tests
uv run pytest -q

# Unit only
uv run pytest tests/unit/ -q

# API only
uv run pytest tests/api/ -q

# With coverage
uv run pytest --cov=app --cov-report=term-missing

# Specific file
uv run pytest tests/unit/test_chunker.py -v
```

### CI Pipeline

GitHub Actions (`.github/workflows/ci.yml`):
- Runs on push/PR to main/master
- Installs uv + Python 3.11
- Runs full test suite (98 tests)
- Checks formatting (ruff format)
- Runs linting (ruff check)
- Builds and tests Docker image on main branch

## Performance

| Metric | Value |
|--------|-------|
| Embedding speed (Cohere) | ~30 chunks/second |
| 302 chunks ingestion | ~10 seconds |
| Upload → READY (typical doc) | <5 seconds |
| Query latency (p95) | <2 seconds |

Compared to local fastembed: **100x faster** ingestion (10s vs 10+ min).

## Development

### Adding a New Provider

1. Create `app/llm/new_provider.py` implementing `LLMProvider` ABC
2. Register in `app/llm/__init__.py` factory
3. Add to frontend provider panel

### Adding a New Intent

1. Add to `Intent` enum in `app/rag/intent.py`
2. Add prompt in `app/rag/generator.py` PROMPTS dict
3. Add rewrite rule in `app/rag/query_rewriter.py`
4. Add tests

### Code Quality

```bash
cd backend
uv run ruff format .      # Format
uv run ruff check .       # Lint
uv run pytest -q          # Test
```

## License

MIT — see [LICENSE](LICENSE)