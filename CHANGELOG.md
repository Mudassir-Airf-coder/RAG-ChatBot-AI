# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added
- Cohere cloud embeddings (`embed-english-v3.0`, 1024-dim)
- Groq LLM integration with two-section provider UI
- Async document ingestion with background processing
- Chat history with localStorage persistence
- Citation rendering with source inspection modal
- Scanned PDF detection with clear error message
- Intent classification (knowledge, summarize, verbatim, teach, compare)

### Fixed
- Chunk index collision causing Qdrant point overwrites
- Empty collection crash when no chunks extracted
- Parser crash on scanned PDFs (now raises ParsingError)
- Duplicate DELETE calls from frontend
- Config partial-save merge

### Changed
- Removed local fastembed (replaced with Cohere cloud)
- Chunk size 1500 → 800 chars, overlap 150 → 100
