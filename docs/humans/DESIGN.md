# Design & UX

## UI Layout — Three Columns

```
┌─────────────────────────────────────────────────────────────────────┐
│  Header (logo + title + active chat + toggle buttons)              │
├──────────┬──────────────────────────────────────────┬──────────────┤
│ Sidebar  │              Chat Area                    │ Config Panel │
│          │                                           │              │
│  Chats   │  • Empty state / messages                 │ LLM Provider │
│  + New   │  • User messages (right, purple)          │  - Provider  │
│  list    │  • Assistant messages (left, surface)     │  - Base URL  │
│          │  • Citations [1][2] inline, clickable     │  - API Key   │
│ Documents│  • Rewrite hint when query rewritten      │  - Model     │
│  Upload  │  • Error messages                         │  - Fetch     │
│  List    │                                           │  - Test      │
│  Delete  │                                           │  - Save      │
│          │                                           │  - Clear     │
├──────────┴──────────────────────────────────────────┴──────────────┤
│ Input Area (sticky bottom)                                        │
│  [textarea]                    [Send]                             │
└─────────────────────────────────────────────────────────────────────┘
```

- **Left (280px)**: Sidebar with Chats + Documents
- **Center (flexible)**: Chat area — only this scrolls
- **Right (320px)**: Config panel (LLM + Embeddings)
- **Header**: Logo, title, active chat title, panel toggles
- **Input**: Sticky at bottom, grows to 120px max

### Collapse States

| State | Grid Columns |
|-------|--------------|
| Default | `280px minmax(0, 1fr) 320px` |
| Left collapsed | `0 minmax(0, 1fr) 320px` |
| Right collapsed | `280px minmax(0, 1fr) 0` |
| Both collapsed | `0 minmax(0, 1fr) 0` |

`minmax(0, 1fr)` prevents the middle column from being squeezed below its content.

## Visual Design

### Color Palette (CSS Variables)

| Variable | Hex | Usage |
|----------|-----|-------|
| `--bg` | `#0a0a0f` | Page background |
| `--surface` | `#12121a` | Panels, header, modal |
| `--surface2` | `#1a1a25` | Inputs, message bubbles, cards |
| `--border` | `#2a2a3a` | Borders, dividers |
| `--text` | `#e0e0e8` | Primary text |
| `--text2` | `#8888a0` | Secondary text, placeholders |
| `--accent` | `#6c5ce7` | Primary actions, links |
| `--accent2` | `#a29bfe` | Secondary accents, citations |
| `--green` | `#00b894` | Success, ready status |
| `--red` | `#e74c3c` | Errors, delete buttons |
| `--orange` | `#fdcb6e` | Warnings, processing |

### Typography

- **Font stack**: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Base size**: 13-14px
- **Headings**: 15px (section-title 12px uppercase)
- **Citations**: 11px, inline pills

### Dark Theme

Full dark mode only. No light mode toggle.

## User Flows

### 1. First Visit → Provider Config → Upload → Query

```
Landing (empty chat)
    │
    ▼
Click gear icon (top right) → Provider panel opens
    │
    ├── LLM Provider: select Groq → enter API key → Fetch Models → select model → Test → Save
    │
    └── Embedding Provider: enter Cohere API key → Test → Save
    │
    ▼
Click "Upload Document" → select file → wait for READY
    │
    ▼
Type question → Send → see answer with citations
```

### 2. Chat History — Create / Switch / Delete

```
New Chat (+ button)
    │
    ▼
Creates new chat_id, saves to localStorage, renders in sidebar
    │
    ▼
Click chat in sidebar → switchToChat() → loads messages, updates active
    │
    ▼
Hover chat → shows ✕ → click → confirm → deleteChat() → removes from localStorage
```

### 3. Document Upload → Processing → Ready

```
Upload (drag-drop or click)
    │
    ▼
POST /documents/upload → 202 Accepted + doc_id
    │
    ▼
Background: parse → chunk → embed (Cohere) → index (Qdrant)
    │
    ▼
Poll GET /documents/{id} every 2s
    │
    ├── READY → show green badge, toast success
    ├── FAILED → show red badge, error message
    └── PROCESSING → show spinner, chunk count, ETA
```

### 4. Document Deletion

```
Click ✕ on document → "Sure?" → click again → DELETE /documents/{id}
    │
    ├── Qdrant delete by document_id
    ├── SQLite delete
    └── Remove upload folder
```

### 5. Provider Configuration

```
LLM Section:          Embedding Section:
- Provider dropdown   - Cohere API key input
- Name input          - Test Connection button
- Base URL            - Save button
- API Key             - Clear button
- Model dropdown
- Fetch Models
- Test button
- Save button
- Clear button
```

## State Management (localStorage)

| Key | Shape | Purpose |
|-----|-------|---------|
| `rag.chats.v1` | `Chat[]` | List of chats `{id, title, created, updated}` |
| `rag.active_chat.v1` | `string` | Current `chat_id` |
| `rag.messages.{chat_id}` | `Message[]` | Per-chat message array |
| `rag_config` | `{name, base_url, api_key, model}` | LLM provider config |
| `rag_cohere_key` | `string` | Cohere API key |

### Message Shape

```json
{
  "role": "user" | "assistant",
  "content": "string",
  "citations": [{"citation_index": 1, "document_id": "...", "chunk_id": "..."}],
  "abstained": false,
  "rewritten_query": "optional",
  "error": false,
  "ts": 1699999999999
}
```

## Citation UX

### Inline Citations (Clickable)

- LLM outputs inline markers: `[1]`, `[2]`, `[3]`
- Rendered as `.inline-cite` spans (purple background, hover darkens)
- Click → opens modal with source chunk text + document name
- No duplicate pill list at bottom (removed to reduce noise)

### Click Behavior

```
Click [1] in message
    │
    ▼
Find citation[0] in msg.citations
    │
    ▼
Open #source-modal with:
  - Chunk text (c.quote or full chunk_text)
  - Document name (c.document_name)
```

## Panel Toggle Persistence

- Left/right panel collapse state saved to `sessionStorage`
- Keys: `ui.leftCollapsed`, `ui.rightCollapsed`
- Restored on page load
- Buttons show `active` class when collapsed

## Responsive Behavior

| Breakpoint | Behavior |
|------------|----------|
| < 768px | Side panels collapse to icons; toggle via header buttons |
| ≥ 768px | Full three-column layout |

No horizontal scroll anywhere. `overflow: hidden` on layout root.