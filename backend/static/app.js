const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const chatHistory = document.getElementById('chat-history');
const newChatBtn = document.getElementById('new-chat-btn');
const toggleSidebarBtn = document.getElementById('toggle-sidebar');
const sidebar = document.getElementById('sidebar');
const sourceModal = document.getElementById('source-modal');
const modalBody = document.getElementById('modal-body');
const closeModalBtn = document.getElementById('close-modal');
const modalBackdrop = sourceModal.querySelector('.modal-backdrop');
const uploadBtn = document.getElementById('upload-btn');
const fileInput = document.getElementById('file-input');
const documentList = document.getElementById('document-list');

const provider = sessionStorage.getItem('provider');
const apiKey = sessionStorage.getItem('api_key');
const model = sessionStorage.getItem('model');

if (!provider || !apiKey || !model) {
    window.location.href = 'login.html';
}

let currentChatId = null;

function generateId() {
    return 'chat_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

async function apiCall(url, method = 'GET', body = null) {
    const opts = { method, headers: {} };
    if (body) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(body);
    }
    const resp = await fetch(url, opts);
    if (resp.status === 204) return null;
    return resp.json();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function renderLoading() {
    const div = document.createElement('div');
    div.className = 'message assistant-message loading-msg';
    div.id = 'loading-indicator';
    div.innerHTML = '<span class="spinner"></span> Thinking...';
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoading() {
    const el = document.getElementById('loading-indicator');
    if (el) el.remove();
}

function renderUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message user-message';
    div.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderAssistantMessage(answer, citations) {
    const div = document.createElement('div');
    div.className = 'message assistant-message';

    let citationsHtml = '';
    if (citations && citations.length > 0) {
        citationsHtml = '<div class="citations">';
        citations.forEach(c => {
            citationsHtml += `<span class="citation" data-doc="${c.document_id}" data-chunk="${c.chunk_id}">[${c.citation_index}]</span> `;
        });
        citationsHtml += '</div>';
    }

    div.innerHTML = `
        <div class="message-content">${escapeHtml(answer)}</div>
        ${citationsHtml}
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    div.querySelectorAll('.citation').forEach(el => {
        el.addEventListener('click', () => openSourceModal(el.dataset.doc, el.dataset.chunk));
    });
}

async function openSourceModal(documentId, chunkId) {
    try {
        const chunk = await apiCall(`/api/v1/documents/${documentId}/chunks/${chunkId}`);
        modalBody.innerHTML = `
            <pre>${escapeHtml(chunk.text)}</pre>
            <div class="chunk-meta">
                <p>Document: ${chunk.document_id}</p>
                <p>Chunk: ${chunk.chunk_index}</p>
            </div>
        `;
        sourceModal.classList.remove('hidden');
    } catch (err) {
        console.error('Failed to load chunk:', err);
    }
}

closeModalBtn.addEventListener('click', () => sourceModal.classList.add('hidden'));
modalBackdrop.addEventListener('click', () => sourceModal.classList.add('hidden'));

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    messageInput.value = '';
    messageInput.style.height = 'auto';

    renderUserMessage(text);
    renderLoading();

    try {
        let chatId = currentChatId;
        if (!chatId) {
            chatId = generateId();
            currentChatId = chatId;
            await apiCall('/api/v1/chats', 'POST', { title: text.slice(0, 50) });
        }

        const result = await apiCall('/api/v1/query', 'POST', {
            chat_id: chatId,
            question: text,
            provider,
            api_key: apiKey,
            model,
        });

        removeLoading();
        renderAssistantMessage(result.answer, result.citations);
        loadChatHistory();
    } catch (err) {
        removeLoading();
        renderAssistantMessage('Error: ' + err.message, []);
        showToast(err.message, 'error');
    }
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
});

newChatBtn.addEventListener('click', () => {
    currentChatId = null;
    chatMessages.innerHTML = '<div class="empty-state"><h2>RAG Chatbot</h2><p>Ask questions about your documents</p></div>';
});

toggleSidebarBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

// Chat history
async function loadChatHistory() {
    try {
        const data = await apiCall('/api/v1/chats');
        chatHistory.innerHTML = '';
        (data.chats || []).forEach(chat => {
            const div = document.createElement('div');
            div.className = 'chat-item';
            div.dataset.id = chat.id;
            div.innerHTML = `
                <span class="chat-title">${escapeHtml(chat.title)}</span>
                <button class="icon-btn chat-delete">✕</button>
            `;
            div.querySelector('.chat-title').addEventListener('click', () => loadChat(chat.id));
            div.querySelector('.chat-delete').addEventListener('click', (e) => {
                e.stopPropagation();
                deleteChat(chat.id, div);
            });
            if (chat.id === currentChatId) div.classList.add('active');
            chatHistory.appendChild(div);
        });
    } catch (err) {
        console.error('Failed to load chats:', err);
    }
}

async function loadChat(chatId) {
    currentChatId = chatId;
    chatMessages.innerHTML = '';

    document.querySelectorAll('.chat-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id === chatId);
    });

    try {
        const data = await apiCall(`/api/v1/chats/${chatId}/messages`);
        (data.messages || []).forEach(msg => {
            if (msg.role === 'user') {
                renderUserMessage(msg.content);
            } else {
                renderAssistantMessage(msg.content, msg.citations);
            }
        });
    } catch (err) {
        console.error('Failed to load messages:', err);
    }
}

async function deleteChat(chatId, item) {
    try {
        await apiCall(`/api/v1/chats/${chatId}`, 'DELETE');
        if (currentChatId === chatId) {
            currentChatId = null;
            chatMessages.innerHTML = '<div class="empty-state"><h2>RAG Chatbot</h2><p>Ask questions about your documents</p></div>';
        }
        loadChatHistory();
        showToast('Chat deleted', 'info');
    } catch (err) {
        console.error('Failed to delete chat:', err);
    }
}

loadChatHistory();

// Document upload
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', async () => {
    for (const file of fileInput.files) {
        await uploadDocument(file);
    }
    fileInput.value = '';
});

async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    const item = document.createElement('div');
    item.className = 'doc-item';
    item.innerHTML = `<span class="doc-name">${escapeHtml(file.name)}</span><span class="doc-status status-processing">PROCESSING</span>`;
    documentList.prepend(item);

    try {
        const resp = await fetch('/api/v1/documents/upload', { method: 'POST', body: formData });
        const data = await resp.json();
        item.querySelector('.doc-status').textContent = data.status;
        item.querySelector('.doc-status').className = `doc-status status-${data.status.toLowerCase()}`;
        item.dataset.id = data.id;

        const delBtn = document.createElement('button');
        delBtn.className = 'icon-btn doc-delete';
        delBtn.textContent = '✕';
        delBtn.addEventListener('click', () => deleteDocument(data.id, item));
        item.appendChild(delBtn);
        showToast(`Uploaded: ${file.name}`, 'success');
    } catch (err) {
        item.querySelector('.doc-status').textContent = 'FAILED';
        item.querySelector('.doc-status').className = 'doc-status status-failed';
        showToast('Upload failed', 'error');
    }
}

async function deleteDocument(docId, item) {
    try {
        await apiCall(`/api/v1/documents/${docId}`, 'DELETE');
        item.remove();
    } catch (err) {
        console.error('Failed to delete:', err);
    }
}

async function loadDocuments() {
    try {
        const data = await apiCall('/api/v1/documents');
        documentList.innerHTML = '';
        (data.documents || []).forEach(doc => {
            const item = document.createElement('div');
            item.className = 'doc-item';
            item.dataset.id = doc.id;
            item.innerHTML = `
                <span class="doc-name">${escapeHtml(doc.filename)}</span>
                <span class="doc-status status-${doc.status.toLowerCase()}">${doc.status}</span>
            `;
            if (doc.status !== 'PROCESSING') {
                const delBtn = document.createElement('button');
                delBtn.className = 'icon-btn doc-delete';
                delBtn.textContent = '✕';
                delBtn.addEventListener('click', () => deleteDocument(doc.id, item));
                item.appendChild(delBtn);
            }
            documentList.appendChild(item);
        });
    } catch (err) {
        console.error('Failed to load documents:', err);
    }
}

loadDocuments();
