# Task List

## Phase 01 — Foundation

- [ ] Create `backend/pyproject.toml` with project metadata and dependencies
- [ ] Create `backend/app/__init__.py` (empty or minimal)
- [ ] Create `backend/app/main.py` with FastAPI app and static mount
- [ ] Create `backend/app/config.py` with Pydantic Settings (Qdrant URL, SQLite path, upload dir)
- [ ] Create `backend/app/logging.py` with structured JSON logger + API key redaction
- [ ] Create `backend/app/exceptions.py` with structured error classes
- [ ] Create `backend/tests/conftest.py` with shared fixtures
- [ ] Create `backend/tests/unit/test_config.py` with config loading tests
- [ ] Create `backend/tests/unit/test_logging.py` with redaction tests
- [ ] Create `backend/tests/unit/test_exceptions.py` with error response tests
- [ ] Test: `curl http://localhost:8000/api/v1/health` returns `{"status":"ok"}`
- [ ] Commit: one commit for all Phase 01 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 02 — Ingestion

- [ ] Create `backend/app/rag/__init__.py`
- [ ] Create `backend/app/rag/parser.py` with `parse_file(file_path) -> list[dict]`
- [ ] Create `backend/app/rag/chunker.py` with `chunk_text(text, chunk_size=500, overlap=50) -> list[dict]`
- [ ] Create `backend/app/rag/embedder.py` with `embed_chunks(chunks) -> list[ndarray]`
- [ ] Create `backend/app/rag/vectorstore.py` with `create_collection()`, `upsert_chunks()`, `delete_by_document_id()`
- [ ] Create `backend/tests/unit/test_parser.py` with parsing tests for PDF, MD, TXT, DOCX
- [ ] Create `backend/tests/unit/test_chunker.py` with chunking edge cases
- [ ] Create `backend/tests/unit/test_embedder.py` with mock embedding tests
- [ ] Create `backend/tests/unit/test_vectorstore.py` with mock Qdrant tests
- [ ] Test: upload a file, chunks appear in Qdrant
- [ ] Commit: one commit for all Phase 02 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 03 — Retrieval

- [ ] Create `backend/app/rag/retriever.py` with `retrieve(query, top_k=5) -> list[dict]`
- [ ] Create `backend/tests/unit/test_retriever.py` with retrieval tests
- [ ] Test: search query returns chunk IDs and payloads from Qdrant
- [ ] Commit: one commit for all Phase 03 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 04 — Generation

- [ ] Create `backend/app/llm/__init__.py`
- [ ] Create `backend/app/llm/base.py` with `LLMProvider` interface (base class)
- [ ] Create `backend/app/llm/groq.py` with `GroqProvider` adapter
- [ ] Create `backend/app/llm/opencode_zen.py` with `OpenCodeZenProvider` adapter
- [ ] Create `backend/app/rag/generator.py` with `generate_answer(context, question, provider) -> str`
- [ ] Create `backend/tests/unit/test_llm_base.py` with interface tests
- [ ] Create `backend/tests/unit/test_llm_groq.py` with mock Groq tests
- [ ] Create `backend/tests/unit/test_llm_opencode_zen.py` with mock OpenCode Zen tests
- [ ] Create `backend/tests/unit/test_generator.py` with generation tests
- [ ] Test: given context + question, generate answer returns a string
- [ ] Commit: one commit for all Phase 04 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 05 — Storage

- [ ] Create `backend/app/storage.py` with SQLite tables: documents, chats, messages
- [ ] Create CRUD helpers: `create_document()`, `get_document()`, `list_documents()`, `delete_document()`
- [ ] Create CRUD helpers: `create_chat()`, `list_chats()`, `get_chat_messages()`, `delete_chat()`
- [ ] Create CRUD helpers: `create_message()`, `get_messages_by_chat()`
- [ ] Create `backend/tests/unit/test_storage.py` with all CRUD tests
- [ ] Test: in-memory SQLite, create/read/delete operations work
- [ ] Commit: one commit for all Phase 05 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 06 — API

- [ ] Create `backend/app/api/__init__.py`
- [ ] Create `backend/app/api/auth.py` with `POST /api/v1/auth/models`
- [ ] Create `backend/app/api/documents.py` with document endpoints
- [ ] Create `backend/app/api/query.py` with `POST /api/v1/query`
- [ ] Create `backend/app/api/chats.py` with chat endpoints
- [ ] Wire all routers into `backend/app/main.py`
- [ ] Create `backend/tests/api/test_auth.py`
- [ ] Create `backend/tests/api/test_documents.py`
- [ ] Create `backend/tests/api/test_query.py`
- [ ] Create `backend/tests/api/test_chats.py`
- [ ] Test: all endpoints return correct response shapes
- [ ] Commit: one commit for all Phase 06 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 07 — Frontend Login

- [ ] Create `backend/static/login.html` with provider dropdown + API key input
- [ ] Create `backend/static/login.js` with connect flow + model fetch
- [ ] Create `backend/static/style.css` with login page styles
- [ ] Test: login page renders, connect calls `/api/v1/auth/models`
- [ ] Test: invalid key shows error, valid key shows model dropdown
- [ ] Test: selecting model + clicking Start Chatting redirects to index.html
- [ ] Commit: one commit for all Phase 07 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 08 — Frontend Chat

- [ ] Create `backend/static/index.html` with chat layout (sidebar + main area)
- [ ] Create `backend/static/app.js` with chat message rendering
- [ ] Create `backend/static/logo.png`
- [ ] Update `backend/static/style.css` with chat page styles
- [ ] Test: message input sends to `/api/v1/query`
- [ ] Test: assistant response renders in chat area with citations
- [ ] Test: citations are clickable and open source modal
- [ ] Commit: one commit for all Phase 08 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 09 — Frontend Documents

- [ ] Add documents section to sidebar in `index.html`
- [ ] Add document upload button + file select
- [ ] Add document list with status indicators
- [ ] Add document delete button
- [ ] Update `app.js` with document CRUD logic
- [ ] Test: upload shows processing state
- [ ] Test: document list updates after upload/delete
- [ ] Test: delete calls `/api/v1/documents/{id}`
- [ ] Commit: one commit for all Phase 09 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 10 — Frontend History

- [ ] Add history section to sidebar in `index.html`
- [ ] Add `+ New Chat` button
- [ ] Add chat list with load/delete actions
- [ ] Update `app.js` with chat CRUD logic
- [ ] Test: new chat creates a new chat and loads empty messages
- [ ] Test: load chat loads messages from that chat
- [ ] Test: delete chat removes from list
- [ ] Commit: one commit for all Phase 10 files
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 11 — Tests

- [ ] Review and expand all unit tests
- [ ] Review and expand all API tests
- [ ] Run full test suite and verify no live API calls
- [ ] Run coverage report and verify 80%+ line coverage
- [ ] Fix any failing tests
- [ ] Commit: one commit for test improvements
- [ ] Update TRACKER.md with DONE status and commit hash

## Phase 12 — Polish

- [ ] Add README screenshots (login page, chat page)
- [ ] Add error states: invalid API key, provider unreachable, no documents
- [ ] Add loading states: model fetch, document upload, query in progress
- [ ] Run final smoke test: full flow from login to chat
- [ ] Review all docs for accuracy and cross-references
- [ ] Update README with screenshots and final setup instructions
- [ ] Commit: one commit for polish
- [ ] Update TRACKER.md with DONE status and commit hash
