# Setup Guide

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | `uv python install 3.11` |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker | 24+ | `docker --version` |
| Git | any | `git --version` |

## Step-by-Step Local Setup

### 1. Clone & Enter

```bash
git clone <repo-url>
cd rag-chatbot
```

### 2. Start Qdrant (Required)

```bash
docker run -d --name rag-qdrant -p 6333:6333 qdrant/qdrant
```

Verify:
```bash
curl http://localhost:6333/collections
# {"result":{"collections":[]},"status":"ok","time":...}
```

### 3. Install Dependencies

```bash
cd backend
uv sync --extra dev
```

### 4. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your API keys (or configure via UI)
```

Required API keys:
- **Groq**: Get at https://console.groq.com/keys (free tier: 14,400 req/day)
- **Cohere**: Get at https://dashboard.cohere.com/api-keys (free trial)

### 5. Start Server

```bash
# From project root
./backend/run.sh
# Or manually:
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Open UI

```
http://localhost:8000
```

## One-Command Startup

```bash
./backend/run.sh
```

This script:
1. Checks Qdrant is running (starts container if not)
2. Runs `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
3. Watches `app/` and `static/` for changes

---

## Environment Variables

Create `backend/.env` from `backend/.env.example`:

```bash
# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=rag_chatbot_cohere

# Storage
SQLITE_PATH=./data/chatbot.db
UPLOAD_DIR=./uploads

# Logging
LOG_LEVEL=INFO

# LLM (Groq)
GROQ_API_KEY=gsk_xxx
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.1-8b-instant

# Embeddings (Cohere)
COHERE_API_KEY=sk-xxx
COHERE_MODEL=embed-english-v3.0

# Chunking
CHUNK_SIZE=800
CHUNK_OVERLAP=100
MAX_CHUNKS_PER_DOC=2000
```

### Getting API Keys

| Provider | URL | Free Tier |
|----------|-----|-----------|
| Groq | https://console.groq.com/keys | 14,400 req/day |
| Cohere | https://dashboard.cohere.com/api-keys | Free trial |

---

## Running Tests

```bash
cd backend
uv run pytest -q
# 98 passed, 2 warnings
```

### Test Categories

| Command | Runs |
|---------|------|
| `uv run pytest tests/unit/ -q` | Unit tests only |
| `uv run pytest tests/api/ -q` | API integration tests |
| `uv run pytest tests/ -k "not live" -q` | Skip live API tests |

### Test Structure

```
tests/
├── unit/
│   ├── test_chunker.py
│   ├── test_config.py
│   ├── test_generator.py
│   ├── test_llm_base.py
│   ├── test_llm_groq.py
│   ├── test_llm_opencode_zen.py
│   ├── test_parser.py
│   ├── test_query_rewriter.py
│   ├── test_retriever.py
│   ├── test_storage.py
│   └── test_vectorstore.py
├── api/
│   ├── test_documents.py
│   ├── test_provider.py
│   ├── test_query.py
│   └── test_health.py
└── conftest.py
```

---

## Verifying the App Works

### Health Check

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok"}
```

### Configure Providers via API

```bash
# LLM (Groq)
curl -X POST http://localhost:8000/api/v1/provider/config \
  -H "Content-Type: application/json" \
  -d '{"name":"Groq","base_url":"https://api.groq.com/openai/v1","api_key":"gsk_xxx","model":"llama-3.1-8b-instant"}'

# Embeddings (Cohere)
curl -X POST http://localhost:8000/api/v1/provider/config \
  -H "Content-Type: application/json" \
  -b "rag_session=<cookie>" \
  -d '{"cohere_api_key":"sk-xxx"}'
```

### Upload Document

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -b "rag_session=<cookie>" \
  -F "file=@document.pdf"
# {"id":"doc_xxx","filename":"document.pdf","status":"UPLOADED"}
```

### Check Document Status

```bash
curl -b "rag_session=<cookie>" http://localhost:8000/api/v1/documents/<doc_id>
# {"id":"doc_xxx","filename":"doc.pdf","status":"READY","chunk_count":13}
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -b "rag_session=<cookie>" \
  -d '{"question":"What is the license?"}'
# {"answer":"MIT [1]","citations":[...],"abstained":false}
```

---

## Project Structure Quick Reference

```
backend/
├── app/
│   ├── api/           # FastAPI routes
│   ├── embeddings/    # Cohere adapter
│   ├── llm/           # Groq + OpenCode Zen adapters
│   ├── rag/           # RAG pipeline
│   ├── storage.py     # SQLite
│   ├── exceptions.py  # Custom errors
│   ├── logging.py     # Structured logging
│   ├── config.py      # Pydantic Settings
│   └── main.py        # FastAPI app
├── static/
│   └── index.html     # Frontend
├── tests/
├── uploads/           # gitignored
├── data/              # gitignored
├── run.sh
├── pyproject.toml
└── uv.lock
```

---

## Common Setup Issues

| Issue | Solution |
|-------|----------|
| `uv: command not found` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| `python3.11 not found` | `uv python install 3.11` |
| Qdrant connection refused | `docker start rag-qdrant` or `docker run -d -p 6333:6333 qdrant/qdrant` |
| Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| `uv sync` fails | `uv cache clean && uv sync --extra dev` |
| Tests fail with async errors | `uv sync --extra dev` (installs pytest-asyncio) |

---

## Next Steps

1. [Read ARCHITECTURE.md](ARCHITECTURE.md) for codebase structure
2. [Read API.md](API.md) for endpoint reference
3. [Read FLOW.md](FLOW.md) for data flow diagrams
4. [Read TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues