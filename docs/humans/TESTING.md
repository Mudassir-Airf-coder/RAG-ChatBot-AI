# Testing Guide

## Quick Start

```bash
cd backend
uv run pytest -q
# 98 passed, 2 warnings
```

---

## Test Structure

```
tests/
├── unit/                    # Pure functions, mocked dependencies
│   ├── test_chunker.py
│   ├── test_config.py
│   ├── test_cohere_embedder.py
│   ├── test_exceptions.py
│   ├── test_generator.py
│   ├── test_llm_base.py
│   ├── test_llm_groq.py
│   ├── test_llm_opencode_zen.py
│   ├── test_logging.py
│   ├── test_parser.py
│   ├── test_query_rewriter.py
│   ├── test_retriever.py
│   ├── test_storage.py
│   └── test_vectorstore.py
├── api/                     # FastAPI TestClient, mocked providers
│   ├── test_chats.py
│   ├── test_documents.py
│   ├── test_health.py
│   ├── test_provider.py
│   └── test_query.py
┠── conftest.py              # Shared TestClient fixture
```

---

## Running Tests

### All Tests

```bash
cd backend
uv run pytest -q
# 98 passed, 2 warnings in ~2s
```

### By Category

```bash
# Unit tests only
uv run pytest tests/unit/ -q

# API integration tests
uv run pytest tests/api/ -q

# Specific file
uv run pytest tests/unit/test_chunker.py -v

# With coverage
uv run pytest --cov=app --cov-report=term-missing
```

### Filter by Marker

```bash
# Skip slow tests (if marked)
uv run pytest -m "not slow"

# Only async tests
uv run pytest -m asyncio
```

---

## Test Categories

### Unit Tests (`tests/unit/`)

Pure functions, fully mocked. No external dependencies.

| File | Tests | Coverage |
|------|-------|----------|
| `test_chunker.py` | 5 | Chunking logic, overlap, boundaries |
| `test_config.py` | 3 | Settings validation |
| `test_cohere_embedder.py` | 10 | Batching, errors, validation |
| `test_exceptions.py` | 4 | Error codes, serialization |
| `test_generator.py` | 2 | Citations, used_indices |
| `test_llm_base.py` | 2 | Abstract interface |
| `test_llm_groq.py` | 7 | Models, chat, errors, validation |
| `test_llm_opencode_zen.py` | 3 | OpenCode Zen adapter |
| `test_parser.py` | 5 | MD, TXT, PDF, unsupported |
| `test_query_rewriter.py` | 4 | Intent classification, rewriting |
| `test_retriever.py` | 4 | Vector search, scoring |
| `test_storage.py` | 8 | SQLite CRUD |
| `test_vectorstore.py` | 2 | Upsert, delete |

### API Tests (`tests/api/`)

FastAPI TestClient with mocked providers. Tests full request/response cycle.

| File | Tests | Coverage |
|------|-------|----------|
| `test_documents.py` | 6 | Upload, list, get, delete, streaming |
| `test_provider.py` | 15 | Config, test, models, persistence |
| `test_query.py` | 5 | Intent, rewrite, retrieve, generate |
| `test_health.py` | 1 | Health endpoint |
| `test_chats.py` | 3 | Chat CRUD (if implemented) |

---

## Writing New Tests

### Unit Test Template

```python
import pytest
from unittest.mock import MagicMock, patch

from app.rag.chunker import chunk_text


def test_chunk_text_returns_chunks():
    text = "word " * 200  # ~1000 chars
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1
    assert all(c["index"] == i for i, c in enumerate(chunks))
```

### Async Test Template

```python
import pytest
from unittest.mock import AsyncMock, patch

from app.llm.groq import GroqProvider


@pytest.mark.asyncio
async def test_chat_returns_content():
    provider = GroqProvider("test-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"choices": [{"message": {"content": "hello"}}]}

    with patch("app.llm.groq.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.post = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value = instance

        result = await provider.chat("model-a", [{"role": "user", "content": "hi"}])
        assert result == "hello"
```

### API Test Template

```python
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app


def test_upload_document():
    client = TestClient(app)
    with patch("app.api.documents.parse_file") as mock_parse, \
         patch("app.embeddings.cohere_cloud.CohereEmbeddingProvider.embed_chunks") as mock_embed:
        mock_parse.return_value = [{"text": "hello", "metadata": {}}]
        mock_embed.return_value = [MagicMock(tolist=lambda: [0.1]*1024)]

        resp = client.post("/api/v1/documents/upload", files={"file": ("test.txt", b"hello", "text/plain")})
        assert resp.status_code == 202
        assert resp.json()["status"] == "UPLOADED"
```

---

## Mocking Guidelines

| Component | Mock Strategy |
|-----------|---------------|
| `CohereEmbeddingProvider` | Mock `embed_chunks` / `embed_query` return `MagicMock(tolist=lambda: [...])` |
| `GroqProvider` / `OpenCodeZenProvider` | Mock `chat()` return string, `get_models()` return list |
| `QdrantClient` | Mock `query_points`, `upsert`, `delete`, `scroll` |
| `httpx.AsyncClient` | Use `AsyncMock` with `__aenter__`/`__aexit__` |
| `parse_file` | Return list of `{"text": "...", "metadata": {...}}` |

### Example: Mocking Cohere Embedder

```python
from unittest.mock import MagicMock, patch

with patch("app.embeddings.cohere_cloud.CohereEmbeddingProvider.embed_chunks") as mock_embed:
    mock_embed.return_value = [MagicMock(tolist=lambda: [0.1]*1024) for _ in range(5)]
    # test code here
```

### Example: Mocking Groq Provider

```python
from unittest.mock import AsyncMock, MagicMock, patch

with patch("app.llm.groq.httpx.AsyncClient") as mock_client:
    instance = AsyncMock()
    instance.post = AsyncMock(return_value=MagicMock(
        status_code=200,
        json=lambda: {"choices": [{"message": {"content": "answer"}}]}
    ))
    instance.__aenter__ = AsyncMock(return_value=instance)
    instance.__aexit__ = AsyncMock(return_value=False)
    mock_client.return_value = instance
```

---

## Test Utilities

### `tests/conftest.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def test_client():
    return TestClient(app)
```

### Session Helper (API tests)

```python
def setup_session(client, session_id="test_session"):
    from app.api.provider import sessions
    sessions[session_id] = {"name": "Groq", "base_url": "https://api.groq.com/openai/v1", "api_key": "gsk_test", "model": "llama-3.1-8b-instant", "cohere_api_key": "sk-test-cohere"}
    client.cookies.set("rag_session", session_id)
    return session_id
```

---

## Continuous Integration

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: Install Python
        run: uv python install 3.11
      - name: Install deps
        working-directory: ./backend
        run: uv sync --extra dev
      - name: Run tests
        working-directory: ./backend
        run: uv run pytest -q
```

---

## Debugging Failed Tests

### Run Single Test with Output

```bash
uv run pytest tests/unit/test_chunker.py::test_overlap_exists -v -s
```

### Verbose Output

```bash
uv run pytest tests/api/test_query.py -v --tb=long
```

### Drop into Debugger

```bash
uv run pytest tests/unit/test_chunker.py -x --pdb
```

---

## Coverage

```bash
uv run pytest --cov=app --cov-report=term-missing --cov-report=html
# Open htmlcov/index.html for visual report
```

### Current Coverage Targets

| Module | Target |
|--------|--------|
| `app.rag.chunker` | 95% |
| `app.rag.parser` | 90% |
| `app.rag.generator` | 85% |
| `app.rag.retriever` | 90% |
| `app.rag.query_rewriter` | 80% |
| `app.api.documents` | 85% |
| `app.api.query` | 85% |
| `app.api.provider` | 90% |

---

## Adding New Test Files

1. Create file in `tests/unit/` or `tests/api/`
2. Follow naming: `test_<module>.py`
3. Import from `app.*` (not relative)
4. Use `pytest.mark.asyncio` for async tests
5. Run `uv run pytest -q` to verify

---

## Common Test Patterns

### Asserting Error Responses

```python
resp = client.post("/api/v1/query", json={"question": "hi"})
assert resp.status_code == 400
assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
```

### Testing Background Tasks

```python
from app.api.documents import run_ingestion
run_ingestion(doc_id, dest, name, settings, embedder, collection)
# Assert status updated in DB
```

### Testing WebSocket (Future)

```python
from fastapi.testclient import TestClient

with client.websocket_connect("/ws/documents/doc_123/status") as ws:
    data = ws.receive_json()
    assert data["status"] == "PROCESSING"
```

---

## Test Data Fixtures

```python
# tests/fixtures/sample_pdf.py
SAMPLE_PDF_PATH = "tests/fixtures/sample.pdf"

# tests/fixtures/sample_docx.py
SAMPLE_DOCX_PATH = "tests/fixtures/sample.docx"
```

---

## Running Tests in CI

```bash
# Local
uv run pytest -q

# GitHub Actions (see .github/workflows/ci.yml)
# Runs on every push/PR to main/master
```

---

## Common Test Failures & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `async def functions are not natively supported` | Missing pytest-asyncio | `uv sync --extra dev` |
| `ModuleNotFoundError: app.rag.embedder` | Old import | Update to `app.embeddings.cohere_cloud` |
| `AttributeError: 'QdrantClient' object has no attribute 'models'` | Wrong import | Use `from qdrant_client.models import ...` |
| `RuntimeError: Caught handled exception` | Background task error after response | Check `background.add_task` error handling |

---

## Test Data Fixtures

```
tests/fixtures/
├── sample.txt
├── sample.md
├── sample.pdf
└── sample.docx
```

Create minimal test files for parser tests.

---

## Performance Tests (Optional)

```bash
uv run pytest --durations=10
```
