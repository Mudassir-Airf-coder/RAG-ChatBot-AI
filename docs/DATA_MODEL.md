# Data Model — RAG Chatbot

## Qdrant collection

### Collection naming
- Collection name configured in `backend/app/config.py`
- v1 assumes one collection for all document chunks.

### Vector configuration
- One named vector (single dense vector)
- Name example: `"dense"` (the exact vector name must be constant in code)

### ID format
- Chunk ids are stored in Qdrant as strings.
- Format:
  - `chunk_{document_id}_{chunk_index}`
  - Example: `chunk_doc_20260916_001_3`

### Chunk ID determinism

`chunk_id` is **deterministic**, not random. The same document combined with the same chunk index always produces the same `chunk_id`.

Format:
```
chunk_{document_id}_{chunk_index}
```

Example:
```
chunk_doc_20260916_001_3
```

Why deterministic:
- Re-uploading the same document does not create duplicate chunks
- Citations remain stable across re-indexing
- Debugging is easier because IDs are human-readable

### Payload fields
Each Qdrant point payload must include:
- `document_id`: string
- `chunk_id`: string (same as the Qdrant point id)
- `chunk_index`: integer
- `chunk_text`: string — the full text of this chunk
- `metadata`: object with at minimum:
  - `source`: original filename
  - optional extraction info (e.g., PDF page)

The payload must be sufficient to:
- map retrieval results back to chunk inspection endpoint
- build citations metadata (document_id + chunk_id)

### Payload example
```json
{
  "document_id": "doc_20260916_001",
  "chunk_id": "chunk_doc_20260916_001_3",
  "chunk_index": 3,
  "chunk_text": "The full text of this specific chunk goes here...",
  "metadata": {"source":"example.pdf","page":12}
}
```

## SQLite schema

SQLite file path configured in `backend/app/config.py`.

### Table: `documents`
Column definitions:
- `id` TEXT PRIMARY KEY
- `filename` TEXT NOT NULL
- `status` TEXT NOT NULL
  - allowed values: `PROCESSING`, `READY`, `FAILED`
- `error_message` TEXT NULL
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

### Table: `chats`
- `id` TEXT PRIMARY KEY
- `title` TEXT NOT NULL
- `created_at` TEXT NOT NULL
- `updated_at` TEXT NOT NULL

### Table: `messages`
Stores both user and assistant messages.
- `id` TEXT PRIMARY KEY
- `chat_id` TEXT NOT NULL (FK to chats.id)
- `role` TEXT NOT NULL
  - allowed values: `user`, `assistant`
- `content` TEXT NOT NULL
- `citations` TEXT NOT NULL
  - JSON-encoded array of citations objects
- `created_at` TEXT NOT NULL

Index suggestions:
- `messages.chat_id`
- `chats.updated_at`

## Disk layout
Configured upload root directory (example: `uploads/`).

### Document directory
- `uploads/{document_id}/`
  - `original/{filename}`

