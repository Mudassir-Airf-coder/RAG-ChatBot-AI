# Specification — RAG Chatbot (v1)

## Feature list (v1)

### UI / UX
1. Login page
   - Provider dropdown: **Groq**
   - API key input (password field)
   - Connect button validates key by calling provider `/models`
   - Model dropdown populated on success
   - Redirect to chat page after model selection
2. Chat page
   - ChatGPT-style layout
   - Sidebar (toggleable)
     - `+ New Chat`
     - Documents: list + upload + delete
     - History: chat list + load + delete
   - Main area
     - Chat messages (user right, assistant left)
     - Citations under assistant messages
     - Input box + send
3. Document management
   - Upload file
   - Show status transitions: `PROCESSING` → `READY` | `FAILED`
   - List documents
   - Delete document
4. Source inspection
   - Click citation to open modal with full chunk text + metadata

### Backend functionality
1. Provider adapters
   - Groq adapter: OpenAI-compatible chat completions API
   - OpenCode Zen adapter: OpenAI-compatible chat completions API at human-confirmed base URL
2. RAG pipeline
   - Parse: PDF, MD, TXT, DOCX
   - Chunk: recursive, 500 chars, 50 overlap
   - Embeddings: local fastembed using `BAAI/bge-small-en-v1.5`
   - Vector DB: Qdrant dense-only retrieval
   - Context: top-K chunks returned by dense search
   - Generation: call the selected provider with context + question
3. Storage
   - SQLite stores documents + chat history
   - Qdrant stores chunk vectors with payload for mapping
   - Disk stores uploaded files for chunk inspection
4. Auth model
   - Session is API-key-based only
   - API key is stored in browser `sessionStorage`
   - No password database, no OAuth
5. Logging
   - Structured JSON logs
   - API key redaction in logs and error responses
6. Tests
   - pytest unit + API tests
   - default test run makes no live API calls

## Non-goals (explicitly excluded)
- Streaming responses in v1
- Hybrid (dense + sparse) retrieval
- Sparse retrieval, rerankers, or sparse indices
- Multi-tenant user accounts
- Any OAuth/password-based auth
- Next.js/React/Streamlit frameworks
- Docker-heavy orchestration beyond a Qdrant container
- Public demo deployment in v1
- “Fallback providers” (no fallback chain; exactly one provider per session)

## User flows

### Flow 1 — Login
1. User opens `http://localhost:8000/`
2. `login.html` shows:
   - Dropdown: **Groq** | **OpenCode Zen**
   - API Key input (password field)
   - Connect button
3. Backend validates:
   - Calls provider `GET {base_url}/models`
4. On success:
   - Model dropdown populated
5. On failure:
   - Error message shown, no redirect
6. User selects model
7. User clicks **Start Chatting**
8. Frontend redirects to `index.html`
9. Frontend stores in `sessionStorage`:
   - `{ provider, api_key, model }`

### Flow 2 — Chat
1. User types question and clicks Send
2. Frontend calls `POST /api/v1/query`
3. Backend:
   - Embed query
   - Search Qdrant (dense-only)
   - Build context (top-K chunks)
   - Call the selected LLM provider
4. Backend stores:
   - message + citations metadata in SQLite
   - chat updated timestamps (in SQLite)
5. Frontend renders:
   - assistant answer
   - citations as clickable items

### Flow 3 — Document Management
1. Upload: user selects file → `POST /api/v1/documents/upload`
2. Backend sets status:
   - `PROCESSING` first
   - then `READY` or `FAILED`
3. Documents list updates in the UI
4. Delete: user clicks delete → `DELETE /api/v1/documents/{id}`
5. Backend removes from:
   - Qdrant vectors for that document
   - SQLite document record
   - disk uploaded file

### Flow 4 — Source Inspection
1. User clicks citation [1]
2. Frontend calls:
   - `GET /api/v1/documents/{id}/chunks/{chunk_id}`
3. Backend returns full chunk text and metadata
4. Frontend displays modal

## Provider behavior

### Groq
- Base URL: `https://api.groq.com/openai/v1`
- Models endpoint: `GET {base_url}/models`
- Auth: `Authorization: Bearer {api_key}`
- Expected: OpenAI-compatible chat completions API

### OpenCode Zen

- Base URL: **PLACEHOLDER — to be provided by the human before Phase 04 begins**
- Expected shape: OpenAI-compatible endpoint at a URL like `https://<opencode-zen-domain>/v1`
- Models endpoint: `GET {base_url}/models`
- Auth: `Authorization: Bearer {api_key}`
- Adapter class name: `OpenCodeZenProvider` (do not rename)

**Action required before Phase 04:**
The human must provide the exact base URL. Until then:
- Phase 01–03 do NOT need this URL
- Phase 04 will implement the adapter with a `BASE_URL` constant that is read from environment variable `OPENCODE_ZEN_BASE_URL`
- If the variable is missing at runtime, the adapter raises a clear `ProviderError` with code `MISSING_BASE_URL`
- No hardcoded fallback URL is allowed

## Session model
- Browser `sessionStorage` stores:
  - `provider`: `groq` | ``
  - `api_key`: raw API key string
  - `model`: model id returned by `/models`
- Backend expects:
  - Frontend sends API key and model (or a derived auth header) for provider calls
- No persistent storage of the API key beyond this browser session in v1

## Error handling rules
1. Every error response uses a stable JSON envelope:
   - `{"error": {"code": "...", "message": "...", "details": {...}}}`
2. API key must never appear in logs or error messages.
3. Provider model validation failure:
   - `401` (invalid key)
   - `502` (provider unreachable)
   - `500` (unexpected provider response shape)
4. Document ingestion failures:
   - Document status set to `FAILED`
   - Upload returns document id + status
5. Query errors:
   - If no documents exist, return a clear error code (no fabricated context)

