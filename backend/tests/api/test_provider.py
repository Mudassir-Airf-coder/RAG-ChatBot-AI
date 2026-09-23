from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.api.provider import sessions
from app.main import app


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
    mock_provider.get_models.return_value = [
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]
    mock_get_provider.return_value = mock_provider

    resp = client.post(
        "/api/v1/provider/models",
        json={
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": "gsk_test",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "llama-3.1-8b-instant" in data["models"]


@patch("app.api.provider.get_provider")
def test_models_opencode_zen(mock_get_provider, client):
    mock_provider = AsyncMock()
    mock_provider.get_models.return_value = ["gpt-4o"]
    mock_get_provider.return_value = mock_provider

    resp = client.post(
        "/api/v1/provider/models",
        json={
            "base_url": "https://opencode.ai/zen/v1",
            "api_key": "oc_test",
        },
    )
    assert resp.status_code == 200
    assert "gpt-4o" in resp.json()["models"]


@patch("app.api.provider.get_provider")
def test_models_unknown_url(mock_get_provider, client):
    from app.exceptions import ValidationError

    mock_get_provider.side_effect = ValidationError("Unsupported provider URL")

    resp = client.post(
        "/api/v1/provider/models",
        json={
            "base_url": "https://unknown.com/v1",
            "api_key": "key",
        },
    )
    assert resp.status_code == 400
    assert "error" in resp.json()


@patch("app.api.provider.get_provider")
def test_test_connection_success(mock_get_provider, client):
    mock_provider = AsyncMock()
    mock_provider.chat.return_value = "OK"
    mock_get_provider.return_value = mock_provider

    resp = client.post(
        "/api/v1/provider/test",
        json={
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": "gsk_test",
            "model": "llama-3.1-8b-instant",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


@patch("app.api.provider.get_provider")
def test_test_connection_failure(mock_get_provider, client):
    mock_provider = AsyncMock()
    mock_provider.chat.side_effect = Exception("Connection refused")
    mock_get_provider.return_value = mock_provider

    resp = client.post(
        "/api/v1/provider/test",
        json={
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": "bad_key",
            "model": "llama-3.1-8b-instant",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is False


def test_config_sets_cookie(client):
    resp = client.post(
        "/api/v1/provider/config",
        json={
            "name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": "gsk_test",
            "model": "llama-3.1-8b-instant",
            "cohere_api_key": "sk-test-cohere",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert "rag_session" in resp.cookies


def test_config_stores_session(client):
    resp = client.post(
        "/api/v1/provider/config",
        json={
            "name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": "gsk_test",
            "model": "llama-3.1-8b-instant",
            "cohere_api_key": "sk-test-cohere",
        },
    )
    cookie = resp.cookies.get("rag_session")
    assert cookie is not None
    assert cookie in sessions
    assert sessions[cookie]["model"] == "llama-3.1-8b-instant"
    assert sessions[cookie]["cohere_api_key"] == "sk-test-cohere"


def test_get_models_old_method_returns_404(client):
    resp = client.get("/api/v1/provider/models")
    assert resp.status_code == 404


@patch("app.api.provider.get_provider")
def test_models_opencode_zen_url(mock_get_provider, client):
    mock_p = AsyncMock()
    mock_p.get_models.return_value = ["gpt-4o-mini", "claude-3-haiku"]
    mock_get_provider.return_value = mock_p

    resp = client.post(
        "/api/v1/provider/models",
        json={
            "base_url": "https://opencode.ai/zen/v1",
            "api_key": "oc_test",
        },
    )
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

    original_sessions_file = provider.SESSIONS_FILE
    original_sessions = provider.sessions

    try:
        monkeypatch.setattr(provider, "SESSIONS_FILE", tmp_path / "sessions.json")
        provider.sessions = {}
        client = TestClient(app)
        client.post(
            "/api/v1/provider/config",
            json={
                "name": "Groq",
                "base_url": "https://api.groq.com/openai/v1",
                "api_key": "test",
                "model": "llama-3.1-8b-instant",
                "cohere_api_key": "sk-test-cohere",
            },
        )
        reloaded = provider._load_sessions()
        assert len(reloaded) == 1
        assert list(reloaded.values())[0]["model"] == "llama-3.1-8b-instant"
    finally:
        provider.SESSIONS_FILE = original_sessions_file
        provider.sessions = original_sessions


def test_config_sets_cookie_after_persist(tmp_path, monkeypatch):
    from app.api import provider

    original_sessions_file = provider.SESSIONS_FILE
    original_sessions = provider.sessions

    try:
        monkeypatch.setattr(provider, "SESSIONS_FILE", tmp_path / "sessions.json")
        provider.sessions = {}
        client = TestClient(app)
        resp = client.post(
            "/api/v1/provider/config",
            json={
                "name": "Groq",
                "base_url": "https://api.groq.com/openai/v1",
                "api_key": "gsk_test",
                "model": "llama-3.1-8b-instant",
                "cohere_api_key": "sk-test-cohere",
            },
        )
        assert resp.status_code == 200
        assert "rag_session" in resp.cookies
        reloaded = provider._load_sessions()
        assert len(reloaded) == 1
    finally:
        provider.SESSIONS_FILE = original_sessions_file
        provider.sessions = original_sessions


@patch("app.embeddings.cohere_cloud.httpx.post")
def test_test_cohere_success(mock_post, client):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"embeddings": [[0.1] * 1024]}
    mock_post.return_value = mock_resp

    resp = client.post(
        "/api/v1/provider/test/cohere",
        json={
            "base_url": "",
            "api_key": "sk-test-cohere",
            "model": "embed-english-v3.0",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


@patch("app.embeddings.cohere_cloud.httpx.post")
def test_test_cohere_failure(mock_post, client):
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_post.return_value = mock_resp

    resp = client.post(
        "/api/v1/provider/test/cohere",
        json={
            "base_url": "",
            "api_key": "bad-key",
            "model": "embed-english-v3.0",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is False


def test_config_with_only_llm_fields(client):
    resp = client.post(
        "/api/v1/provider/config",
        json={
            "name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": "gsk_test",
            "model": "llama-3.1-8b-instant",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert "rag_session" in resp.cookies
    cookie = resp.cookies.get("rag_session")
    assert cookie in sessions
    assert sessions[cookie]["model"] == "llama-3.1-8b-instant"
    assert sessions[cookie]["cohere_api_key"] == ""


def test_config_with_only_cohere_key_succeeds(client):
    resp = client.post(
        "/api/v1/provider/config",
        json={
            "cohere_api_key": "sk-test-cohere",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ok"] is True
    assert data["llm_configured"] is False
    assert data["cohere_configured"] is True
    cookie = resp.cookies.get("rag_session")
    assert cookie in sessions
    assert sessions[cookie]["cohere_api_key"] == "sk-test-cohere"


def test_config_merges_partial_saves(client):
    # First save LLM only
    resp1 = client.post(
        "/api/v1/provider/config",
        json={
            "name": "Groq",
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": "gsk_test",
            "model": "llama-3.1-8b-instant",
        },
    )
    assert resp1.status_code == 200
    cookie = resp1.cookies.get("rag_session")
    assert cookie in sessions
    assert sessions[cookie]["model"] == "llama-3.1-8b-instant"
    assert sessions[cookie]["cohere_api_key"] == ""

    # Then save Cohere only (using the same cookie)
    client.cookies.set("rag_session", cookie)
    resp2 = client.post(
        "/api/v1/provider/config",
        json={
            "cohere_api_key": "sk-test-cohere",
        },
    )
    assert resp2.status_code == 200
    assert resp2.json()["ok"] is True
    assert resp2.json()["cohere_configured"] is True
    assert sessions[cookie]["model"] == "llama-3.1-8b-instant"
    assert sessions[cookie]["cohere_api_key"] == "sk-test-cohere"
