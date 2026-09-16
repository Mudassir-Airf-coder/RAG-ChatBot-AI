# Phase 07 — Frontend Login

## Goal
Build the login page: provider dropdown, API key input, model fetch on connect, and redirect to chat page after model selection.

## Files to create or modify
- `backend/static/login.html` — Login page HTML
- `backend/static/login.js` — Login page JavaScript
- `backend/static/style.css` — Login page styles

## Interfaces to define

### `backend/static/login.js`
```javascript
// DOM elements
const providerSelect = document.getElementById('provider');
const apiKeyInput = document.getElementById('api-key');
const connectBtn = document.getElementById('connect-btn');
const modelSelect = document.getElementById('model-select');
const startBtn = document.getElementById('start-btn');
const errorDiv = document.getElementById('error');

// Event handlers
connectBtn.addEventListener('click', async () => {
    // 1. Get provider and api_key from inputs
    // 2. POST /api/v1/auth/models with {provider, api_key}
    // 3. On success: populate modelSelect dropdown
    // 4. On failure: show error message
});

startBtn.addEventListener('click', () => {
    // 1. Get selected model from modelSelect
    // 2. Store {provider, api_key, model} in sessionStorage
    // 3. Redirect to index.html
});
```

### `backend/static/login.html`
```html
<!-- Provider dropdown -->
<select id="provider">
    <option value="groq">Groq</option>
    <option value="opencode_zen">OpenCode Zen</option>
</select>

<!-- API key input -->
<input type="password" id="api-key" placeholder="API Key">

<!-- Connect button -->
<button id="connect-btn">Connect</button>

<!-- Model dropdown (hidden until connected) -->
<select id="model-select" style="display:none"></select>

<!-- Start button (hidden until model selected) -->
<button id="start-btn" style="display:none">Start Chatting</button>

<!-- Error display -->
<div id="error"></div>
```

## Tests required
- `backend/static/login.js` tests (manual or browser-based)
  - Test: connect button calls POST /api/v1/auth/models
  - Test: invalid key shows error message
  - Test: valid key populates model dropdown
  - Test: selecting model + clicking Start Chatting stores sessionStorage and redirects

## Manual verification
1. Open `http://localhost:8000`
2. Select provider: Groq
3. Paste API key
4. Click Connect
5. Verify model dropdown appears with model list
6. Select a model
7. Click Start Chatting
8. Verify redirect to `index.html`
9. Verify `sessionStorage` contains `{provider, api_key, model}`

## Definition of Done
- [ ] Login page renders with provider dropdown and API key input
- [ ] Connect button calls `/api/v1/auth/models` and populates model dropdown
- [ ] Invalid key shows error message
- [ ] Start Chatting stores session and redirects
- [ ] Login page is styled and responsive

## Evidence to record
- Paste browser interaction description in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: which endpoint fails, which UI element doesn't work
- Report to: human

## Do NOT
- Do not create chat page yet
- Do not create document upload UI yet
- Do not create chat history UI yet
