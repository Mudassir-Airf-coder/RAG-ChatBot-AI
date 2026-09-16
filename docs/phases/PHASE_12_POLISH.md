# Phase 12 — Polish

## Goal
Add README screenshots, error states, loading states, and run a final smoke test to verify the complete flow.

## Files to create or modify
- `README.md` — Add screenshots and final setup instructions
- `backend/static/login.html` — Add loading states
- `backend/static/index.html` — Add loading states
- `backend/static/app.js` — Add error handling and loading indicators
- `backend/static/style.css` — Add loading and error styles

## Interfaces to define

### `backend/static/app.js` (additions)
```javascript
// Loading states
function showLoading(elementId) {
    // Add loading spinner or text
}

function hideLoading(elementId) {
    // Remove loading spinner
}

// Error handling
function showError(message) {
    // Display error to user
}

// Toast notifications
function showToast(message, type) {
    // Show success/error/info toast
}
```

## Tests required
- Manual smoke test of complete flow:
  1. Open `http://localhost:8000`
  2. Login with Groq provider
  3. Upload a document
  4. Wait for READY status
  5. Send a question about the document
  6. Verify answer with citations
  7. Click citation to view source
  8. Create new chat
  9. Delete old chat
  10. Delete document
  11. Logout (clear sessionStorage)

## Manual verification
```bash
# Final smoke test
curl -s http://localhost:8000/api/v1/health
# Expected: {"status":"ok"}

curl -s http://localhost:8000/api/v1/documents
# Expected: {"documents":[]}

curl -s http://localhost:8000/api/v1/chats
# Expected: {"chats":[]}
```

## Definition of Done
- [ ] README has screenshots (login page, chat page)
- [ ] README has final setup instructions
- [ ] Error states display correctly (invalid key, provider unreachable, no documents)
- [ ] Loading states display during operations
- [ ] Complete flow works end-to-end
- [ ] All tests pass
- [ ] No placeholder text or TODO items remain

## Evidence to record
- Paste final smoke test output in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: which flow step fails, which UI element is missing
- Report to: human

## Do NOT
- Do not add new features
- Do not change existing behavior
- Do not add streaming
- Do not add deployment scripts
