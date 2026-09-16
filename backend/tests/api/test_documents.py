import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.storage import init_db


@pytest.fixture
def client():
    return TestClient(app)


@patch("app.api.documents.embed_chunks")
@patch("app.api.documents.parse_file")
def test_upload_document(mock_parse, mock_embed, client, tmp_path):
    mock_parse.return_value = [{"text": "hello world", "metadata": {"source": "test.txt"}}]
    mock_embed.return_value = [MagicMock(tolist=lambda: [0.1] * 384)]

    db = str(tmp_path / "test.db")
    init_db(db)

    with patch("app.api.documents.settings") as mock_settings:
        mock_settings.upload_dir = str(tmp_path / "uploads")
        mock_settings.sqlite_path = db
        mock_settings.qdrant_url = "http://localhost:6333"
        mock_settings.qdrant_collection = "test"

        with patch("app.api.documents.create_collection"), \
             patch("app.api.documents.upsert_chunks"):
            resp = client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.txt", b"hello world", "text/plain")},
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data["filename"] == "test.txt"
            assert data["status"] in ("PROCESSING", "READY", "FAILED")


@patch("app.api.documents.settings")
def test_list_documents(mock_settings, client, tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    mock_settings.sqlite_path = db
    resp = client.get("/api/v1/documents")
    assert resp.status_code == 200
    assert "documents" in resp.json()


@patch("app.api.documents.settings")
def test_delete_nonexistent_document(mock_settings, client, tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    mock_settings.sqlite_path = db
    resp = client.delete("/api/v1/documents/nonexistent")
    assert resp.status_code == 404
