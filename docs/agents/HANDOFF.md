# Handoff Document

## Current State (One Paragraph)

The RAG Chatbot is a fully functional local-first RAG system with Cohere embeddings (1024-dim), Groq/OpenCode Zen LLMs, Qdrant vector DB, and SQLite metadata. All 98 tests pass. Features: document upload (PDF/MD/TXT/DOCX), async ingestion with progress, intent-aware query pipeline (verbatim/teach/summarize/compare/knowledge), inline clickable citations, chat history with localStorage persistence, sticky header/input UI, provider config persistence. Scanned PDFs require Tesseract OCR (not installed). All 98 tests pass. Server runs on port 8000 with `./backend/run.sh`.

---

## What to Do Next (Numbered)

1. **Install Tesseract OCR** (5 min) — `sudo apt install tesseract-ocr` (or `brew install tesseract` on macOS). Enables scanned PDF processing.

2. **Add hybrid search** (2 days) — Combine BM25 (keyword) + dense (Cohere) retrieval for better precision on exact matches.

3. **Add streaming LLM responses** (1 day) — Stream Groq tokens to frontend for perceived speed.

4. **Add multi-user auth** (3 days) — JWT-based auth, per-user data isolation, team workspaces.

4. **Document versioning** (2 days) — Track document updates, show diff, allow rollback.

5. **Next.js frontend rewrite** (1 week) — React/TypeScript for better DX, component reuse, testing.

6. **Streamlit demo** (2 days) — Quick demo deployable to Streamlit Cloud.

6. **CLI installer** (1 day) — `pipx install rag-chatbot` or `uv tool install`.

7. **Team workspaces** (3 days) — Shared docs, RBAC, audit logs.

---

## Known Issues

| Issue | Severity | Workaround |
|-------|----------|------------|
| Tesseract not installed | Medium | Install manually: `apt install tesseract-ocr` |
| Scanned PDFs >200 pages rejected | Low | Split PDF before upload |
| Large scanned PDFs slow (100 pages = 2-5 min) | Medium | Acceptable for batch processing |
| No streaming responses | Low | Add `stream=True` to Groq call |
| No multi-user auth | High | Requires JWT + per-user data isolation |
| No hybrid search | Medium | Add BM25 index alongside Qdrant |
| No document versioning | Low | Add version column + diff view |
| No streaming responses | Low | Add SSE/WebSocket endpoint |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cohere API changes | Low | High | Pin model version, monitor changelog |
| Groq API changes | Low | High | Pin model version, monitor changelog |
| Qdrant breaking changes | Low | Medium | Pin version in docker-compose |
| SQLite corruption | Low | High | WAL mode enabled, backup strategy |
| Cohere rate limits (429) | Medium | Medium | Semaphore + exponential backoff |
| Tesseract not installed | High | Medium | Clear error message, install guide |
| SQLite locking | Low | Medium | WAL mode, single writer |
| Qdrant data loss | Low | Critical | Regular snapshots, backup script |

---

## Do Not Touch

| File | Reason |
|------|--------|
| `backend/app/rag/parser.py` — `_parse_pdf` page_count fix | Critical for scanned PDF error handling |
| `backend/app/api/documents.py` — global `chunk_index` | Prevents Qdrant point ID collisions |
| `backend/app/rag/vectorstore.py` — empty points guard | Prevents upsert crashes |
| `backend/app/rag/intent.py` — intent classification | Core to per-intent behavior |
| `backend/app/rag/generator.py` — `PROMPTS` dict | Per-intent system prompts |
| `backend/app/rag/query_rewriter.py` — `REWRITE_PROMPT` | Typo fixing + intent preservation |
| `backend/app/api/query.py` — intent-aware pipeline | Core query flow |
| `backend/static/index.html` — CSS layout | Sticky header/input depends on exact flex values |
| `backend/static/index.html` — `makeCitationsClickable` | Inline citation UX |
| `backend/app/api/provider.py` — session merge logic | Config persistence |
| `backend/app/rag/chunker.py` — global `chunk_index` | Chunk ID uniqueness |
| `backend/app/config.py` — all settings | Central config, don't hardcode |

---

## Test Commands

```bash
# All tests
cd backend && uv run pytest -q
# 98 passed

# Unit only
uv run pytest tests/unit/ -q

# API only
uv run pytest tests/api/ -q

# With coverage
uv run pytest --cov=app --cov-report=term-missing

# Single test
uv run pytest tests/unit/test_chunker.py::test_overlap_exists -v
```

---

## Quick Verification

```bash
# 1. Health
curl http://localhost:8000/api/v1/health
# {"status":"ok"}

# 2. Provider config
curl -X POST http://localhost:8000/api/v1/provider/config \
  -H "Content-Type: application/json" \
  -d '{"name":"Groq","base_url":"https://api.groq.com/openai/v1","api_key":"gsk_test","model":"llama-3.1-8b-instant","cohere_api_key":"sk-test"}'
# {"ok":true,"llm_configured":true,"cohere_configured":true}

# 3. Upload
curl -X POST -b cookie.txt -F "file=@README.md" http://localhost:8000/api/v1/documents/upload
# {"id":"doc_xxx","filename":"README.md","status":"UPLOADED"}

# 3. Query
curl -X POST -b cookie.txt -H "Content-Type: application/json" \
  -d '{"question":"What is the license?"}' \
  http://localhost:8000/api/v1/query
# {"answer":"The license is MIT. [1]","citations":[...],"abstained":false}
```

---

## Git State

```bash
# Current branch
git branch
# master

# Last 5 commits
git log --oneline -5
# 7a3d8f8 fix(ui): sticky header and input; only messages scroll (ChatGPT-like)
# dd31ed4 fix(documents): use global chunk index to prevent Qdrant point ID collisions
# 9e316db fix(vectorstore): correct argument order for delete_by_document_id
# 7c60b81 chore: restore uv.lock (dependency lock file, must be tracked)
# 87811a7 chore: remove junk files from git tracking

# Working tree status
git status
# On branch master
# nothing to commit, working tree clean
```

---

## Quick Links

| Resource | Link |
|----------|------|
| Project root | `~/Desktop/CODING/project_01/` |
| Backend | `~/Desktop/CODING/project_01/backend/` |
| Frontend | `~/Desktop/CODING/project_01/backend/static/index.html` |
| Docs (humans) | `~/Desktop/CODING/project_01/docs/humans/` |
| Docs (agents) | `~/Desktop/CODING/project_01/docs/agents/` |
| Tests | `~/Desktop/CODING/project_01/backend/tests/` |
| Qdrant UI | `http://localhost:6333/dashboard` |
| API docs | `http://localhost:8000/docs` |

---

## Final Notes

The project is in a **stable, production-ready state** for local single-user use. All core features work, tests pass, and the codebase follows clean architecture with clear layer boundaries. The main gaps are Tesseract OCR (system dependency), streaming responses, multi-user auth, and hybrid search — all documented as next steps.

**To resume work**: Read this file, then `docs/agents/SESSIONS.md`, then `docs/agents/TRACKER.md`, then run `cd backend && uv run pytest -q` to verify.