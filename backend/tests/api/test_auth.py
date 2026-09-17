import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@patch("app.api.auth._get_provider")
def test_get_models_valid_key(mock_get_provider):
    mock_provider = AsyncMock()
    mock_provider.get_models.return_value = ["model-a", "model-b"]
    mock_get_provider.return_value = mock_provider

    client = TestClient(app)
    resp = client.post("/api/v1/auth/models", json={"provider": "groq", "api_key": "test-key"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "groq"
    assert "model-a" in data["models"]


@patch("app.api.auth._get_provider")
def test_get_models_invalid_key(mock_get_provider):
    from app.exceptions import ProviderError
    mock_get_provider.side_effect = ProviderError("Invalid API key")

    client = TestClient(app)
    resp = client.post("/api/v1/auth/models", json={"provider": "groq", "api_key": "bad"})
    assert resp.status_code == 502
    assert resp.json()["error"]["code"] == "PROVIDER_ERROR"


def test_non_ascii_key_returns_400():
    client = TestClient(app)
    resp = client.post("/api/v1/auth/models", json={"provider": "groq", "api_key": "gsk_test_with_em_dash_\u2014"})
    assert resp.status_code == 400
    assert "invalid characters" in resp.json()["error"]["message"]
