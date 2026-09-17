import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.provider import sessions


@pytest.fixture
def client():
    return TestClient(app)


def clear_sessions():
    sessions.clear()


@pytest.fixture(autouse=True)
def cleanup():
    clear_sessions()
    yield
    clear_sessions()


@patch("app.api.provider.get_provider")
def test_models_groq(mock_get_provider, client):
    mock_provider = AsyncMock()
    mock_provider.get_models.return_value = ["llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    mock_get_provider.return_value = mock_provider

    resp = client.post("/api/v1/provider/models", json={
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "gsk_test",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "llama-3.1-8b-instant" in data["models"]


@patch("app.api.provider.get_provider")
def test_models_opencode_zen(mock_get_provider, client):
    mock_provider = AsyncMock()
    mock_provider.get_models.return_value = ["gpt-4o"]
    mock_get_provider.return_value = mock_provider

    resp = client.post("/api/v1/provider/models", json={
        "base_url": "https://opencode.ai/zen/v1",
        "api_key": "oc_test",
    })
    assert resp.status_code == 200
    assert "gpt-4o" in resp.json()["models"]


@patch("app.api.provider.get_provider")
def test_models_unknown_url(mock_get_provider, client):
    from app.exceptions import ValidationError
    mock_get_provider.side_effect = ValidationError("Unsupported provider URL")

    resp = client.post("/api/v1/provider/models", json={
        "base_url": "https://unknown.com/v1",
        "api_key": "key",
    })
    assert resp.status_code == 400
    assert "error" in resp.json()


@patch("app.api.provider.get_provider")
def test_test_connection_success(mock_get_provider, client):
    mock_provider = AsyncMock()
    mock_provider.chat.return_value = "OK"
    mock_get_provider.return_value = mock_provider

    resp = client.post("/api/v1/provider/test", json={
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "gsk_test",
        "model": "llama-3.1-8b-instant",
    })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


@patch("app.api.provider.get_provider")
def test_test_connection_failure(mock_get_provider, client):
    mock_provider = AsyncMock()
    mock_provider.chat.side_effect = Exception("Connection refused")
    mock_get_provider.return_value = mock_provider

    resp = client.post("/api/v1/provider/test", json={
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "bad_key",
        "model": "llama-3.1-8b-instant",
    })
    assert resp.status_code == 200
    assert resp.json()["ok"] is False


def test_config_sets_cookie(client):
    resp = client.post("/api/v1/provider/config", json={
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "gsk_test",
        "model": "llama-3.1-8b-instant",
    })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert "rag_session" in resp.cookies


def test_config_stores_session(client):
    resp = client.post("/api/v1/provider/config", json={
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "gsk_test",
        "model": "llama-3.1-8b-instant",
    })
    cookie = resp.cookies.get("rag_session")
    assert cookie is not None
    assert cookie in sessions
    assert sessions[cookie]["model"] == "llama-3.1-8b-instant"


def test_get_models_old_method_returns_404(client):
    resp = client.get("/api/v1/provider/models")
    assert resp.status_code == 404


@patch("app.api.provider.get_provider")
def test_models_opencode_zen_url(mock_get_provider, client):
    mock_p = AsyncMock()
    mock_p.get_models.return_value = ["gpt-4o-mini", "claude-3-haiku"]
    mock_get_provider.return_value = mock_p

    resp = client.post("/api/v1/provider/models", json={
        "base_url": "https://opencode.ai/zen/v1",
        "api_key": "oc_test",
    })
    assert resp.status_code == 200
    assert "gpt-4o-mini" in resp.json()["models"]


def test_factory_picks_opencode_zen():
    from app.llm import get_provider
    from app.llm.opencode_zen import OpenCodeZenProvider
    p = get_provider("https://opencode.ai/zen/v1", "test")
    assert isinstance(p, OpenCodeZenProvider)


def test_factory_picks_groq():
    from app.llm import get_provider
    from app.llm.groq import GroqProvider
    p = get_provider("https://api.groq.com/openai/v1", "test")
    assert isinstance(p, GroqProvider)


def test_config_persists_across_reload(tmp_path, monkeypatch):
    from app.api import provider
    monkeypatch.setattr(provider, "SESSIONS_FILE", tmp_path / "sessions.json")
    provider.sessions = {}
    client = TestClient(app)
    client.post("/api/v1/provider/config", json={
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "test",
        "model": "llama-3.1-8b-instant",
    })
    reloaded = provider._load_sessions()
    assert len(reloaded) == 1
    assert list(reloaded.values())[0]["model"] == "llama-3.1-8b-instant"


def test_config_sets_cookie_after_persist(tmp_path, monkeypatch):
    from app.api import provider
    monkeypatch.setattr(provider, "SESSIONS_FILE", tmp_path / "sessions.json")
    provider.sessions = {}
    client = TestClient(app)
    resp = client.post("/api/v1/provider/config", json={
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "gsk_test",
        "model": "llama-3.1-8b-instant",
    })
    assert resp.status_code == 200
    assert "rag_session" in resp.cookies
    reloaded = provider._load_sessions()
    assert len(reloaded) == 1
