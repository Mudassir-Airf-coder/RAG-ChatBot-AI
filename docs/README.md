# Project Documentation

This folder contains all project documentation, split into two audiences:

## 📁 Structure

```
docs/
├── agents/          # Documentation for AI coding agents
│   ├── AGENT.md          # Instructions for AI agents working on this project
│   ├── SESSIONS.md       # Log of all AI agent sessions
│   ├── TRACKER.md        # Phase tracker with status and evidence
│   ├── TASKS.md          # Task list with priorities
│   └── HANDOFF.md        # Handover document for next agent
└── humans/         # Documentation for human developers
    ├── OVERVIEW.md       # What this project is and why it exists
    ├── DESIGN.md         # UI/UX design, user flows, state management
    ├── FLOW.md           # Data flows with diagrams
    ├── ARCHITECTURE.md   # Layer diagram, folder structure, key decisions
    ├── SETUP.md          # Prerequisites, step-by-step setup, env vars
    ├── API.md            # Full endpoint reference with curl examples
    ├── DATA_MODEL.md     # Qdrant, SQLite, localStorage schemas
    ├── TESTING.md        # How to run tests, test categories
    └── TROUBLESHOOTING.md # Common errors and fixes
```

## 🎯 Where to Start

| Audience | Start Here |
|----------|------------|
| **Human developers** | [humans/OVERVIEW.md](humans/OVERVIEW.md) |
| **AI coding agents** | [agents/AGENT.md](agents/AGENT.md) |

## 📋 Project Status

- **Backend**: FastAPI + Python 3.11+, 98 tests passing
- **Frontend**: Single-file HTML/CSS/JS (dark theme)
- **RAG Pipeline**: Cohere embeddings → Qdrant → Groq LLM
- **Tests**: 98 passing
- **License**: MIT

See [humans/OVERVIEW.md](humans/OVERVIEW.md) for full project description.