import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.storage import init_db, create_chat


@pytest.fixture
def client():
    return TestClient(app)


@patch("app.api.query._get_provider")
@patch("app.api.query.retrieve")
def test_query_returns_answer(mock_retrieve, mock_get_provider, client, tmp_path):
    mock_retrieve.return_value = [
        {"chunk_id": "c1", "document_id": "d1", "chunk_index": 0, "chunk_text": "ctx", "metadata": {}, "score": 0.9}
    ]
    mock_provider = MagicMock()
    mock_provider.chat.return_value = "The answer is yes."
    mock_get_provider.return_value = mock_provider

    db = str(tmp_path / "test.db")
    init_db(db)
    create_chat("chat_test", "Test Chat", sqlite_path=db)

    with patch("app.api.query.settings") as mock_settings:
        mock_settings.sqlite_path = db
        mock_settings.qdrant_url = "http://localhost:6333"
        mock_settings.qdrant_collection = "test"

        resp = client.post("/api/v1/query", json={
            "chat_id": "chat_test",
            "question": "Is it yes?",
            "provider": "groq",
            "api_key": "key",
            "model": "test",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["answer"] == "The answer is yes."
        assert len(data["citations"]) == 1


@patch("app.api.query.retrieve")
def test_query_no_documents_returns_error(mock_retrieve, client):
    mock_retrieve.return_value = []

    with patch("app.api.query.settings") as mock_settings:
        mock_settings.sqlite_path = ":memory:"
        resp = client.post("/api/v1/query", json={
            "chat_id": "chat_test",
            "question": "What?",
            "provider": "groq",
            "api_key": "key",
            "model": "test",
        })
        assert resp.status_code == 400
