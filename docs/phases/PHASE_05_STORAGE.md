# Phase 05 — Storage

## Goal
Build the SQLite storage layer: tables for documents, chats, and messages, plus CRUD helpers for all operations.

## Files to create or modify
- `backend/app/storage.py` — SQLite schema and CRUD helpers
- `backend/tests/unit/test_storage.py` — All CRUD tests

## Interfaces to define

### `backend/app/storage.py`

#### Document operations
```python
def create_document(
    document_id: str,
    filename: str,
    status: str = "PROCESSING",
    error_message: str | None = None,
) -> dict:
    """Create a document record. Returns created document dict."""
    ...

def get_document(document_id: str) -> dict | None:
    """Get document by ID."""
    ...

def list_documents() -> list[dict]:
    """List all documents ordered by created_at desc."""
    ...

def update_document_status(
    document_id: str,
    status: str,
    error_message: str | None = None,
) -> None:
    """Update document status."""
    ...

def delete_document(document_id: str) -> None:
    """Delete document record."""
    ...
```

#### Chat operations
```python
def create_chat(
    chat_id: str,
    title: str = "New chat",
) -> dict:
    """Create a chat record."""
    ...

def list_chats() -> list[dict]:
    """List all chats ordered by updated_at desc."""
    ...

def get_chat(chat_id: str) -> dict | None:
    """Get chat by ID."""
    ...

def update_chat_timestamp(chat_id: str) -> None:
    """Update chat updated_at timestamp."""
    ...

def delete_chat(chat_id: str) -> None:
    """Delete chat record and its messages."""
    ...
```

#### Message operations
```python
def create_message(
    message_id: str,
    chat_id: str,
    role: str,
    content: str,
    citations: list[dict] | None = None,
) -> dict:
    """Create a message record."""
    ...

def get_messages_by_chat(chat_id: str) -> list[dict]:
    """Get all messages for a chat, ordered by created_at."""
    ...
```

#### Database initialization
```python
def init_db(sqlite_path: str) -> None:
    """Create tables if they don't exist."""
    ...
```

## Tests required
- `backend/tests/unit/test_storage.py`
  - Test: `create_document` returns created document with correct fields
  - Test: `get_document` returns None for nonexistent ID
  - Test: `list_documents` returns all documents ordered by created_at
  - Test: `update_document_status` changes status field
  - Test: `delete_document` removes record
  - Test: `create_chat` returns created chat
  - Test: `list_chats` returns chats ordered by updated_at
  - Test: `update_chat_timestamp` updates updated_at
  - Test: `delete_chat` removes chat and its messages
  - Test: `create_message` stores citations as JSON
  - Test: `get_messages_by_chat` returns messages in order
  - Test: in-memory SQLite is used for all tests (no file on disk)

## Manual verification
```bash
# Once Phase 06 wires the endpoint
curl -s http://localhost:8000/api/v1/documents
```
Expected:
```json
{"documents": []}
```

## Definition of Done
- [ ] SQLite tables created: documents, chats, messages
- [ ] All CRUD helpers work correctly
- [ ] In-memory SQLite used in tests
- [ ] All tests pass

## Evidence to record
- Paste test output in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: SQLite schema issues, CRUD logic bugs
- Report to: human

## Do NOT
- Do not create API endpoints yet
- Do not create frontend files yet
- Do not implement RAG pipeline yet
