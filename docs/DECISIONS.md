# Architectural Decisions — RAG Chatbot

## ADR 001: FastAPI + plain HTML/CSS/JS (not Next.js/Streamlit)

### Context
This is a local-first RAG chatbot for a developer/portfolio. It does not need SSR, complex routing, or a component framework.

### Decision
Use FastAPI for the backend and plain HTML + CSS + JavaScript for the frontend. No framework, no build step.

### Consequences
- FastAPI gives async support and OpenAPI docs out of the box.
- Plain frontend eliminates npm, node_modules, build toolchains.
- Tradeoff: no hot-reload, no typed component system, no reusable component library.
- Acceptable: the frontend is small (login + chat + sidebar).

---

## ADR 002: Single LLM provider (Groq)

### Context
RAG chatbots often add many providers with fallback chains and configuration sprawl.

### Decision
Support exactly 1 provider: **Groq**. No others. No fallback chains.

### Consequences
- Groq adapter implements the LLMProvider interface.
- Groq base URL is hardcoded in config (no .env required).
- Tradeoff: no fallback if Groq is down.
- Acceptable: single-user workflow, no SLA.

---

## ADR 003: Dense-only retrieval

### Context
Hybrid retrieval (dense + sparse) and rerankers improve relevance but add complexity.

### Decision
Use dense-only retrieval via fastembed vectors in Qdrant. No sparse, no hybrid, no reranker in v1.

### Consequences
- Single vector search call per query.
- Tradeoff: no BM25-style keyword fallback for rare terms.
- Acceptable: documents are small and focused; dense retrieval is sufficient for v1.

---

## ADR 004: SQLite for metadata storage

### Context
The app needs to store document metadata, chat history, and message history.

### Decision
Use SQLite as the single metadata store. No PostgreSQL, no ORM.

### Consequences
- Zero configuration; file-based database.
- One DB file per project.
- Tradeoff: no concurrent write scalability.
- Acceptable: single-user local workflow.

---

## ADR 005: sessionStorage for API key

### Context
The API key must be available to the frontend for provider calls but should not persist.

### Decision
Store `{ provider, api_key, model }` in browser `sessionStorage`. Clear on tab close.

### Consequences
- No password database, no OAuth, no backend auth storage.
- Tradeoff: key is lost on tab close; user re-enters it.
- Acceptable: single-user demo workflow; key is the user's own key.

---

## ADR 006: Recursive chunking (500 chars, 50 overlap)

### Context
Documents must be chunked before embedding. There are many chunking strategies.

### Decision
Use recursive character chunking: split at 500 characters with 50-character overlap.

### Consequences
- Simple, predictable chunk sizes.
- Overlap prevents information loss at boundaries.
- Tradeoff: fixed-size chunks may split mid-sentence.
- Acceptable: recursive splitting tries paragraph/sentence boundaries first.

---

## ADR 007: fastembed for local embeddings

### Context
Embeddings require either a remote API or a local model. Remote embeddings add latency, cost, and API-key dependency.

### Decision
Use fastembed with the `BAAI/bge-small-en-v1.5` model for local embeddings. No API key needed.

### Consequences
- No external embedding API dependency.
- First call downloads the model (one-time).
- Tradeoff: slightly higher local memory usage.
- Acceptable: the model is small (134M parameters).

---

## ADR 008: Structured JSON logging with API key redaction

### Context
Logs are useful for debugging but API keys must never appear in logs.

### Decision
All logs are structured JSON. Any API key in a log message is redacted before writing.

### Consequences
- Easy to parse logs programmatically.
- API key is safe in production.
- Tradeoff: redaction may obscure some debug info.
- Acceptable: redaction targets only the key, not surrounding context.

---

## ADR 009: No streaming in v1

### Context
Streaming improves perceived latency for LLM responses. But it adds complexity to both backend and frontend.

### Decision
Do not implement streaming in v1. The LLM response is fully generated before returning to the frontend.

### Consequences
- Simpler backend (no SSE or WebSocket).
- Simpler frontend (no streaming render).
- Tradeoff: user waits for full response before seeing anything.
- Acceptable: demo/portfolio workflow; latency is low with Groq.

---

## ADR 010: No multi-tenancy or OAuth

### Context
Many RAG chatbots have user accounts, team workspaces, and shared documents.

### Decision
No user accounts. No OAuth. No password database. Single-session, single-user workflow only.

### Consequences
- No auth infrastructure to maintain.
- Tradeoff: no shared documents, no team features.
- Acceptable: local-first, single-user design.
