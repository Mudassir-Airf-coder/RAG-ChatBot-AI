import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.llm.groq import GroqProvider
from app.exceptions import ProviderError


@pytest.fixture
def provider():
    return GroqProvider("test-key")


@pytest.mark.asyncio
async def test_get_models_returns_list(provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": [{"id": "model-a"}, {"id": "model-b"}]}

    with patch("app.llm.groq.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value = instance

        models = await provider.get_models()
        assert models == ["model-a", "model-b"]


@pytest.mark.asyncio
async def test_chat_returns_content(provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "hello there"}}]
    }

    with patch("app.llm.groq.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.post = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value = instance

        result = await provider.chat("model-a", [{"role": "user", "content": "hi"}])
        assert result == "hello there"


@pytest.mark.asyncio
async def test_invalid_api_key_raises():
    provider = GroqProvider("bad-key")
    mock_resp = MagicMock()
    mock_resp.status_code = 401

    with patch("app.llm.groq.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value = instance

        with pytest.raises(ProviderError, match="Invalid API key"):
            await provider.get_models()
