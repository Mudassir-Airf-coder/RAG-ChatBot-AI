# Phase 04 — Generation

## Goal
Build the LLM provider adapters: base interface, Groq adapter, OpenCode Zen adapter, and the grounded answer generator that combines retrieved context with LLM calls.

## Files to create or modify
- `backend/app/llm/__init__.py` — Package init
- `backend/app/llm/base.py` — LLMProvider interface (base class)
- `backend/app/llm/groq.py` — Groq adapter
- `backend/app/llm/opencode_zen.py` — OpenCode Zen adapter
- `backend/app/rag/generator.py` — Grounded answer via LLM
- `backend/tests/unit/test_llm_base.py` — Interface tests
- `backend/tests/unit/test_llm_groq.py` — Mock Groq tests
- `backend/tests/unit/test_llm_opencode_zen.py` — Mock OpenCode Zen tests
- `backend/tests/unit/test_generator.py` — Generation tests

## Interfaces to define

### `backend/app/llm/base.py`
```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def __init__(self, api_key: str):
        ...

    @abstractmethod
    async def get_models(self) -> list[str]:
        """Return list of available model IDs."""
        ...

    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: list[dict],
    ) -> str:
        """Return assistant message content."""
        ...
```

### `backend/app/llm/groq.py`
```python
class GroqProvider(LLMProvider):
    BASE_URL = "https://api.groq.com/openai/v1"

    async def get_models(self) -> list[str]:
        """GET {BASE_URL}/models"""
        ...

    async def chat(self, model: str, messages: list[dict]) -> str:
        """POST {BASE_URL}/chat/completions"""
        ...
```

### `backend/app/llm/opencode_zen.py`
```python
class OpenCodeZenProvider(LLMProvider):
    BASE_URL = "PLACEHOLDER"  # Must be confirmed by human

    async def get_models(self) -> list[str]:
        """GET {BASE_URL}/models"""
        ...

    async def chat(self, model: str, messages: list[dict]) -> str:
        """POST {BASE_URL}/chat/completions"""
        ...
```

### `backend/app/rag/generator.py`
```python
def generate_answer(
    context_chunks: list[dict],
    question: str,
    provider: LLMProvider,
    model: str,
) -> dict:
    """
    Returns:
    {
        "answer": "assistant answer text",
        "citations": [
            {"citation_index": 1, "document_id": "doc_...", "chunk_id": "chunk_..."},
            ...
        ]
    }
    """
    ...
```

## Tests required
- `backend/tests/unit/test_llm_base.py`
  - Test: `LLMProvider` cannot be instantiated directly
  - Test: subclass must implement `get_models` and `chat`
- `backend/tests/unit/test_llm_groq.py`
  - Mock httpx; assert GET /models returns model list
  - Mock httpx; assert POST /chat/completions returns answer
  - Test: invalid API key returns 401 error
- `backend/tests/unit/test_llm_opencode_zen.py`
  - Same as Groq but with OpenCode Zen base URL
- `backend/tests/unit/test_generator.py`
  - Test: context chunks + question → answer string
  - Test: citations list is constructed from context chunks
  - Test: empty context returns error

## Manual verification
```bash
# Once Phase 06 wires the endpoint
curl -s -X POST http://localhost:8000/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"chat_id":"chat_123","question":"What is X?","provider":"groq","api_key":"...","model":"llama-3.1-70b-versatile"}'
```
Expected:
```json
{
  "chat_id": "chat_123",
  "answer": "...",
  "citations": [{"citation_index":1,"document_id":"doc_...","chunk_id":"chunk_..."}]
}
```

## Definition of Done
- [ ] `LLMProvider` base class defined
- [ ] Groq adapter calls GET /models and POST /chat/completions
- [ ] OpenCode Zen adapter calls GET /models and POST /chat/completions
- [ ] `generate_answer` builds context from chunks and calls LLM
- [ ] Citations are correctly constructed from context chunks
- [ ] All tests pass with mocked HTTP calls

## Evidence to record
- Paste test output in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: which provider endpoint fails, which response shape is unexpected
- Report to: human (especially for OpenCode Zen base URL confirmation)

## Do NOT
- Do not implement API endpoints yet
- Do not create frontend files yet
- Do not add streaming
- Do not add fallback providers
