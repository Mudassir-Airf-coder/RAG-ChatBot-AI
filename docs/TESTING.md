# Testing — RAG Chatbot

## Test framework

- Framework: `pytest`
- Location: `backend/tests/`
- Default run: no live API calls

## Test structure

```
backend/tests/
├── conftest.py           # Shared fixtures
├── unit/
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_logging.py
│   ├── test_parser.py
│   ├── test_chunker.py
│   ├── test_embedder.py
│   ├── test_vectorstore.py
│   ├── test_retriever.py
│   ├── test_generator.py
│   ├── test_storage.py
│   └── test_llm_base.py
├── api/
│   ├── test_auth.py
│   ├── test_documents.py
│   ├── test_query.py
│   └── test_chats.py
```

## What to mock

### Unit tests
Mock everything external:

| Module | What to mock |
|--------|--------------|
| `rag/parser.py` | No external dependencies; test with real files |
| `rag/chunker.py` | No external dependencies; test with raw text |
| `rag/embedder.py` | Mock fastembed model; return fixed vectors |
| `rag/vectorstore.py` | Mock Qdrant client; return fake points |
| `rag/retriever.py` | Mock Qdrant search; return fake payload |
| `rag/generator.py` | Mock LLM provider; return fake answer |
| `storage.py` | Use in-memory SQLite (no file) |
| `llm/groq.py` | Mock httpx responses |
| `llm/opencode_zen.py` | Mock httpx responses |

### API tests
Use FastAPI `TestClient` with mocked dependencies:

| Endpoint | What to mock |
|----------|--------------|
| `POST /api/v1/auth/models` | LLM provider `get_models` call |
| `POST /api/v1/documents/upload` | `rag/` pipeline (parser, chunker, embedder, vectorstore) |
| `DELETE /api/v1/documents/{id}` | `storage.py` + `vectorstore.py` + disk removal |
| `GET /api/v1/documents/{id}/chunks/{chunk_id}` | Disk read for chunk file |
| `POST /api/v1/query` | `rag/` pipeline + LLM provider |
| `GET /api/v1/chats` | `storage.py` |
| `POST /api/v1/chats` | `storage.py` |
| `DELETE /api/v1/chats/{id}` | `storage.py` |

## Shared fixtures (`conftest.py`)

```python
@pytest.fixture
def test_client(app):
    """FastAPI test client with mocked dependencies."""
    ...
```

```python
@pytest.fixture
def in_memory_db(tmp_path):
    """In-memory SQLite for unit tests."""
    ...
```

```python
@pytest.fixture
def mock_qdrant():
    """Mocked Qdrant client."""
    ...
```

```python
@pytest.fixture
def mock_llm_provider():
    """Mocked LLM provider returning canned answers."""
    ...
```

## Live tests

- Mark live tests with `@pytest.mark.live`
- Default `pytest` run skips them
- To run live tests:
  ```bash
  uv run pytest -m live
  ```
- Live tests require real API keys in environment
- Live tests must NOT be committed with hardcoded keys

## Coverage expectations

- Overall: 80%+ line coverage
- Critical paths (query, ingestion, provider adapter): 90%+
- Run with:
  ```bash
  uv run pytest --cov=app --cov-report=term-missing
  ```

## No live API calls in default run

The `pytest` command must run without hitting any real API endpoint. All external calls (LLM providers, Qdrant, fastembed model loading) must be mocked in the default test suite.
