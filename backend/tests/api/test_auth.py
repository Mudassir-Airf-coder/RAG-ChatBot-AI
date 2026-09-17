import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@patch("app.api.auth.GroqProvider")
def test_get_models_valid_key(mock_provider_cls):
    mock_provider = AsyncMock()
    mock_provider.get_models.return_value = ["model-a", "model-b"]
    mock_provider_cls.return_value = mock_provider

    client = TestClient(app)
    resp = client.post("/api/v1/auth/models", json={"provider": "groq", "api_key": "test-key"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "groq"
    assert "model-a" in data["models"]


def test_opencode_zen_returns_400():
    client = TestClient(app)
    resp = client.post("/api/v1/auth/models", json={"provider": "opencode_zen", "api_key": "key"})
    assert resp.status_code == 400
    assert "Unsupported provider" in resp.json()["error"]["message"]


def test_unknown_provider_returns_400():
    client = TestClient(app)
    resp = client.post("/api/v1/auth/models", json={"provider": "unknown", "api_key": "key"})
    assert resp.status_code == 400
    assert "Unsupported provider" in resp.json()["error"]["message"]


def test_non_ascii_key_returns_400():
    client = TestClient(app)
    resp = client.post("/api/v1/auth/models", json={"provider": "groq", "api_key": "gsk_test_with_em_dash_\u2014"})
    assert resp.status_code == 400
    assert "invalid characters" in resp.json()["error"]["message"]
