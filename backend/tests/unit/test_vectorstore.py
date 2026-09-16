from unittest.mock import MagicMock, patch
import numpy as np

from app.rag.vectorstore import upsert_chunks, delete_by_document_id


@patch("app.rag.vectorstore._get_client")
def test_upsert_chunks_creates_points(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    chunks = [
        {"index": 0, "text": "first chunk"},
        {"index": 1, "text": "second chunk"},
    ]
    embeddings = [np.zeros(384), np.ones(384)]

    upsert_chunks("test_col", "doc_001", chunks, embeddings)

    mock_client.upsert.assert_called_once()
    call_args = mock_client.upsert.call_args
    points = call_args.kwargs["points"]
    assert len(points) == 2
    assert points[0].id == "chunk_doc_001_0"
    assert points[0].payload["chunk_text"] == "first chunk"
    assert points[0].payload["document_id"] == "doc_001"


@patch("app.rag.vectorstore._get_client")
def test_delete_by_document_id(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    delete_by_document_id("doc_001", "test_col")

    mock_client.delete.assert_called_once()
    call_args = mock_client.delete.call_args
    assert call_args.kwargs["collection_name"] == "test_col"
