from unittest.mock import MagicMock, patch
import numpy as np

from app.rag.retriever import retrieve


def _mock_point(chunk_id, doc_id, index, text, score):
    point = MagicMock()
    point.payload = {
        "chunk_id": chunk_id,
        "document_id": doc_id,
        "chunk_index": index,
        "chunk_text": text,
        "metadata": {"source": "test.txt"},
    }
    point.score = score
    return point


@patch("app.rag.retriever._get_client")
@patch("app.rag.retriever.embed_query")
def test_returns_empty_when_no_results(mock_embed, mock_get_client):
    mock_embed.return_value = np.zeros(384)
    mock_client = MagicMock()
    mock_client.query_points.return_value.points = []
    mock_get_client.return_value = mock_client

    result = retrieve("test query")
    assert result == []


@patch("app.rag.retriever._get_client")
@patch("app.rag.retriever.embed_query")
def test_returns_top_k_sorted_by_score(mock_embed, mock_get_client):
    mock_embed.return_value = np.zeros(384)
    mock_client = MagicMock()
    mock_client.query_points.return_value.points = [
        _mock_point("c2", "d1", 1, "high", 0.9),
        _mock_point("c3", "d1", 2, "mid", 0.7),
        _mock_point("c1", "d1", 0, "low", 0.5),
    ]
    mock_get_client.return_value = mock_client

    result = retrieve("test", top_k=3)
    assert len(result) == 3
    assert result[0]["score"] >= result[1]["score"] >= result[2]["score"]


@patch("app.rag.retriever._get_client")
@patch("app.rag.retriever.embed_query")
def test_result_has_required_fields(mock_embed, mock_get_client):
    mock_embed.return_value = np.zeros(384)
    mock_client = MagicMock()
    mock_client.query_points.return_value.points = [
        _mock_point("chunk_doc_001_0", "doc_001", 0, "hello world", 0.85),
    ]
    mock_get_client.return_value = mock_client

    result = retrieve("test", top_k=1)
    assert len(result) == 1
    chunk = result[0]
    assert chunk["chunk_id"] == "chunk_doc_001_0"
    assert chunk["document_id"] == "doc_001"
    assert chunk["chunk_index"] == 0
    assert chunk["chunk_text"] == "hello world"
    assert chunk["score"] == 0.85
    assert "metadata" in chunk


@patch("app.rag.retriever._get_client")
@patch("app.rag.retriever.embed_query")
def test_embeds_query_before_search(mock_embed, mock_get_client):
    mock_embed.return_value = np.ones(384)
    mock_client = MagicMock()
    mock_client.query_points.return_value.points = []
    mock_get_client.return_value = mock_client

    retrieve("my query")
    mock_embed.assert_called_once_with("my query")
