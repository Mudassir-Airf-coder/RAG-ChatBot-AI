# RAG Chatbot

## What this project is
A local-first RAG (retrieval-augmented generation) chatbot that lets a user upload documents, then ask questions grounded in those documents.

- Single-user workflow (local developer/demo user)
- Documents are embedded locally and indexed in Qdrant
- Chats and document metadata are stored in SQLite
- Exactly two LLM providers: **Groq** and **OpenCode Zen**

## What this project is NOT
- Not a production SaaS
- Not multi-tenant
- Not a Next.js or Streamlit application
- Not a collection of fallbacks and workarounds
- Not a solution that claims “done” without verification steps

## Screenshot
(Place a screenshot here after you have a working UI.)

## Quick setup (30-second version)
1. Prereqs: Python 3.11+, `uv`, Docker
2. Start Qdrant (Docker)
3. Configure providers in the app
4. Start the FastAPI backend
5. Open `http://localhost:8000/`

Detailed steps: `docs/SETUP.md`

Deep dives:
- `docs/ARCHITECTURE.md`
- `docs/SPECIFICATION.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`

