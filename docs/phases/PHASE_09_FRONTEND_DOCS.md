# Phase 09 — Frontend Documents

## Goal
Build the documents section in the sidebar: upload button, file select, document list with status indicators, and delete button.

## Files to create or modify
- `backend/static/index.html` — Update sidebar with documents section
- `backend/static/app.js` — Add document CRUD logic

## Interfaces to define

### `backend/static/app.js` (additions)
```javascript
// DOM elements for documents
const documentsSection = document.getElementById('documents-section');
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const documentList = document.getElementById('document-list');

// Functions
async function uploadDocument(file) {
    // 1. Create FormData with file
    // 2. POST /api/v1/documents/upload
    // 3. Show status: PROCESSING
    // 4. Poll or refresh until status: READY or FAILED
}

async function loadDocuments() {
    // 1. GET /api/v1/documents
    // 2. Render document list with status indicators
}

async function deleteDocument(documentId) {
    // 1. Confirm deletion
    // 2. DELETE /api/v1/documents/{documentId}
    // 3. Refresh document list
}

function renderDocumentList(documents) {
    // For each document:
    // - Show filename
    // - Show status badge (PROCESSING / READY / FAILED)
    // - Show delete button (only if READY or FAILED)
}
```

### `backend/static/index.html` (additions)
```html
<div id="documents-section">
    <h3>Documents</h3>
    <input type="file" id="file-input" style="display:none">
    <button id="upload-btn">Upload Document</button>
    <div id="document-list">
        <!-- Documents rendered here -->
    </div>
</div>
```

## Tests required
- Manual browser tests
  - Test: upload button opens file select dialog
  - Test: file select triggers upload
  - Test: document appears in list with PROCESSING status
  - Test: document status changes to READY after processing
  - Test: delete button removes document from list
  - Test: error status shows FAILED badge

## Manual verification
1. Login and open chat page
2. Click Upload Document button
3. Select a file
4. Verify document appears in list with PROCESSING status
5. Wait for processing to complete
6. Verify status changes to READY
7. Click delete button
8. Verify document is removed from list

## Definition of Done
- [ ] Upload button opens file select
- [ ] File upload calls POST /api/v1/documents/upload
- [ ] Document list shows all documents with status
- [ ] Delete button removes document
- [ ] Status indicators update correctly

## Evidence to record
- Paste browser interaction description in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: which upload fails, which status doesn't update
- Report to: human

## Do NOT
- Do not create chat history UI yet
