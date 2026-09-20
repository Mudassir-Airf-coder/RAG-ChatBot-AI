import pytest
from unittest.mock import patch, MagicMock
import numpy as np

from app.embeddings.cohere_cloud import CohereEmbeddingProvider
from app.exceptions import ProviderError, ValidationError


@pytest.fixture
def provider():
    return CohereEmbeddingProvider("sk-test-key")


def test_init_valid_key(provider):
    assert provider.api_key == "sk-test-key"
    assert provider.model == "embed-english-v3.0"
    assert provider.dimension == 1024
    assert provider.collection_name == "rag_chatbot_cohere"


def test_init_empty_key_raises():
    with pytest.raises(ValidationError, match="Cohere API key is required"):
        CohereEmbeddingProvider("")


def test_init_non_ascii_key_raises():
    with pytest.raises(ValidationError, match="API key contains invalid characters"):
        CohereEmbeddingProvider("sk-test-\u2014")


def test_embed_chunks_empty_returns_empty_list(provider):
    result = provider.embed_chunks([])
    assert result == []


def test_embed_chunks_single_batch(provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"embeddings": [[0.1] * 1024, [0.2] * 1024]}

    with patch("app.embeddings.cohere_cloud.httpx.post", return_value=mock_resp) as mock_post:
        result = provider.embed_chunks(["text1", "text2"])
        assert len(result) == 2
        assert all(isinstance(v, np.ndarray) for v in result)
        assert all(v.shape == (1024,) for v in result)
        assert all(v.dtype == np.float32 for v in result)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args.kwargs["json"]["input_type"] == "search_document"
        assert call_args.kwargs["json"]["texts"] == ["text1", "text2"]


def test_embed_query(provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"embeddings": [[0.5] * 1024]}

    with patch("app.embeddings.cohere_cloud.httpx.post", return_value=mock_resp) as mock_post:
        result = provider.embed_query("test query")
        assert isinstance(result, np.ndarray)
        assert result.shape == (1024,)
        assert result.dtype == np.float32
        call_args = mock_post.call_args
        assert call_args.kwargs["json"]["input_type"] == "search_query"
        assert call_args.kwargs["json"]["texts"] == ["test query"]


def test_embed_chunks_multiple_batches(provider):
    texts = ["text" + str(i) for i in range(100)]  # More than MAX_BATCH (96)
    # First batch: 96 texts, second batch: 4 texts
    mock_resp_1 = MagicMock()
    mock_resp_1.status_code = 200
    mock_resp_1.json.return_value = {"embeddings": [[0.1] * 1024] * 96}
    mock_resp_2 = MagicMock()
    mock_resp_2.status_code = 200
    mock_resp_2.json.return_value = {"embeddings": [[0.2] * 1024] * 4}

    with patch("app.embeddings.cohere_cloud.httpx.post", side_effect=[mock_resp_1, mock_resp_2]) as mock_post:
        result = provider.embed_chunks(texts)
        assert len(result) == 100
        assert mock_post.call_count == 2


def test_401_raises_provider_error(provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 401

    with patch("app.embeddings.cohere_cloud.httpx.post", return_value=mock_resp):
        with pytest.raises(ProviderError, match="Invalid Cohere API key"):
            provider.embed_chunks(["test"])


def test_429_raises_provider_error(provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 429

    with patch("app.embeddings.cohere_cloud.httpx.post", return_value=mock_resp):
        with pytest.raises(ProviderError, match="Cohere rate limit exceeded"):
            provider.embed_chunks(["test"])


def test_other_error_raises_provider_error(provider):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with patch("app.embeddings.cohere_cloud.httpx.post", return_value=mock_resp):
        with pytest.raises(ProviderError, match="Cohere returned 500"):
            provider.embed_chunks(["test"])