# Data Models

## Qdrant Collection: `rag_chatbot_cohere`

### Collection Config

```json
{
  "vectors": { "size": 1024, "distance": "Cosine" },
  "hnsw_config": { "m": 16, "ef_construct": 100 },
  "optimizer_config": { "deleted_threshold": 0.2, "vacuum_min_vector_number": 1000 }
}
```

### Point Structure

```json
{
  "id": "f7ce7713-3422-5b6b-bbdb-b15084c0dc44",
  "vector": [0.1, 0.2, ...],
  "payload": {
    "document_id": "doc_abc123",
    "chunk_id": "chunk_doc_abc123_5",
    "chunk_index": 5,
    "chunk_text": "The license is MIT...",
    "metadata": { "source": "LICENSE.md", "page": 1 }
  }
}
```

### Point ID Generation

Deterministic UUID5 from namespace + `chunk_{doc_id}_{chunk_index}`:

```python
_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
point_id = str(uuid.uuid5(_NAMESPACE, f"chunk_{doc_id}_{chunk['index']}"))
```

### Collection Management

- Auto-created on first upsert (`create_collection` in `vectorstore.py`)
- Dimension: 1024 (Cohere embed-english-v3.0)
- Distance: Cosine
- One collection per deployment (no multi-tenancy)

---

## SQLite Schema (`data/chatbot.db`)

### Table: `documents`

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,           -- UPLOADED, PROCESSING, READY, FAILED
    error_message TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### Table: `chats`

```sql
CREATE TABLE chats (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT 'New chat',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### Table: `messages`

```sql
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    citations TEXT,
    abstained INTEGER DEFAULT 0,
    abstain_reason TEXT,
    rewritten_query TEXT,
    error INTEGER DEFAULT 0,
    ts TEXT NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chats(id)
);
```

### Indexes

```sql
CREATE INDEX idx_messages_chat_id ON messages(chat_id);
CREATE INDEX idx_messages_ts ON messages(ts);
CREATE INDEX idx_documents_status ON documents(status);
```

---

## localStorage (Frontend)

### `rag.chats.v1` — Chat List

```json
[{"id": "chat_abc123", "title": "License questions", "created": 1699999999999, "updated": 1699999999999}]
```

### `rag.active_chat.v1` — Active Chat ID

```json
"chat_abc123"
```

### `rag.messages.{chat_id}` — Per-Chat Messages

```json
[{"role": "user", "content": "What is the license?", "ts": 1699999999999}, {"role": "assistant", "content": "The license is MIT. [1]", "citations": [{"citation_index": 1, "document_id": "doc_abc", "chunk_id": "chunk_xyz"}], "abstained": false, "rewritten_query": null, "ts": 1699999999999}]
```

### `rag_config` — LLM Provider Config

```json
{"name": "Groq", "base_url": "https://api.groq.com/openai/v1", "api_key": "gsk_xxx", "model": "llama-3.1-8b-instant"}
```

### `rag_cohere_key` — Cohere API Key

```json
"ijYteUqLQnnqwaWCXiHqLczeKhJ6C4MvD0KKCOvu"
```

---

## Server-Side Sessions (`data/sessions.json`)

```json
{ "session_hex_id": { "name": "Groq", "base_url": "https://api.groq.com/openai/v1", "api_key": "gsk_xxx", "model": "llama-3.1-8b-instant", "cohere_api_key": "sk-xxx" } }
```

- Key: random hex (from `uuid.uuid4().hex`)
- Value: merged LLM + Cohere config
- Persisted to `data/sessions.json` on every save
- Loaded on startup

### Cookie

| Attribute | Value |
|-----------|-------|
| Name | `rag_session` |
| Value | Session hex ID |
| HttpOnly | Yes |
| SameSite | Lax |
| Path | `/` |
| Secure | No (localhost) |
| Max-Age | Session (browser close) |

---

## File Upload Structure

```
backend/uploads/
├── doc_abc123/ └── document.pdf
├── doc_def456/ └── notes.md
└── doc_ghi789/ └── report.docx
```

- Created on upload: `uploads/{doc_id}/{original_filename}`
- Deleted on document deletion (best effort)
- Max file size: 2048 MB (configurable)

---

## Qdrant Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `document_id` | string | FK to documents table |
| `chunk_id` | string | `chunk_{doc_id}_{index}` |
| `chunk_index` | int | Global chunk index (0-based) |
| `chunk_text` | string | Full chunk text |
| `metadata` | object | `{source, page, ...}` from parser |

---

## Embedding Vector

- Provider: Cohere `embed-english-v3.0`
- Dimension: 1024
- Batch size: 96
- Input types: `search_document` (chunks), `search_query` (queries)
- Truncation: `END` (Cohere default)

---

## Chunking Parameters

| Parameter | Value | Config |
|-----------|-------|----------|
| Chunk size | 800 chars | `CHUNK_SIZE` |
| Overlap | 100 chars | `CHUNK_OVERLAP` |
| Max chunks/doc | 2000 | `MAX_CHUNKS_PER_DOC` |
| Context chunks | 6 | `MAX_CONTEXT_CHUNKS` |
| Retrieval top-K | 10 | `RETRIEVAL_TOP_K` |

### Chunk Index

- Global sequential index across all pages (0, 1, 2, ...)
- Used in point ID: `chunk_{doc_id}_{index}`
- Stored in `chunk_index` payload field

---

## Session Cookie

| Attribute | Value |
|-----------|-------|
| Name | `rag_session` |
| Value | Session hex ID |
| HttpOnly | Yes |
| SameSite | Lax |
| Path | `/` |
| Secure | No (localhost) |
| Max-Age | Session (browser close) |

---

## Chats Table (Frontend localStorage)

### `rag.chats.v1`

```json
[{"id": "chat_abc", "title": "License questions", "created": 1699999999, "updated": 1699999999}]
```

### `rag.active_chat.v1`

```json
"chat_abc"
```

### `rag.messages.chat_abc`

```json
[{"role": "user", "content": "What is the license?", "ts": 1699999999}, {"role": "assistant", "content": "MIT [1]", "citations": [...], "abstained": false, "ts": 1699999999}]
```

---

## Query Request/Response

### Request

```json
{"question": "What is the license?"}
```

### Response

```json
{
  "answer": "The license is MIT. [1]",
  "citations": [{"citation_index": 1, "document_id": "doc_abc", "chunk_id": "chunk_doc_abc_0", "document_name": "LICENSE.md", "page": 1, "quote": "MIT License..."}],
  "abstained": false,
  "abstain_reason": null,
  "rewritten_query": null
}
```

---

## Citation Shape (Frontend)

```typescript
interface Citation {
  citation_index: number;
  document_id: string;
  chunk_id: string;
  document_name: string;
  page: number | null;
  quote: string;
}
```

---

## Document Status Enum

| Value | Meaning |
|-------|---------|
| `UPLOADED` | File saved, not yet processed |
| `PROCESSING` | Parse/chunk/embed/index in progress |
| `READY` | Successfully indexed, queryable |
| `FAILED` | Error during processing (see `error_message`) |

---

## Error Response

```json
{ "error": { "code": "VALIDATION_ERROR", "message": "Configure Cohere API key first", "details": {} } }
```

| Code | HTTP | Context |
|------|------|---------|
| `VALIDATION_ERROR` | 400 | Missing config, bad input |
| `NOT_FOUND` | 404 | Document/chat not found |
| `PROVIDER_ERROR` | 502 | Upstream API failure |
| `PARSING_ERROR` | 400 | PDF parse failed |
| `VECTOR_DB_ERROR` | 500 | Qdrant error |
| `STORAGE_ERROR` | 500 | SQLite error |