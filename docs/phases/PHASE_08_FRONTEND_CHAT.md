# Phase 08 — Frontend Chat

## Goal
Build the chat page: ChatGPT-style layout with message display, input box, and citation rendering.

## Files to create or modify
- `backend/static/index.html` — Chat page HTML
- `backend/static/app.js` — Chat page JavaScript
- `backend/static/style.css` — Chat page styles

## Interfaces to define

### `backend/static/app.js`
```javascript
// DOM elements
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');

// State
let currentChatId = null;

// Functions
async function sendMessage() {
    // 1. Get message text from input
    // 2. Render user message on right side
    // 3. POST /api/v1/query with {chat_id, question, provider, api_key, model}
    // 4. Render assistant message on left side with citations
    // 5. Clear input
}

function renderUserMessage(text) {
    // Create div with user message styling (right-aligned)
}

function renderAssistantMessage(answer, citations) {
    // Create div with assistant message styling (left-aligned)
    // Add citations section below the answer
    // Each citation is clickable → opens source modal
}

function openSourceModal(documentId, chunkId) {
    // 1. GET /api/v1/documents/{documentId}/chunks/{chunkId}
    // 2. Display modal with full chunk text + metadata
}
```

### `backend/static/index.html`
```html
<!-- Sidebar (toggleable) -->
<div id="sidebar">
    <button id="new-chat-btn">+ New Chat</button>
    <div id="documents-section">
        <!-- Documents list -->
    </div>
    <div id="history-section">
        <!-- Chat history list -->
    </div>
</div>

<!-- Main chat area -->
<div id="chat-area">
    <div id="chat-messages">
        <!-- Messages rendered here -->
    </div>
    <div id="input-area">
        <textarea id="message-input" placeholder="Type your question..."></textarea>
        <button id="send-btn">Send</button>
    </div>
</div>

<!-- Source inspection modal -->
<div id="source-modal" style="display:none">
    <div id="modal-content">
        <!-- Chunk text + metadata -->
    </div>
</div>
```

### `backend/static/style.css`
```css
/* ChatGPT-style layout */
/* Messages: user right, assistant left */
/* Citations: styled below each assistant message */
/* Sidebar: collapsible */
/* Modal: centered overlay */
```

## Tests required
- `backend/static/app.js` tests (manual or browser-based)
  - Test: message input sends to POST /api/v1/query
  - Test: user message renders right-aligned
  - Test: assistant message renders left-aligned with citations
  - Test: citation click opens source modal
  - Test: modal displays full chunk text

## Manual verification
1. Login with valid credentials (Phase 07 must be complete)
2. See empty chat page with sidebar and input box
3. Type a question and click Send
4. Verify user message appears right-aligned
5. Verify assistant response appears left-aligned with citations
6. Click a citation
7. Verify source modal opens with full chunk text

## Definition of Done
- [ ] Chat page renders with sidebar and main area
- [ ] Message input sends to POST /api/v1/query
- [ ] User messages render right-aligned
- [ ] Assistant messages render left-aligned with citations
- [ ] Citation click opens source modal
- [ ] Sidebar is toggleable
- [ ] Chat layout is responsive

## Evidence to record
- Paste browser interaction description in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: which API call fails, which UI element doesn't render
- Report to: human

## Do NOT
- Do not create document upload UI yet
- Do not create chat history UI yet
