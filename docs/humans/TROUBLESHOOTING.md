# Troubleshooting

## Quick Diagnosis

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Server won't start | Port 8000 in use | `lsof -ti:8000 \| xargs kill -9` |
| Qdrant connection refused | Qdrant not running | `docker start rag-qdrant` |
| "PDF has N pages but no extractable text" | Scanned/image PDF | Install Tesseract OCR |
| "Invalid Cohere API key" | Wrong/missing key | Re-enter key in UI |
| "Invalid Groq API key" | Wrong/missing key | Re-enter key in UI |
| "Configure Cohere API key first" | Key not saved | Save in Embedding section |
| "Configure LLM provider first" | Key not saved | Save in LLM section |
| Upload stuck at PROCESSING | Cohere 429/500 | Wait, check logs |
| Query returns "couldn't find" | No docs / wrong intent | Upload docs, check status |
| Citations show but not clickable | JS error | Check console, reload |

---

## Server Issues

### Server Won't Start

```bash
lsof -ti:8000 | xargs kill -9
ps aux | grep uvicorn
```

### Qdrant Not Running

```bash
docker start rag-qdrant
# Or create new
docker run -d --name rag-qdrant -p 6333:6333 qdrant/qdrant
curl http://localhost:6333/collections
```

### Server Shuts Down Immediately

```bash
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
# Look for: startup_complete, then shutdown
# Common: ImportError, missing dependency, port conflict
```

---

## Document Processing Errors

### "PDF has N pages but no extractable text"

**Cause**: PDF is scanned/images only (no text layer).

**Fix**:
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract

# Python bindings
uv add pytesseract pillow
```

**Note**: OCR on 100-page PDF at 200 DPI takes ~2-5 minutes. Files >200 pages rejected.

### "PDF has N pages but OCR also failed"

**Cause**: Tesseract not installed or not in PATH.

```bash
which tesseract && tesseract --version
# If missing: sudo apt install tesseract-ocr / brew install tesseract
```

### "Document produces N chunks, exceeds limit of 2000"

**Cause**: Document too large for current chunk limit.

**Fix**:
```bash
# Option 1: Increase limit (backend/.env)
MAX_CHUNKS_PER_DOC=5000

# Option 2: Split PDF (pdftk, pdfseparate, or online tools)
```

### "Invalid Cohere API key"

**Cause**: Key invalid, expired, or not set.

**Fix**: 1. Get key at https://dashboard.cohere.com/api-keys
2. Enter in UI: Gear → Embedding Provider → API Key → Test Connection → Save
3. Or via API:
```bash
curl -X POST http://localhost:8000/api/v1/provider/config -H "Content-Type: application/json" -b "rag_session=<cookie>" -d '{"cohere_api_key": "sk-xxx"}'
```

### "Invalid Groq API key"

**Cause**: Groq key invalid or expired.

**Fix**: 1. Get key at https://console.groq.com/keys
2. Enter in UI: Gear → LLM Provider → API Key → Fetch Models → Select → Test → Save

### "Configure Cohere API key first"

**Cause**: Cohere key not configured or session expired.

**Fix**: Gear → Embedding Provider → Enter key → Test Connection → Save. Or via API:
```bash
curl -X POST http://localhost:8000/api/v1/provider/config -H "Content-Type: application/json" -b "rag_session=<cookie>" -d '{"cohere_api_key": "sk-xxx"}'
```

### "Configure LLM provider first (Groq or OpenCode Zen)"

**Cause**: No LLM config saved.

**Fix**: Gear → LLM Provider → Fill all fields → Fetch Models → Select → Test → Save. Or via API:
```bash
curl -X POST http://localhost:8000/api/v1/provider/config -H "Content-Type: application/json" -d '{"name":"Groq","base_url":"https://api.groq.com/openai/v1","api_key":"gsk_xxx","model":"llama-3.1-8b-instant"}'
```

---

## Upload Issues

### Upload Stuck at "Uploading..."

Check server logs. Common: File too large (>2GB), network timeout. Check `MAX_UPLOAD_MB` in .env (default 2048 MB).

### Upload Stuck at "Processing..."

Check server logs for: `parse_done`, `embed_started`/`embed_progress`, Cohere 429 (rate limit), Cohere 401 (invalid key), Qdrant connection error.

### Document Stays at UPLOADED

Background task may have failed silently. Check server logs for: `parse_done`, `ingestion_failed`, exception in `_ingest_pipeline`.

### Document Shows FAILED

```bash
curl -b "rag_session=<cookie>" http://localhost:8000/api/v1/documents/<doc_id>
# Check error_message field
# Common: "PDF has N pages but no extractable text"
```

---

## Query Issues

### Always Returns "I couldn't find any relevant information"

| Cause | Check |
|-------|-------|
| No documents uploaded | `GET /documents` |
| Documents not READY | `GET /documents` → status READY |
| Query too vague | Try specific question |
| No relevant chunks | Lower similarity threshold (not configurable yet) |
| Wrong collection | Check collection = `rag_chatbot_cohere` |

### Citations Not Clickable / Missing

```bash
# Check browser console (F12) for "makeCitationsClickable" errors
# Fix: Hard refresh (Ctrl+Shift+R)
```

### Citations Show Wrong Text

```bash
uv run python -c "
from app.rag.vectorstore import _get_client
c = _get_client()
pts, _ = c.scroll('rag_chatbot_cohere', limit=5, with_payload=True)
for p in pts:
    pl = p.payload or {}
    print(f'  doc={pl.get(\"document_id\")} idx={pl.get(\"chunk_index\")} preview={pl.get(\"chunk_text\",\"\")[:80]!r}')
"
```

### Query Returns "Error: Invalid Cohere API key"

```bash
curl -X POST http://localhost:8000/api/v1/provider/config -H "Content-Type: application/json" -b "rag_session=<cookie>" -d '{"cohere_api_key": "sk-xxx"}'
```

### Query Returns "Error: Invalid API key" (Groq)

```bash
curl -X POST http://localhost:8000/api/v1/provider/config -H "Content-Type: application/json" -d '{"name":"Groq","base_url":"https://api.groq.com/openai/v1","api_key":"gsk_xxx","model":"llama-3.1-8b-instant"}'
```

---

## Configuration Issues

### Session Lost on Refresh

Check localStorage in DevTools: `rag.chats.v1`, `rag.active_chat.v1`, `rag.messages.*`, `rag_config`, `rag_cohere_key`. If missing: localStorage blocked or cleared.

### Provider Config Not Persisting

Check localStorage: `rag_config`, `rag_cohere_key`. If missing: localStorage blocked, private browsing, or quota exceeded.

### Session Cookie Not Set

Check DevTools Network: POST `/provider/config` should return `Set-Cookie` header. Check: `HttpOnly`, `SameSite=lax`, `Path=/`.

---

## Performance Issues

### Slow Query Response

Check: 1) Cohere embedding latency (1-2s), 2) Groq LLM latency (0.5-2s), 3) Qdrant query time (<100ms), 4) Total 2-5s.

### Slow Document Processing

Check server logs for: `parse_done`, `embed_progress`, `embed_done`, `upsert_done`. Typical 100-page text PDF: 10-30s. Scanned PDF with OCR: 2-5 min.

### High Memory Usage

Qdrant holds vectors in memory. 100k vectors × 1024 dim × 4 bytes ≈ 400MB. Monitor: `docker stats rag-qdrant`.

---

## Docker Issues

### Qdrant Container Exits Immediately

```bash
docker logs rag-qdrant
# Common: insufficient memory, port conflict
```

### Port 6333 Already in Use

```bash
lsof -ti:6333 | xargs kill -9
docker start rag-qdrant
```

---

## Database Issues

### SQLite Locked

```bash
pkill -f uvicorn
```

### Corrupted Database

```bash
cp backend/data/chatbot.db backup.db
rm backend/data/chatbot.db
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
# Tables auto-created on startup
```

### Sessions Not Persisting

```bash
cat backend/data/sessions.json
# Should have session entries with cohere_api_key
```

---

## Frontend Issues

### White Screen / JS Error

Open DevTools Console (F12). Look for red errors. Common: SyntaxError from syntax error in edit. Fix: Reload with Ctrl+Shift+R.

### Sticky Header/Input Not Working

```bash
# Check CSS:
# .chat-main { min-height: 0; height: 100vh; overflow: hidden }
# .chat-messages { flex: 1 1 auto; min-height: 0; overflow-y: auto }
# .input-area { flex: 0 0 auto }
# Hard refresh: Ctrl+Shift+R
```

### Panel Toggles Not Working

Check DevTools Console for errors. Check sessionStorage keys: `ui.leftCollapsed`, `ui.rightCollapsed`.

---

## Debug Commands

### Check Qdrant Collection

```bash
curl -s http://localhost:6333/collections/rag_chatbot_cohere | python3 -m json.tool
```

### Check Points in Collection

```bash
uv run python -c "
from app.rag.vectorstore import _get_client
c = _get_client()
info = c.get_collection('rag_chatbot_cohere')
print('Points:', info.points_count)
pts, _ = c.scroll('rag_chatbot_cohere', limit=3, with_payload=True)
for p in pts:
    pl = p.payload or {}
    print(f'  len={len(pl.get(\"chunk_text\",\"\"))} doc={pl.get(\"document_id\",\"?\")[:20]} preview={pl.get(\"chunk_text\",\"`)[:120]!r}')
"
```

### Test Retrieval Directly

```bash
uv run python -c "
from app.embeddings.cohere_cloud import CohereEmbeddingProvider
from app.rag.retriever import retrieve
import json
key = 'ijYteUqLQnnqwaWCXiHqLczeKhJ6C4MvD0KKCOvu'
e = CohereEmbeddingProvider(key)
r = retrieve('What is the license?', top_k=5, embedder=e)
for x in r:
    print(f'score={x[\"score\"]:.3f} {x[\"chunk_text\"][:150]!r}')
"
```

### View Server Logs

```bash
cat /tmp/server.log
# Or systemd: journalctl -u rag-chatbot -f
```

---

## Reset Everything

```bash
cd ~/Desktop/CODING/project_01
pkill -f uvicorn
docker stop rag-qdrant
rm -rf backend/data backend/uploads backend/__pycache__ backend/.pytest_cache
cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Still Stuck?

1. Run tests: `cd backend && uv run pytest -q` (should be 98 passed)
2. Check server logs for stack traces
3. Open GitHub issue with: error message, server log snippet, steps to reproduce, `curl /api/v1/health` output