import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.config import Settings
from app.exceptions import ProviderError


def _make_provider():
    with patch("app.llm.opencode_zen.settings") as mock_settings:
        mock_settings.opencode_zen_base_url = "https://zen.example.com/v1"
        from app.llm.opencode_zen import OpenCodeZenProvider
        return OpenCodeZenProvider("test-key")


@pytest.mark.asyncio
async def test_missing_base_url_raises():
    with patch("app.llm.opencode_zen.settings") as mock_settings:
        mock_settings.opencode_zen_base_url = ""
        from app.llm.opencode_zen import OpenCodeZenProvider
        with pytest.raises(ProviderError, match="OPENCODE_ZEN_BASE_URL"):
            OpenCodeZenProvider("key")


@pytest.mark.asyncio
async def test_get_models_returns_list():
    provider = _make_provider()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": [{"id": "zen-1"}]}

    with patch("app.llm.opencode_zen.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value = instance

        models = await provider.get_models()
        assert models == ["zen-1"]


@pytest.mark.asyncio
async def test_chat_returns_content():
    provider = _make_provider()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "zen answer"}}]
    }

    with patch("app.llm.opencode_zen.httpx.AsyncClient") as mock_client:
        instance = AsyncMock()
        instance.post = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value = instance

        result = await provider.chat("zen-1", [{"role": "user", "content": "q"}])
        assert result == "zen answer"
