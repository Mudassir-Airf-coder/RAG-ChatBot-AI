# Developer Setup — RAG Chatbot

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.11+ | https://www.python.org/downloads/ |
| uv | latest | `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker | latest | https://docs.docker.com/get-docker/ |

## Quick start

```bash
# 1. Clone the repo
git clone <repo-url>
cd rag-chatbot

# 2. Start Qdrant
docker compose up -d qdrant

# 3. Install dependencies
cd backend
uv sync

# 4. Create .env from example
cp .env.example .env

# 5. Start the backend
uv run uvicorn app.main:app --reload

# 6. Open browser
open http://localhost:8000
```

## .env.example

The `.env.example` file documents environment variables.

```
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=rag_chatbot
SQLITE_PATH=./data/chatbot.db
UPLOAD_DIR=./uploads
OPENCODE_ZEN_BASE_URL=
LOG_LEVEL=INFO
```

## How to run tests

```bash
cd backend

# Run default tests (no live API calls)
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run only unit tests
uv run pytest tests/unit/

# Run only API tests
uv run pytest tests/api/

# Run live tests (requires real API keys)
uv run pytest -m live
```

## How to configure provider (in app)

1. Open `http://localhost:8000`
2. Select a provider from the dropdown: **Groq** or **OpenCode Zen**
3. Paste your API key into the password field
4. Click **Connect** to validate
5. Select a model from the dropdown
6. Click **Start Chatting**

### Groq API key
Get one free at https://console.groq.com

### OpenCode Zen API key
- Base URL: must be provided by the human before Phase 04
- Set `OPENCODE_ZEN_BASE_URL` in your `.env` file
- If the variable is missing at runtime, the adapter raises `ProviderError` with code `MISSING_BASE_URL`
- No hardcoded fallback URL is allowed

## Docker services

Only Qdrant runs in Docker.

```bash
# Start Qdrant
docker compose up -d qdrant

# Check Qdrant is running
curl http://localhost:6333/healthz

# Stop Qdrant
docker compose down
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Qdrant not reachable | `docker compose up -d qdrant` then `curl http://localhost:6333/healthz` |
| Port 8000 already in use | `uvicorn app.main:app --port 8001` then open `http://localhost:8001` |
| Import errors | `cd backend && uv sync` |
| SQLite locked | Check no other process holds the DB file |
