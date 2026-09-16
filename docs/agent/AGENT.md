# Agent Instructions — RAG Chatbot

## Read this first

Every coding session starts by reading this file. Do not skip it.

## How to work

### 1. Read specs before coding

Before writing any code:
1. Read `docs/SPECIFICATION.md`
2. Read the phase doc for the current phase (e.g., `docs/phases/PHASE_01_FOUNDATION.md`)
3. Read `docs/ARCHITECTURE.md`
4. Read `docs/DATA_MODEL.md` if you are touching storage or vector DB
5. Read `docs/API.md` if you are wiring endpoints

### 2. Follow the locked decisions

The decisions in `docs/DECISIONS.md` are locked for v1. Do not override them:
- FastAPI + plain HTML/CSS/JS
- Only 2 providers (Groq + OpenCode Zen)
- Dense-only retrieval
- SQLite for metadata
- sessionStorage for API key
- Recursive chunking (500 chars, 50 overlap)
- fastembed local embeddings
- No streaming, no hybrid, no reranker

### 3. Respect layer boundaries

Never violate these boundaries:

| Layer | Can call | Cannot call |
|-------|----------|-------------|
| `api/` | `rag/`, `storage.py`, `llm/` | Static files, browser |
| `rag/` | Qdrant (via `vectorstore.py`), fastembed (via `embedder.py`), disk (for chunk files) | LLM providers |
| `llm/` | External API (Groq, OpenCode Zen) | `rag/`, `storage.py` |
| `storage.py` | SQLite | Qdrant, LLM providers |
| `static/` | Backend via HTTP | Direct module imports |

The orchestrator pattern:
- `api/` is the only layer that combines `rag/`, `storage.py`, and `llm/`
- `rag/` never calls `llm/` directly
- `llm/` never calls `rag/` directly

### 4. Evidence before claims

Never say "done" without evidence.

For code changes:
- Run `pytest` and show the passing test count
- Show the relevant test names

For API changes:
- Show the `curl` command and the response body

For frontend changes:
- Show the browser interaction or a screenshot

### 5. One fix, one commit

- Each commit addresses exactly one change
- Commit messages are scoped: `fix(chunker): split at paragraph boundaries`
- Never bundle unrelated changes in one commit

### 6. Update tracker after completing a phase

After completing every phase:
1. Update `docs/agent/TRACKER.md`
2. Update `docs/agent/PROGRESS.md`
3. Commit both with the phase commit

### 7. Stop and ask when blocked

If something is ambiguous, wrong, or missing:
1. Stop
2. Describe the blocker clearly
3. Ask the human

Do not guess. Do not invent providers. Do not add fallbacks.

## Hard NO list

| Action | Why |
|--------|-----|
| Fake progress | Never claim work is done without evidence |
| Fallback providers | Only Groq and OpenCode Zen. No others. |
| Unverified claims | Always run tests or show curl output |
| Adding streaming | Out of scope for v1 |
| Adding hybrid retrieval | Out of scope for v1 |
| Adding rerankers | Out of scope for v1 |
| Adding OAuth or user accounts | Out of scope for v1 |
| Adding Next.js or Streamlit | Use plain HTML/CSS/JS |
| Modifying locked decisions | They are locked for v1 |
| Committing API keys | Never commit secrets |
| Making up responses | Never fabricate data |

## File naming conventions

- Python modules: `snake_case.py`
- Test files: `test_{module_name}.py`
- Phase docs: `PHASE_NN_NAME.md`
- Agent docs: UPPERCASE

## When to use the task tool

- If a subtask is independent and bounded, dispatch to a subagent
- If a subtask touches multiple modules, keep it in the main agent
- Always verify subagent output before claiming done
