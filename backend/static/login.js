const providerSelect = document.getElementById('provider');
const apiKeyInput = document.getElementById('api-key');
const connectBtn = document.getElementById('connect-btn');
const modelSection = document.getElementById('model-section');
const modelSelect = document.getElementById('model-select');
const startBtn = document.getElementById('start-btn');
const errorDiv = document.getElementById('error');

function showError(msg) {
    errorDiv.textContent = msg;
    errorDiv.style.display = 'block';
}

function hideError() {
    errorDiv.style.display = 'none';
}

connectBtn.addEventListener('click', async () => {
    hideError();
    const provider = providerSelect.value;
    const apiKey = apiKeyInput.value.trim();

    if (!apiKey) {
        showError('Please enter an API key');
        return;
    }

    connectBtn.disabled = true;
    connectBtn.textContent = 'Connecting...';

    try {
        const resp = await fetch('/api/v1/auth/models', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ provider, api_key: apiKey }),
        });

        const data = await resp.json();

        if (!resp.ok) {
            showError(data.error?.message || 'Connection failed');
            return;
        }

        modelSelect.innerHTML = '';
        data.models.forEach(model => {
            const opt = document.createElement('option');
            opt.value = model;
            opt.textContent = model;
            modelSelect.appendChild(opt);
        });

        modelSection.classList.remove('hidden');
    } catch (err) {
        showError('Network error: ' + err.message);
    } finally {
        connectBtn.disabled = false;
        connectBtn.textContent = 'Connect';
    }
});

startBtn.addEventListener('click', () => {
    const model = modelSelect.value;
    if (!model) return;

    sessionStorage.setItem('provider', providerSelect.value);
    sessionStorage.setItem('api_key', apiKeyInput.value.trim());
    sessionStorage.setItem('model', model);

    window.location.href = 'index.html';
});
