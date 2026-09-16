# Phase 02 — Ingestion

## Goal
Build the document ingestion pipeline: parse files into raw text, chunk into 500-character segments, embed with fastembed, and upsert into Qdrant.

## Files to create or modify
- `backend/app/rag/__init__.py` — Package init
- `backend/app/rag/parser.py` — Parse PDF, MD, TXT, DOCX into raw text with metadata
- `backend/app/rag/chunker.py` — Recursive chunking (500 chars, 50 overlap)
- `backend/app/rag/embedder.py` — fastembed wrapper (BAAI/bge-small-en-v1.5)
- `backend/app/rag/vectorstore.py` — Qdrant collection create/upsert/delete
- `backend/tests/unit/test_parser.py` — Parsing tests
- `backend/tests/unit/test_chunker.py` — Chunking edge cases
- `backend/tests/unit/test_embedder.py` — Mock embedding tests
- `backend/tests/unit/test_vectorstore.py` — Mock Qdrant tests

## Interfaces to define

### `backend/app/rag/parser.py`
```python
def parse_file(file_path: str) -> list[dict]:
    """Returns [{"text": "...", "metadata": {"source": "filename", "page": 1}}, ...]"""
    ...
```

### `backend/app/rag/chunker.py`
```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """Returns [{"index": 0, "text": "..."}, ...]"""
    ...
```

### `backend/app/rag/embedder.py`
```python
from numpy import ndarray

def embed_chunks(chunks: list[str]) -> list[ndarray]:
    """Returns list of embedding vectors."""
    ...
```

### `backend/app/rag/vectorstore.py`
```python
from qdrant_client.models import PointStruct

def create_collection(collection_name: str) -> None:
    """Create Qdrant collection with dense vector."""
    ...

def upsert_chunks(
    collection_name: str,
    document_id: str,
    chunks: list[dict],
    embeddings: list[ndarray],
) -> None:
    """Upsert chunk vectors + payload into Qdrant."""
    ...

def delete_by_document_id(collection_name: str, document_id: str) -> None:
    """Delete all points for a document."""
    ...
```

## Tests required
- `backend/tests/unit/test_parser.py`
  - Test parsing a TXT file returns text + metadata
  - Test parsing a MD file returns sections
  - Test parsing a PDF file returns pages
  - Test parsing a DOCX file returns paragraphs
- `backend/tests/unit/test_chunker.py`
  - Test chunking short text (< 500 chars) returns 1 chunk
  - Test chunking long text returns multiple chunks with overlap
  - Test overlap content matches between adjacent chunks
- `backend/tests/unit/test_embedder.py`
  - Mock fastembed model; assert embed_chunks returns correct count
  - Assert each embedding has correct shape
- `backend/tests/unit/test_vectorstore.py`
  - Mock Qdrant client; assert create_collection called correctly
  - Assert upsert_chunks creates points with correct payload
  - Assert delete_by_document_id filters by document_id

## Manual verification
```bash
# Upload a test file and verify chunks in Qdrant
curl -s -X POST http://localhost:8000/api/v1/documents/upload \
  -F 'file=@test.txt'
```
Expected:
```json
{"id":"doc_...","filename":"test.txt","status":"PROCESSING"}
```
After processing completes:
```json
{"id":"doc_...","filename":"test.txt","status":"READY"}
```

## Definition of Done
- [ ] Parser handles PDF, MD, TXT, DOCX
- [ ] Chunker produces 500-char chunks with 50 overlap
- [ ] Embedder uses fastembed with BAAI/bge-small-en-v1.5
- [ ] Vectorstore creates collection and upserts chunks
- [ ] Upload flow works end-to-end
- [ ] All tests pass

## Evidence to record
- Paste curl output in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: which parser fails, which Qdrant operation fails
- Report to: human

## Do NOT
- Do not implement retrieval yet
- Do not implement LLM generation yet
- Do not create API endpoints yet
- Do not create frontend files yet
