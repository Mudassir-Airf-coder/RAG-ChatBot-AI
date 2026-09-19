from unittest.mock import MagicMock, patch
import numpy as np


@patch("app.rag.embedder._get_model")
def test_embed_chunks_returns_correct_count(mock_get_model):
    mock_model = MagicMock()
    mock_model.embed.return_value = [np.zeros(384) for _ in range(3)]
    mock_get_model.return_value = mock_model

    from app.rag.embedder import embed_chunks
    result = embed_chunks(["a", "b", "c"])

    assert len(result) == 3
    mock_model.embed.assert_called_once_with(["a", "b", "c"], batch_size=64, parallel=4)


@patch("app.rag.embedder._get_model")
def test_embed_query_returns_vector(mock_get_model):
    mock_model = MagicMock()
    mock_model.embed.return_value = [np.ones(384)]
    mock_get_model.return_value = mock_model

    from app.rag.embedder import embed_query
    result = embed_query("test query")

    assert result.shape == (384,)
    mock_model.embed.assert_called_once_with(["test query"], batch_size=1, parallel=1)
