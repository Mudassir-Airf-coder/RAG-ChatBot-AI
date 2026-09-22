# Task List

## Completed Tasks

| Task | Commit | Evidence |
|------|--------|----------|
| Fix parser: capture page_count before doc.close() | 421b9b4 | `grep page_count app/rag/parser.py` |
| Fix global chunk index for Qdrant point IDs | 6781d52 | `grep chunk_index app/api/documents.py` |
| Replace fastembed with Cohere cloud embeddings | 7f9cce5 | `ls app/embeddings/` |
| Add intent classification (5 categories) | 1a305b2 | `ls app/rag/intent.py` |
| Add query rewriter with typo fixing | 1a305b2 | `grep rewrite_query app/rag/query_rewriter.py` |
| Per-intent system prompts (5 categories) | 1a305b2 | `grep PROMPTS app/rag/generator.py` |
| Query pipeline uses intent | 1a305b2 | `grep classify_intent app/api/query.py` |
| Sticky header + input, scrollable messages | 7a3d8f8 | `grep min-height:0 backend/static/index.html` |
| Inline clickable citations [1][2] | 7a3d8f8 | `grep inline-cite backend/static/index.html` |
| Chat history sidebar with persistence | 7a3d8f8 | `grep STORAGE_CHATS backend/static/index.html` |
| Provider config in localStorage + cookie | 7a3d8f8 | `grep localStorage backend/static/index.html` |
| OCR fallback for scanned PDFs | 7f9cce5 | `grep _parse_pdf_ocr app/rag/parser.py` |
| Multiple extraction modes (text/blocks/dict) | 7f9cce5 | `grep get_text.*blocks app/rag/parser.py` |
| Global chunk index (fix Qdrant collisions) | 6781d52 | `grep chunk_index app/api/documents.py` |
| Parser page_count fix | 421b9b4 | `grep page_count app/rag/parser.py` |
| Clean frontend rewrite (no duplicates) | 7a3d8f8 | `wc -l backend/static/index.html` |
| Sticky header + input, scrollable messages | 7a3d8f8 | `grep min-height:0 backend/static/index.html` |
| Chat history sidebar with localStorage | 7a3d8f8 | `grep STORAGE_CHATS backend/static/index.html` |
| Provider config in localStorage + cookie | 7a3d8f8 | `grep localStorage backend/static/index.html` |
| OCR fallback for scanned PDFs | 7f9cce5 | `grep _parse_pdf_ocr app/rag/parser.py` |
| Multiple extraction modes | 7f9cce5 | `grep get_text.*blocks app/rag/parser.py` |
| Global chunk index fix | 6781d52 | `grep chunk_index app/api/documents.py` |
| Page count fix | 421b9b4 | `grep page_count app/rag/parser.py` |
| All 98 tests passing | various | `uv run pytest -q` |
| CI workflow | 7a3d8f8 | `ls .github/workflows/` |
| README rewrite | 7c157ee | `head -50 README.md` |
| Stale docs cleanup | 7de88b1 | `ls docs/` |
| uv.lock restore | 87811a7 | `ls backend/uv.lock` |
| Delete doc fix (real Request) | fa61c27 | `grep delete_doc app/api/documents.py` |
| Delete argument order fix | 9e316db | `grep delete_by_document_id app/rag/vectorstore.py` |
| Sticky UI fix | 7a3d8f8 | `grep min-height:0 backend/static/index.html` |

---

## In-Progress Tasks

| Task | Status | Blocker |
|------|--------|---------|
| Tesseract OCR system install | BLOCKED | Requires sudo |
| Streamlit demo | NOT_STARTED | — |
| Next.js UI | NOT_STARTED | — |
| Hybrid search (BM25 + dense) | NOT_STARTED | — |
| Streaming LLM responses | NOT_STARTED | — |
| Multi-user auth | NOT_STARTED | — |
| Document versioning | NOT_STARTED | — |
| Team workspaces | NOT_STARTED | — |

---

## Next Tasks (Prioritized)

| Priority | Task | Estimate |
|----------|------|----------|
| 1 | Install Tesseract OCR system package | 5 min |
| 2 | Add hybrid search (BM25 + dense) | 2 days |
| 3 | Add streaming LLM responses | 1 day |
| 4 | Add multi-user auth (JWT) | 3 days |
| 5 | Document versioning | 2 days |
| 6 | Next.js frontend rewrite | 1 week |
| 7 | Streamlit demo | 2 days |
| 8 | CLI installer | 1 day |
| 9 | Team workspaces | 3 days |
| 10 | Multi-user auth | 3 days |

---

## Blocked Tasks

| Task | Reason | Resolution |
|------|--------|------------|
| Tesseract OCR install | Requires sudo | Manual install needed |
| Streaming responses | Architectural change needed | Design first |
| Multi-user auth | Requires auth layer | Design first |
| Hybrid search | Requires BM25 index | Design first |

---

## Deferred / Nice-to-Have

- [ ] Document tagging/filtering
- [ ] Query analytics dashboard
- [ ] Export chat as PDF/MD
- [ ] Keyboard shortcuts
- [ ] Dark/light theme toggle
- [ ] Mobile responsive improvements
- [ ] Accessibility audit (WCAG)
- [ ] Internationalization (i18n)
- [ ] Plugin system for custom parsers
- [ ] Webhook notifications