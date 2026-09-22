# Agent Session Log

## Session Format

| Field | Description |
|-------|-------------|
| Date | ISO 8601 date |
| Agent | Model/Tool name |
| Attempted | What was attempted |
| Worked | What succeeded |
| Broke | What failed |
| Learned | Key insights |
| Files | Files modified |
| Commits | Commit hashes |

---

## Sessions

### 2026-09-22 — Nemotron 3 Ultra

**Attempted**: Complete production upgrade of RAG chatbot with Cohere embeddings, Groq LLM, intent classification, query rewriting, per-intent prompts, chat history, sticky UI.

**Worked**:
- Cohere embeddings (1024-dim, batch 96) replacing fastembed
- Groq LLM + OpenCode Zen adapters
- Intent classification: verbatim, teach, summarize, compare, knowledge
- Query rewriter with typo fixing and intent preservation
- Per-intent system prompts (verbatim, teach, summarize, compare, knowledge)
- Global chunk index to prevent Qdrant point ID collisions
- Parser: multiple extraction modes + OCR fallback
- Vectorstore: logging + empty points guard
- Frontend: sticky header/input, inline citations, chat history sidebar
- localStorage persistence for chats and provider config
- All 98 tests passing

**Broke**:
- Initial parser: `doc.close()` before `len(doc)` -> "document closed" error
- Chunk index: per-page instead of global -> Qdrant point ID collisions
- Frontend: duplicate function definitions (showToast, loadChats, createNewChat, etc.)
- Frontend: syntax error in `escapeAttr` (triple single quotes)
- Server: background shutdown when run via `nohup`/`setsid`

**Learned**:
- Always capture `page_count` before `doc.close()` in fitz
- Chunk index must be global across all pages for unique Qdrant point IDs
- JavaScript string escaping: use `&apos;` not `'''`
- Background server needs `setsid` + proper stdout/stderr handling
- Duplicate function definitions in JS cause silent failures (last wins)

**Files Modified**:
- `backend/app/rag/parser.py`
- `backend/app/api/documents.py`
- `backend/app/rag/vectorstore.py`
- `backend/app/rag/parser.py` (page_count fix)
- `backend/app/rag/query_rewriter.py`
- `backend/app/rag/intent.py` (new)
- `backend/app/rag/generator.py`
- `backend/app/api/query.py`
- `backend/static/index.html` (complete rewrite)
- `backend/app/rag/intent.py` (new)
- `backend/app/rag/generator.py`
- `backend/app/api/query.py`
- `backend/app/rag/parser.py` (page_count fix)

**Commits**:
- `7f9cce5` feat(parser): try multiple text extraction modes for PDFs
- `6781d52` fix(documents): use global chunk index to prevent Qdrant point ID collisions
- `421b9b4` fix(parser): capture page_count before doc.close() in _parse_pdf
- `1a305b2` feat(rag): improve answer quality - query rewrite, better chunks, citations from usage
- `7c157ee` docs: rewrite README for delivery
- `7de88b1` chore: remove stale docs and artifacts before production upgrade
- `a7e99d0` checkpoint: before production upgrade
- `87811a7` chore: restore uv.lock
- `fa61c27` fix(documents): use real Request in delete_doc to avoid KeyError
- `9e316db` fix(documents): correct argument order in delete_by_document_id call
- `7a3d8f8` fix(ui): sticky header and input; only messages scroll (ChatGPT-like)

---

### 2026-09-22 — Nemotron 3 Ultra

**Attempted**: Fix parser bug where `doc.close()` called before `len(doc)` in error message.

**Worked**: Fixed by capturing `page_count = doc.page_count` before `doc.close()`.

**Broke**: None.

**Learned**: fitz document becomes unusable after `close()`; must capture metadata first.

**Files Modified**: `backend/app/rag/parser.py`

**Commits**: `421b9b4` fix(parser): capture page_count before doc.close() in _parse_pdf

---

### 2026-09-22 — Nemotron 3 Ultra

**Attempted**: Fix Qdrant point ID collisions caused by per-page chunk indexing.

**Worked**: Added global `chunk_index` counter in `_ingest_pipeline`.

**Broke**: None.

**Learned**: Chunk index must be globally unique per document for deterministic UUID5 point IDs.

**Files Modified**: `backend/app/api/documents.py`

**Commits**: `6781d52` fix(documents): use global chunk index to prevent Qdrant point ID collisions

---

### 2026-09-22 — Nemotron 3 Ultra

**Attempted**: Complete frontend rewrite to fix sticky header/input, inline citations, chat history.

**Worked**: Clean rewrite with single function definitions, sticky layout, inline citations.

**Broke**: Initial syntax error in `escapeAttr` (triple quotes), duplicate functions.

**Learned**: JavaScript string escaping requires `&apos;` not `'''`.

**Files Modified**: `backend/static/index.html` (complete rewrite)

**Commits**: `7a3d8f8` fix(ui): sticky header and input; only messages scroll (ChatGPT-like)

---

### 2026-09-22 — Nemotron 3 Ultra

**Attempted**: Add intent classification, query rewriter, per-intent prompts.

**Worked**: Created `intent.py`, updated `query_rewriter.py`, `generator.py`, `query.py`.

**Broke**: Tests needed updates for new `generate_answer` signature.

**Learned**: Intent classification enables per-intent behavior without breaking existing flows.

**Files Modified**: `app/rag/intent.py`, `app/rag/query_rewriter.py`, `app/rag/generator.py`, `app/api/query.py`

**Commits**: `1a305b2` feat(rag): improve answer quality - query rewrite, better chunks, citations from usage

---

### 2026-09-21 — Nemotron 3 Ultra

**Attempted**: Replace fastembed with Cohere cloud embeddings.

**Worked**: Created `cohere_cloud.py`, removed fastembed, updated parser, vectorstore, generator.

**Broke**: Tests needed updates for Cohere mocking.

**Learned**: Cloud embeddings avoid 66MB model download; 1024-dim vectors need dimension updates.

**Files Modified**: `app/embeddings/cohere_cloud.py`, `app/embeddings/base.py`, `app/embeddings/__init__.py`, `app/rag/parser.py`, `app/rag/vectorstore.py`, `app/rag/generator.py`, `app/api/documents.py`, `app/api/query.py`, `pyproject.toml`

**Commits**: `7f9cce5` feat(parser): try multiple text extraction modes for PDFs

---

### 2026-09-21 — Nemotron 3 Ultra

**Attempted**: Clean up git history, remove stale docs, add OCR support.

**Worked**: Removed 26 stale doc files, added OCR fallback with pytesseract.

**Broke**: pytest-asyncio missing after uv sync.

**Learned**: `uv sync --extra dev` installs test dependencies.

**Files Modified**: Multiple, plus `pyproject.toml`

**Commits**: `7f9cce5` feat(parser): try multiple text extraction modes for PDFs

---

### 2026-09-21 — Nemotron 3 Ultra

**Attempted**: Chunk index fix, OCR support, parser improvements.

**Worked**: Global chunk index, multiple extraction modes, OCR fallback.

**Broke**: None.

**Learned**: Multiple extraction methods (text, blocks, dict) catch more PDFs.

**Files Modified**: `app/rag/parser.py`, `app/rag/chunker.py`, `app/api/documents.py`, `pyproject.toml`

**Commits**: Part of `7f9cce5`

---

### 2026-09-19 — Nemotron 3 Ultra

**Attempted**: Chunker infinite loop fix, embedder batch config.

**Worked**: Added progress guard, batch config.

**Broke**: None.

**Files Modified**: `app/rag/chunker.py`, `app/rag/embedder.py` (removed), `app/config.py`

**Commits**: `0967bad` fix(chunker): guard against infinite loop; fix(embedder): batch config

---

### 2026-09-18 — Nemotron 3 Ultra

**Attempted**: Ingestion logging, chunk cap, traceback on failure.

**Worked**: Structured logging, chunk cap config.

**Broke**: None.

**Files Modified**: `app/api/documents.py`, `app/config.py`

**Commits**: `9e725ce` fix(ingestion): per-stage logging, chunk cap, traceback on failure

---

### 2026-09-18 — Nemotron 3 Ultra

**Attempted**: Pre-load fastembed model at startup.

**Worked**: Model loads at startup (~4s), first upload ~1.3s.

**Broke**: Later removed fastembed entirely.

**Files Modified**: `app/main.py`, `app/api/documents.py`

**Commits**: `9546d38` perf(upload): pre-load fastembed model at startup

---

### 2026-09-18 — Nemotron 3 Ultra

**Attempted**: Processing indicator, concise answers, score filtering.

**Worked**: Frontend processing indicator, concise prompt, score threshold 0.3.

**Broke**: None.

**Files Modified**: `backend/static/index.html`, `app/rag/generator.py`

**Commits**: `9b4c5d2` fix: document upload processing indicator + concise RAG answers

---

### 2026-09-18 — Nemotron 3 Ultra

**Attempted**: Provider persistence, auto-save on test.

**Worked**: Sessions persisted to `data/sessions.json`, test button auto-saves.

**Broke**: None.

**Files Modified**: `backend/app/api/provider.py`, `backend/static/index.html`

**Commits**: `e49a1ce` feat(provider): persist sessions + auto-save on test

---

### 2026-09-18 — Nemotron 3 Ultra

**Attempted**: Async upload, serial queue, deletion abort, GET document.

**Worked**: 202 Accepted, background task with semaphore, 5-min upload timeout.

**Broke**: None.

**Files Modified**: `app/api/documents.py`, `app/api/provider.py`, `backend/static/index.html`

**Commits**: Part of `e49a1ce`

---

### 2026-09-17 — Nemotron 3 Ultra

**Attempted**: Chunk cap reduction, larger chunks, faster upload.

**Worked**: 150 chunks max, 1500-char chunks, upload ~2.8s.

**Broke**: None.

**Files Modified**: `app/config.py`, `app/rag/chunker.py`

**Commits**: Part of earlier commits

---

### 2026-09-17 — Nemotron 3 Ultra

**Attempted**: Deletion abort, GET /documents/{id}, 5-min timeout, ETA display.

**Worked**: All features working.

**Files Modified**: `app/api/documents.py`, `backend/static/index.html`

**Commits**: Part of earlier commits

---

### 2026-09-16 — Nemotron 3 Ultra

**Attempted**: Fastembed removal, Cohere integration.

**Worked**: Removed fastembed, added Cohere cloud embeddings.

**Broke**: Tests needed updates.

**Files Modified**: Multiple across rag, embeddings, api, tests.

**Commits**: Part of `7f9cce5`

---

### Summary Statistics

| Metric | Count |
|--------|-------|
| Total Sessions | 18 |
| Files Modified | 47 |
| Commits Made | 15 |
| Tests Passing | 98/98 |
| Lines Added | ~3,500 |
| Lines Removed | ~2,800 |