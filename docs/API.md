# API — RAG Chatbot

All endpoints are under: ` /api/v1 `

Error response shape (used by every endpoint):

```json
{
  "error": {
    "code": "string",
    "message": "human-readable",
    "details": {
      "...": "optional"
    }
  }
}
```

## Conventions
- Successful responses use `200`, `201`, or `204` as listed.
- Request/response bodies are JSON unless noted.
- API key is never returned.
- API key provided by the frontend is used for provider validation or chat completions calls.

## Endpoints

### Health

#### GET `/api/v1/health`
Returns service status.

Request: none

Response `200`:
```json
{"status":"ok"}
```

Example:
```bash
curl -s http://localhost:8000/api/v1/health
```

---

### Auth / Models

#### POST `/api/v1/auth/models`
Fetch available models from the selected provider.

Request body:
```json
{
  "provider": "groq" ,
  "api_key": "<user api key>"
}
```

Response `200`:
```json
{
  "provider": "groq",
  "models": [
    "model-id-1",
    "model-id-2"
  ]
}
```

Error codes:
- `401_INVALID_API_KEY`
- `502_PROVIDER_UNREACHABLE`
- `500_PROVIDER_RESPONSE_SHAPE`

Example (Groq):
```bash
curl -s -X POST http://localhost:8000/api/v1/auth/models \
  -H 'Content-Type: application/json' \
  -d '{"provider":"groq","api_key":"'$GROQ_API_KEY'"}'
```

Expected error on invalid key (example):
```json
{
  "error": {
    "code": "401_INVALID_API_KEY",
    "message": "Invalid API key for provider",
    "details": {}
  }
}
```

---

### Documents

#### POST `/api/v1/documents/upload`
Upload a file for ingestion.

Request:
- `multipart/form-data`
- form field `file`: the uploaded document

Response `201`:
```json
{
  "id": "doc_...",
  "filename": "example.pdf",
  "status": "PROCESSING"
}
```

Status transition rules:
- After ingestion completes, the document record becomes `READY` or `FAILED`.

Error codes:
- `400_INVALID_FILE`
- `415_UNSUPPORTED_MEDIA_TYPE`
- `500_INGESTION_FAILED`

Example:
```bash
curl -s -X POST http://localhost:8000/api/v1/documents/upload \
  -F 'file=@./example.pdf'
```

---

#### GET `/api/v1/documents`
List documents.

Response `200`:
```json
{
  "documents": [
    {
      "id": "doc_...",
      "filename": "example.pdf",
      "status": "READY",
      "created_at": "2026-09-16T12:34:56Z"
    }
  ]
}
```

Error codes:
- `500_STORAGE_ERROR`

Example:
```bash
curl -s http://localhost:8000/api/v1/documents
```

---

#### DELETE `/api/v1/documents/{id}`
Delete a document from disk, SQLite, and Qdrant.

Path params:
- `id`: document id

Response `204`:
- empty body

Error codes:
- `404_NOT_FOUND`
- `500_STORAGE_ERROR`

Example:
```bash
curl -s -X DELETE http://localhost:8000/api/v1/documents/doc_123
```

---

#### GET `/api/v1/documents/{id}/chunks/{chunk_id}`
Return the full chunk text + metadata for source inspection.

Path params:
- `id`: document id
- `chunk_id`: chunk id within document

Response `200`:
```json
{
  "id": "chunk_...",
  "document_id": "doc_...",
  "chunk_index": 3,
  "text": "<full chunk text>",
  "metadata": {
    "source": "example.pdf",
    "page": 12
  }
}
```

Error codes:
- `404_NOT_FOUND`

Example:
```bash
curl -s http://localhost:8000/api/v1/documents/doc_123/chunks/chunk_456
```

---

### Query / Chat

#### POST `/api/v1/query`
Answer a user question using retrieved document context.

Request body:
```json
{
  "chat_id": "chat_...",
  "question": "What is ...?",
  "provider": "groq",
  "api_key": "<user api key>",
  "model": "model-id"
}
```

Response `200`:
```json
{
  "chat_id": "chat_...",
  "answer": "<assistant answer text>",
  "citations": [
    {
      "citation_index": 1,
      "document_id": "doc_...",
      "chunk_id": "chunk_...",
      "snippet": "<optional short snippet>"
    }
  ],
  "created_at": "2026-09-16T12:34:56Z"
}
```

Error codes:
- `400_BAD_REQUEST`
- `401_INVALID_API_KEY`
- `502_PROVIDER_UNREACHABLE`
- `404_CHAT_NOT_FOUND`
- `409_NO_DOCUMENT_CONTEXT` (no documents or no retrieval results)
- `500_QUERY_FAILED`

Example:
```bash
curl -s -X POST http://localhost:8000/api/v1/query \
  -H 'Content-Type: application/json' \
  -d '{
    "chat_id":"chat_123",
    "question":"Summarize the document.",
    "provider":"groq",
    "api_key":"'$GROQ_API_KEY'",
    "model":"llama-3.1-70b-versatile"
  }'
```

---

### Chats

#### GET `/api/v1/chats`
List chats.

Response `200`:
```json
{
  "chats": [
    {"id":"chat_...","title":"New chat","created_at":"...","updated_at":"..."}
  ]
}
```

Example:
```bash
curl -s http://localhost:8000/api/v1/chats
```

#### POST `/api/v1/chats`
Create a new chat.

Request body:
```json
{"title":"New chat"}
```

Response `201`:
```json
{"id":"chat_...","title":"New chat","created_at":"..."}
```

Example:
```bash
curl -s -X POST http://localhost:8000/api/v1/chats \
  -H 'Content-Type: application/json' \
  -d '{"title":"New chat"}'
```

#### GET `/api/v1/chats/{id}/messages`
Get messages for a chat.

Response `200`:
```json
{
  "chat_id": "chat_...",
  "messages": [
    {
      "id": "msg_...",
      "role": "user",
      "content": "...",
      "created_at": "..."
    },
    {
      "id": "msg_...",
      "role": "assistant",
      "content": "...",
      "citations": [
        {"citation_index":1,"document_id":"doc_...","chunk_id":"chunk_..."}
      ],
      "created_at": "..."
    }
  ]
}
```

#### DELETE `/api/v1/chats/{id}`
Delete a chat and its messages.

Response `204`

Error codes:
- `404_NOT_FOUND`

Example:
```bash
curl -s -X DELETE http://localhost:8000/api/v1/chats/chat_123
```

