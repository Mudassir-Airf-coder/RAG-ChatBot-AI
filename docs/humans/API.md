# API Reference

Base URL: `http://localhost:8000/api/v1`

All endpoints require `Content-Type: application/json` unless multipart.

Authentication: Session cookie `rag_session` (HttpOnly, set by `/provider/config`).

---

## Health

### GET `/health`

Check service status.

```bash
curl http://localhost:8000/api/v1/health
```

**Response** (200):
```json
{"status": "ok"}
```

---

## Documents

### POST `/documents/upload`

Upload a document for processing. Returns 202 Accepted immediately; processing happens in background.

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -b "rag_session=<cookie>" \
  -F "file=@document.pdf"
```

**Request**: `multipart/form-data`
- `file` (required): PDF, MD, TXT, or DOCX

**Response** (202):
```json
{"id": "doc_abc123", "filename": "document.pdf", "status": "UPLOADED"}
```

**Errors**:
- 400: No file, file too large (>2GB), no Cohere key configured
- 413: File exceeds `MAX_UPLOAD_MB` (default 2048 MB)

### GET `/documents`

List all uploaded documents.

```bash
curl -b "rag_session=<cookie>" http://localhost:8000/api/v1/documents
```

**Response** (200):
```json
{"documents": [{"id": "doc_abc123", "filename": "document.pdf", "status": "READY", "error_message": null, "created_at": "2026-09-22T10:00:00Z", "updated_at": "2026-09-22T10:00:05Z"}]}
```

**Status values**: `UPLOADED`, `PROCESSING`, `READY`, `FAILED`

### GET `/documents/{id}`

Get document details including chunk count when ready.

```bash
curl -b "rag_session=<cookie>" http://localhost:8000/api/v1/documents/doc_abc123
```

**Response** (200):
```json
{"id": "doc_abc123", "filename": "document.pdf", "status": "READY", "error_message": null, "created_at": "2026-09-22T10:00:00Z", "updated_at": "2026-09-22T10:00:05Z", "chunk_count": 13}
```

### DELETE `/documents/{id}`

Delete a document (removes from Qdrant, SQLite, and disk).

```bash
curl -X DELETE -b "rag_session=<cookie>" http://localhost:8000/api/v1/documents/doc_abc123
```

**Response** (204 No Content)

**Errors**: 404: Document not found

---

## Query

### POST `/query`

Ask a question about uploaded documents.

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -b "rag_session=<cookie>" \
  -d '{"question": "What is the license?"}'
```

**Request**: `{"question": "What is the license?"}`

**Response** (200):
```json
{"answer": "The license is MIT. [1]", "citations": [{"citation_index": 1, "document_id": "doc_abc123", "chunk_id": "chunk_doc_abc123_0", "document_name": "LICENSE.md", "page": null, "quote": "MIT License\n\nCopyright (c)..."}], "abstained": false, "abstain_reason": null, "rewritten_query": null}
```

**Fields**:
- `answer`: LLM response with inline `[N]` citations
- `citations`: Array of cited chunks (only those actually cited)
- `abstained`: True if LLM couldn't find answer
- `abstain_reason`: `"no_documents"` or `"llm_abstained"`
- `rewritten_query`: The rewritten query if different from original

**Errors**: 400: No LLM config, no Cohere key, empty question; 502: LLM/Cohere upstream error

### Intent Behavior

| Query Example | Intent | Rewrite? | Top-K | Temp |
|---------------|--------|----------|-------|------|
| "what is the license?" | knowledge | No | 10 | 0.1 |
| "so you write this docs as is" | verbatim | No | 15 | 0.0 |
| "act as teacher" | teach | No | 10 | 0.2 |
| "summarize this" | summarize | No | 12 | 0.1 |
| "compare A and B" | compare | No | 10 | 0.1 |
| "hi" | knowledge | Yes → "What is this document about?" | 10 | 0.1 |

---

## Provider Configuration

### POST `/provider/models`

Fetch available models for a provider.

```bash
curl -X POST http://localhost:8000/api/v1/provider/models -H "Content-Type: application/json" -d '{"base_url": "https://api.groq.com/openai/v1", "api_key": "gsk_xxx"}'
```

**Response** (200): `{"models": ["llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]}`

### POST `/provider/test`

Test LLM connection.

```bash
curl -X POST http://localhost:8000/api/v1/provider/test -H "Content-Type: application/json" -d '{"base_url": "https://api.groq.com/openai/v1", "api_key": "gsk_xxx", "model": "llama-3.1-8b-instant"}'
```

**Response** (200): `{"ok": true, "message": "Connection successful"}` or `{"ok": false, "error": "Invalid API key"}`

### POST `/provider/test/cohere`

Test Cohere embedding connection.

```bash
curl -X POST http://localhost:8000/api/v1/provider/test/cohere -H "Content-Type: application/json" -d '{"base_url": "", "api_key": "sk-xxx", "model": "embed-english-v3.0"}'
```

**Response** (200): `{"ok": true, "message": "Cohere connection successful"}`

### POST `/provider/config`

Save provider configuration (LLM + Cohere). Merges with existing session.

```bash
# LLM only
curl -X POST http://localhost:8000/api/v1/provider/config -H "Content-Type: application/json" -d '{"name":"Groq","base_url":"https://api.groq.com/openai/v1","api_key":"gsk_xxx","model":"llama-3.1-8b-instant"}'

# Cohere only (merges with existing LLM config)
curl -X POST http://localhost:8000/api/v1/provider/config -H "Content-Type: application/json" -b "rag_session=<cookie>" -d '{"cohere_api_key": "sk-xxx"}'
```

**Request** (all optional, merged with existing):
```json
{"name": "Groq", "base_url": "https://api.groq.com/openai/v1", "api_key": "gsk_xxx", "model": "llama-3.1-8b-instant", "cohere_api_key": "sk-xxx"}
```

**Response** (200): `{"ok": true, "llm_configured": true, "cohere_configured": true}`

**Errors**: 400: No LLM fields provided, or no config at all. Sets `rag_session` HttpOnly cookie on success.

---

## Error Format

All errors follow this structure:

```json
{"error": {"code": "VALIDATION_ERROR", "message": "Human-readable message", "details": {}}}
```

| Code | HTTP | Meaning |
|------|------|---------|
| `VALIDATION_ERROR` | 400 | Bad request / missing config |
| `NOT_FOUND` | 404 | Resource not found |
| `PROVIDER_ERROR` | 502 | Upstream API error |
| `PARSING_ERROR` | 400 | Document parsing failed |
| `VECTOR_DB_ERROR` | 500 | Qdrant error |
| `STORAGE_ERROR` | 500 | SQLite error |

---

## WebSocket (Future)

Currently HTTP polling for document status. WebSocket endpoint planned:

```
GET /ws/documents/{id}/status
```

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/provider/models` | 10/min |
| `/provider/test` | 5/min |
| `/provider/test/cohere` | 5/min |
| `/provider/config` | 30/min |
| `/documents/upload` | 10/min |
| `/query` | 60/min |

---

## Curl Cheat Sheet

```bash
COOKIE_JAR="cookie.txt"

# 1. Configure LLM
curl -X POST http://localhost:8000/api/v1/provider/config -H "Content-Type: application/json" -c $COOKIE_JAR -d '{"name":"Groq","base_url":"https://api.groq.com/openai/v1","api_key":"gsk_xxx","model":"llama-3.1-8b-instant"}'

# 2. Configure Cohere
curl -X POST http://localhost:8000/api/v1/provider/config -H "Content-Type: application/json" -b $COOKIE_JAR -c $COOKIE_JAR -d '{"cohere_api_key":"sk-xxx"}'

# 3. Upload
curl -X POST -b $COOKIE_JAR -c $COOKIE_JAR -F "file=@doc.pdf" http://localhost:8000/api/v1/documents/upload

# 4. Poll for ready
for i in {1..50}; do STATUS=$(curl -s -b $COOKIE_JAR http://localhost:8000/api/v1/documents/$DOC_ID | jq -r .status); echo "Status: $STATUS"; [[ "$STATUS" == "READY" ]] && break; [[ "$STATUS" == "FAILED" ]] && break; sleep 2; done

# 5. Query
curl -X POST -b $COOKIE_JAR -H "Content-Type: application/json" -d '{"question":"What is the license?"}' http://localhost:8000/api/v1/query | jq .
```