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

function generateMsgId() {
    return 'msg_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
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

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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

    try {
        let chatId = currentChatId;
        if (!chatId) {
            chatId = generateId();
            await apiCall('/api/v1/chats', 'POST', { title: text.slice(0, 50) });
            currentChatId = chatId;
        }

        const result = await apiCall('/api/v1/query', 'POST', {
            chat_id: chatId,
            question: text,
            provider,
            api_key: apiKey,
            model,
        });

        renderAssistantMessage(result.answer, result.citations);
        loadChatHistory();
    } catch (err) {
        renderAssistantMessage('Error: ' + err.message, []);
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

async function loadChatHistory() {
    try {
        const data = await apiCall('/api/v1/chats');
        chatHistory.innerHTML = '';
        (data.chats || []).forEach(chat => {
            const div = document.createElement('div');
            div.className = 'chat-item';
            div.textContent = chat.title;
            div.addEventListener('click', () => loadChat(chat.id));
            chatHistory.appendChild(div);
        });
    } catch (err) {
        console.error('Failed to load chats:', err);
    }
}

async function loadChat(chatId) {
    currentChatId = chatId;
    chatMessages.innerHTML = '';

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

loadChatHistory();
