# RAG Chatbot

Local-first RAG chatbot with two providers:
- Groq for LLM (answers)
- Cohere for embeddings (vector search)

## What it does
Upload documents → ask questions → get answers with citations from your docs.

## Stack
- Backend: FastAPI + Python 3.11+
- Vector DB: Qdrant (Docker)
- Metadata: SQLite
- Embeddings: Cohere embed-english-v3.0 (1024-dim, cloud)
- LLM: Groq (llama-3.1-8b-instant and others)
- Frontend: plain HTML/CSS/JS (served by FastAPI)

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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | Health check |
| GET | /api/v1/documents | List documents |
| POST | /api/v1/documents/upload | Upload file (multipart) |
| GET | /api/v1/documents/{id} | Get document status |
| DELETE | /api/v1/documents/{id} | Delete document |
| POST | /api/v1/query | Ask question |
| POST | /api/v1/provider/models | List models for provider |
| POST | /api/v1/provider/test | Test LLM connection |
| POST | /api/v1/provider/test/cohere | Test Cohere connection |
| POST | /api/v1/provider/config | Save provider config |

## Configuration

Environment variables (optional, in `.env`):

```
QDRANT_URL=http://localhost:6333
SQLITE_PATH=./data/chatbot.db
UPLOAD_DIR=./uploads
MAX_UPLOAD_MB=2048
MAX_CHUNKS_PER_DOC=1000
CHUNK_SIZE=1500
CHUNK_OVERLAP=150
LOG_LEVEL=INFO
```

## Project Structure

```
rag-chatbot/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI routes
│   │   ├── embeddings/    # Cohere embedding provider
│   │   ├── llm/           # Groq + OpenCode Zen providers
│   │   ├── rag/           # Parser, chunker, retriever, generator
│   │   └── storage.py     # SQLite operations
│   ├── static/index.html  # Frontend (single file)
│   ├── run.sh             # Start Qdrant + uvicorn
│   └── pyproject.toml
├── .gitignore
└── README.md
```

## Tests

```bash
cd backend
uv run pytest -q
# 98 tests pass
```

## Performance

- Cohere cloud embeddings: ~30 chunks/second
- 302 chunks in ~10 seconds (vs 10+ minutes with local fastembed)
- Upload → READY in seconds for typical docs

## License

MIT