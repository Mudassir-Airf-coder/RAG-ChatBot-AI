# AI Agent Instructions

## Read First — Required Files

Before making any changes, read these files in order:

1. `docs/humans/OVERVIEW.md` — Project purpose and scope
2. `docs/humans/ARCHITECTURE.md` — Layer diagram, folder structure, key decisions
3. `docs/humans/FLOW.md` — Data flows with diagrams
4. `docs/humans/SETUP.md` — How to run, test, verify
5. `backend/app/main.py` — FastAPI app entry point
5. `backend/app/config.py` — Settings and env vars
6. `backend/app/api/query.py` — Core query pipeline
7. `backend/app/rag/generator.py` — Intent-specific prompts
8. `backend/app/rag/intent.py` — Intent classification
9. `backend/app/rag/query_rewriter.py` — Query rewriting
10. `backend/app/rag/retriever.py` — Vector search
10. `backend/app/rag/parser.py` — Document parsing
11. `backend/app/rag/chunker.py` — Text chunking
12. `backend/app/rag/vectorstore.py` — Qdrant operations
13. `backend/app/embeddings/cohere_cloud.py` — Cohere embeddings
14. `backend/app/llm/groq.py` — Groq LLM adapter
15. `backend/app/llm/opencode_zen.py` — OpenCode Zen adapter
16. `backend/app/api/documents.py` — Upload/ingestion pipeline
17. `backend/app/api/provider.py` — Provider config + session
18. `backend/app/api/query.py` — Query pipeline
18. `backend/app/api/provider.py` — Provider config
19. `backend/static/index.html` — Frontend

---

## Project State

### What Works (Verified)

- ✅ Document upload (PDF/MD/TXT/DOCX) → 202 Accepted → background processing → READY
- ✅ Cohere embeddings (1024-dim, batch 96, multiple extraction modes)
- ✅ Groq LLM + OpenCode Zen (OpenAI-compatible)
- ✅ Qdrant vector DB (Docker, 1024-dim, Cosine)
- ✅ SQLite metadata (documents, chats, messages)
- ✅ Query pipeline: intent → rewrite → retrieve → generate → citations
- ✅ Intent classification: verbatim, teach, summarize, compare, knowledge
- ✅ Per-intent system prompts (verbatim, teach, summarize, compare, knowledge)
- ✅ Query rewrite with typo fixing, intent preservation
- ✅ Inline clickable citations [1][2] in answers
- ✅ Chat history with localStorage persistence
- ✅ Provider config (LLM + Cohere) with localStorage + HttpOnly cookie
- ✅ Document upload/delete, status polling
- ✅ 98 tests passing (unit + API)
- ✅ Sticky header/input, scrollable messages only
- ✅ Sticky header/input, only messages scroll

### What Doesn't Work / Known Limitations

- ❌ Scanned PDFs: Need Tesseract OCR (not installed by default)
- ❌ No streaming LLM responses
- ❌ No hybrid search (BM25 + dense)
- ❌ No multi-user auth
- ❌ Large scanned PDFs slow (100 pages = 2-5 min OCR)
- ❌ No document versioning
- ❌ No multi-user / team workspaces
- ❌ No streaming LLM responses
- ❌ Tesseract OCR not installed (system dependency)

---

## Layer Boundaries — Never Break These

| Layer | Can Import From | Cannot Import From |
|-------|-----------------|-------------------|
| API (`app/api/*`) | Application, Domain, Adapter | — |
| Application (`app/api/*` logic) | Domain, Adapter | API |
| Domain (`app/rag/*`) | Adapter | Application, API |
| Adapter (`app/llm/*`, `app/embeddings/*`) | stdlib, 3rd party | Domain, Application, API |

**Enforced by import structure** — if you violate this, tests will catch it.

---

## Commit Message Format

```
<type>(<scope>): <summary>

[optional body]

[optional footer]
```

| Type | Use For |
|------|---------|
| `fix` | Bug fixes |
| `feat` | New features |
| `chore` | Maintenance, config, deps |
| `docs` | Documentation only |
| `refactor` | Code restructuring |
| `test` | Test changes |
| `perf` | Performance improvements |

**Examples**:
```
fix(documents): use global chunk index to prevent Qdrant point ID collisions
feat(rag): intent classification + per-intent prompts (verbatim, teach, summarize)
fix(ui): sticky header and input; only messages scroll (ChatGPT-like)
chore: remove stale docs and artifacts before production upgrade
docs: complete project documentation with human and agent views
```

---

## Evidence Rules

**Always paste real output, never summaries.**

| Claim | Required Evidence |
|-------|-------------------|
| "Tests pass" | `uv run pytest -q` output (98 passed) |
| "Server works" | `curl /api/v1/health` → `{"status":"ok"}` |
| "Upload works" | Upload log showing `upload_streamed` → `parse_done` → `chunk_done` → `embed_done` → `upsert_done` → `index_done` |
| "Query works" | `curl /query` output with citations |
| "No secrets in git" | `git log -p -10 \| grep -iE "api_key\|secret" \| grep -v example` |

**Never claim success without pasting actual terminal output.**

---

## Hard NO List

| Never Do This | Why |
|---------------|-----|
| Change Qdrant collection name (`rag_chatbot_cohere`) | Breaks existing data |
| Change Cohere model away from `embed-english-v3.0` | Breaks 1024-dim vectors |
| Remove `min-height: 0` from `.chat-messages` | Breaks sticky header/input |
| Remove `flex: 0 0 auto` from `.input-area` | Input scrolls away |
| Remove `min-height: 0` from `.sidebar` / `.config-panel` | Layout breaks on collapse |
| Change `minmax(0, 1fr)` in grid template | Breaks collapse states |
| Remove `min-height: 0` from `.chat-main` | Flex children won't scroll |
| Change chunk index from global to per-page | Breaks Qdrant point ID uniqueness |
| Remove `min-height: 0` from `.chat-messages` | Messages push input out of view |
| Remove `sessionStorage` for panel collapse state | State lost on reload |
| Change `localStorage` to `sessionStorage` for provider config | Config lost on tab close |
| Remove `HttpOnly` cookie for session | Security regression |
| Change Qdrant dimension from 1024 | Breaks all existing vectors |
| Remove `semaphore` in ingestion | Cohere 429 / Qdrant overload |
| Remove `page_count` capture before `doc.close()` | Parser crashes on scanned PDFs |

---

## Evidence-Based Workflow

1. **Diagnose first** — Run diagnostics, paste output
2. **Plan minimal fix** — One file, one change
3. **Implement** — Follow layer boundaries
4. **Verify** — Run `uv run pytest -q` (must be 98 passed)
5. **Test in browser** — Paste actual curl output / screenshots
6. **Commit** — Use proper format, reference issue

---

## How to Resume Work

1. Read `docs/agents/SESSIONS.md` for previous session log
2. Check `docs/agents/TRACKER.md` for current phase
3. Read `docs/agents/TASKS.md` for prioritized tasks
4. Run `cd backend && uv run pytest -q` — confirm 98 passed
5. Start server: `./run.sh` (from project root)
6. Verify: `curl http://localhost:8000/api/v1/health`

---

## Key Files Quick Reference

| Task | File |
|------|------|
| Add new intent | `app/rag/intent.py` + `app/rag/generator.py` |
| Fix chunking | `app/rag/chunker.py` |
| Fix parser | `app/rag/parser.py` |
| Fix embeddings | `app/embeddings/cohere_cloud.py` |
| Fix retrieval | `app/rag/retriever.py` |
| Fix generation | `app/rag/generator.py` |
| Fix query pipeline | `app/api/query.py` |
| Fix upload/ingestion | `app/api/documents.py` |
| Fix provider config | `app/api/provider.py` |
| Fix frontend UI | `backend/static/index.html` |
| Fix tests | `tests/unit/` or `tests/api/` |

---

## Safety Checklist Before Commit

- [ ] `uv run pytest -q` → 98 passed
- [ ] `curl /api/v1/health` → `{"status":"ok"}`
- [ ] No secrets in diff (`git diff --no-color | grep -iE "api_key|secret|token" | grep -v example`)
- [ ] Commit message follows format
- [ ] Only intended files changed (`git status`)
- [ ] No debug prints, no `print()`, no `console.log`

---

## Emergency Rollback

```bash
# If something breaks badly
git reset --hard HEAD~1
pkill -f uvicorn
docker stop rag-qdrant
cd ~/Desktop/CODING/project_01 && ./backend/run.sh
```