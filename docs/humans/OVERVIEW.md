# RAG Chatbot — Overview

## What This Project Is

A local-first Retrieval-Augmented Generation (RAG) chatbot that lets you upload documents and ask questions about them. The system extracts text from your documents, converts it to vector embeddings using Cohere's cloud API, stores them in a local Qdrant vector database, and answers questions using Groq's LLM with citations pointing back to the source documents.

## Why It Exists

Most RAG solutions require complex infrastructure (Kubernetes, managed vector databases, cloud functions) or send your documents to third-party SaaS. This project gives you a complete RAG system that runs entirely on your machine with two external API calls (Cohere for embeddings, Groq for LLM). Your documents never leave your machine except for the API calls to generate embeddings and answers.

## What It Does

- **Upload documents**: PDF, Markdown, Text, DOCX (drag-and-drop or file picker)
- **Automatic processing**: Parses → chunks → embeds (Cohere) → indexes in Qdrant
- **Ask questions**: Natural language queries with inline citations [1][2][3]
- **Chat history**: Multiple conversations persisted in localStorage
- **Provider configuration**: Switch between Groq and OpenCode Zen LLMs; configure Cohere embeddings
- **Document management**: List, delete, view status (UPLOADED → PROCESSING → READY/FAILED)
- **Sticky UI**: Header and input stay fixed; only messages scroll

## What It Does NOT Do

| Non-Goal | Reason |
|----------|--------|
| Multi-user authentication | Local-first single-user design |
| Streaming responses | Simpler implementation; Groq supports streaming but adds complexity |
| OCR for scanned PDFs | Requires Tesseract system install; clear error message guides user |
| Hybrid search (BM25 + dense) | Dense-only with Cohere embeddings works well for semantic search |
| Multi-user / team workspaces | Local-first single-user design |
| Document versioning | Overwrite on re-upload; simple by design |
| Streaming LLM responses | Simpler implementation; Groq supports streaming but adds complexity |

## Who It's For

- Developers who want a working RAG system to study or extend
- Researchers who need to query local documents privately
- Anyone who wants a ChatGPT-like experience over their own documents without cloud dependencies

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Web Framework | FastAPI 0.115+ |
| Package Manager | uv |
| Vector Database | Qdrant (Docker) |
| Embeddings | Cohere embed-english-v3.0 (1024-dim, cloud) |
| LLM | Groq (llama-3.1-8b-instant, openai/gpt-oss-120b) / OpenCode Zen |
| Metadata DB | SQLite (chatbot.db) |
| Frontend | Vanilla HTML/CSS/JS (single file) |
| Styling | Custom CSS variables, dark theme |
| Testing | pytest + pytest-asyncio (98 tests) |
| Package Manager | uv |
| Container | Docker (Qdrant only) |

## Quick Start

```bash
# 1. Clone and enter
cd rag-chatbot

# 2. Start Qdrant + backend (one command)
./backend/run.sh

# 3. Open browser
open http://localhost:8000

# 4. Configure providers in UI (gear icon)
#    - LLM: Groq API key + model
#    - Embeddings: Cohere API key
# 5. Upload a document, wait for READY, ask questions
```

## Documentation Index

| Audience | Start Here | Full Index |
|----------|------------|------------|
| Humans | [OVERVIEW.md](OVERVIEW.md) | [humans/](./humans/) |
| AI Agents | [AGENT.md](../agents/AGENT.md) | [agents/](../agents/) |