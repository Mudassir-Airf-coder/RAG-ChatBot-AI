# RAG Chatbot

A local-first RAG (retrieval-augmented generation) chatbot that lets a user upload documents, then ask questions grounded in those documents.

- Single-user workflow (local developer/demo user)
- Documents are embedded locally and indexed in Qdrant
- Chats and document metadata are stored in SQLite
- LLM provider: **Groq**

## Quick start

```bash
./run.sh
```

Then open http://localhost:8000/login.html

**Prerequisites:** Python 3.11+, `uv`, Docker

## Documentation

- `docs/ARCHITECTURE.md` - System design
- `docs/SPECIFICATION.md` - Requirements
- `docs/API.md` - Endpoint reference
- `docs/DATA_MODEL.md` - Schema
- `docs/SETUP.md` - Detailed setup
