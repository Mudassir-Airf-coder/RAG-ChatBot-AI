# Phase 03 — Retrieval

## Goal
Build the dense retrieval layer: embed a query, search Qdrant for top-K chunks, and return chunk IDs with payloads.

## Files to create or modify
- `backend/app/rag/retriever.py` — Dense search with top-K
- `backend/tests/unit/test_retriever.py` — Retrieval tests

## Interfaces to define

### `backend/app/rag/retriever.py`
```python
def retrieve(
    collection_name: str,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Returns list of retrieved chunks:
    [
        {
            "chunk_id": "chunk_doc_123_0",
            "document_id": "doc_123",
            "chunk_index": 0,
            "chunk_text": "full text of chunk...",
            "metadata": {"source": "example.pdf", "page": 12},
            "score": 0.87
        },
        ...
    ]
    """
    ...
```

## Tests required
- `backend/tests/unit/test_retriever.py`
  - Test: returns empty list when no chunks in Qdrant
  - Test: returns top_k results sorted by score descending
  - Test: each result contains chunk_id, document_id, chunk_index, chunk_text, metadata, score
  - Test: embedding the query before search

## Manual verification
```bash
# First, upload a document (Phase 02 must be complete)
curl -s -X POST http://localhost:8000/api/v1/documents/upload \
  -F 'file=@test.txt'

# Then, query it
curl -s -X POST http://localhost:8000/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"chat_id":"chat_123","question":"What is X?","provider":"groq","api_key":"...","model":"..."}'
```
Expected (once Phase 06 wires the endpoint):
```json
{
  "chat_id": "chat_123",
  "answer": "...",
  "citations": [...]
}
```

## Definition of Done
- [ ] `retrieve()` embeds query and searches Qdrant
- [ ] Returns top-K results sorted by score
- [ ] Each result has full payload (chunk_id, document_id, metadata, score)
- [ ] Tests pass with mocked Qdrant

## Evidence to record
- Paste test output in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: Qdrant search issues, embedding shape mismatches
- Report to: human

## Do NOT
- Do not implement LLM generation yet
- Do not create API endpoints yet
- Do not create frontend files yet
