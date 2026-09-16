# Phase 10 — Frontend History

## Goal
Build the chat history section in the sidebar: new chat button, chat list, load chat, and delete chat.

## Files to create or modify
- `backend/static/index.html` — Update sidebar with history section
- `backend/static/app.js` — Add chat CRUD logic

## Interfaces to define

### `backend/static/app.js` (additions)
```javascript
// DOM elements for history
const historySection = document.getElementById('history-section');
const newChatBtn = document.getElementById('new-chat-btn');
const chatList = document.getElementById('chat-list');

// Functions
async function createNewChat() {
    // 1. POST /api/v1/chats with {title: "New chat"}
    // 2. Set currentChatId to new chat id
    // 3. Clear chat messages area
    // 4. Refresh chat list
}

async function loadChats() {
    // 1. GET /api/v1/chats
    // 2. Render chat list with timestamps
}

async function loadChat(chatId) {
    // 1. GET /api/v1/chats/{chatId}/messages
    // 2. Set currentChatId
    // 3. Render messages in chat area
}

async function deleteChat(chatId) {
    // 1. Confirm deletion
    // 2. DELETE /api/v1/chats/{chatId}
    // 3. If deleted chat was current, clear chat area
    // 4. Refresh chat list
}

function renderChatList(chats) {
    // For each chat:
    // - Show title
    // - Show timestamp
    // - Click to load chat
    // - Delete button
}
```

### `backend/static/index.html` (additions)
```html
<div id="history-section">
    <h3>History</h3>
    <div id="chat-list">
        <!-- Chats rendered here -->
    </div>
</div>
```

## Tests required
- Manual browser tests
  - Test: New Chat button creates a new chat
  - Test: Chat list shows all chats
  - Test: Clicking a chat loads its messages
  - Test: Delete button removes chat from list
  - Test: Current chat is highlighted in list

## Manual verification
1. Login and open chat page
2. Send a message (creates a chat automatically)
3. Verify chat appears in History section
4. Click New Chat button
5. Verify new empty chat is created
6. Send another message
7. Verify both chats appear in History
8. Click first chat
9. Verify its messages load
10. Delete second chat
11. Verify it's removed from list

## Definition of Done
- [ ] New Chat button creates a new chat
- [ ] Chat list shows all chats
- [ ] Clicking a chat loads its messages
- [ ] Delete button removes chat
- [ ] Current chat is highlighted

## Evidence to record
- Paste browser interaction description in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: which chat operation fails, which UI doesn't update
- Report to: human

## Do NOT
- Do not add streaming
- Do not add chat export
- Do not add chat renaming
