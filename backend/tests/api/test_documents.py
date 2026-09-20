import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.storage import init_db


@pytest.fixture
def client():
    return TestClient(app)


@patch("app.api.documents.parse_file")
@patch("app.embeddings.cohere_cloud.CohereEmbeddingProvider.embed_chunks")
def test_upload_document(mock_embed, mock_parse, client, tmp_path):
    mock_parse.return_value = [{"text": "hello world", "metadata": {"source": "test.txt"}}]
    mock_embed.return_value = [MagicMock(tolist=lambda: [0.1] * 1024)]

    db = str(tmp_path / "test.db")
    init_db(db)

    with patch("app.api.documents.settings") as mock_settings:
        mock_settings.upload_dir = str(tmp_path / "uploads")
        mock_settings.sqlite_path = db
        mock_settings.qdrant_url = "http://localhost:6333"
        mock_settings.qdrant_collection = "rag_chatbot_cohere"
        mock_settings.max_upload_mb = 10
        mock_settings.max_chunks_per_doc = 150
        mock_settings.chunk_size = 1500
        mock_settings.chunk_overlap = 150

        # Mock session config with Cohere key
        with patch("app.api.documents.get_session_config") as mock_session:
            mock_session.return_value = {"cohere_api_key": "sk-test-key"}

            with patch("app.api.documents.create_collection"), \
                 patch("app.api.documents.upsert_chunks"):
                resp = client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("test.txt", b"hello world", "text/plain")},
                )
                assert resp.status_code == 202
                data = resp.json()
                assert data["filename"] == "test.txt"
                assert data["status"] == "UPLOADED"


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


@patch("app.embeddings.cohere_cloud.CohereEmbeddingProvider.embed_chunks")
@patch("app.api.documents.parse_file")
def test_upload_small_file(mock_parse, mock_embed, client, tmp_path):
    mock_parse.return_value = [{"text": "tiny", "metadata": {}}]
    mock_embed.return_value = [MagicMock(tolist=lambda: [0.1] * 1024)]

    db = str(tmp_path / "test.db")
    init_db(db)

    with patch("app.api.documents.settings") as mock_settings:
        mock_settings.upload_dir = str(tmp_path / "uploads")
        mock_settings.sqlite_path = db
        mock_settings.qdrant_url = "http://localhost:6333"
        mock_settings.qdrant_collection = "rag_chatbot_cohere"
        mock_settings.max_upload_mb = 10
        mock_settings.max_chunks_per_doc = 150
        mock_settings.chunk_size = 1500
        mock_settings.chunk_overlap = 150

        with patch("app.api.documents.get_session_config") as mock_session:
            mock_session.return_value = {"cohere_api_key": "sk-test-key"}

            with patch("app.api.documents.create_collection"), \
                 patch("app.api.documents.upsert_chunks"):
                resp = client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("small.txt", b"tiny content", "text/plain")},
                )
                assert resp.status_code == 202
                data = resp.json()
                assert data["filename"] == "small.txt"
                assert data["id"].startswith("doc_")
                assert data["status"] == "UPLOADED"


def test_upload_rejects_oversized_file(client, tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)

    with patch("app.api.documents.settings") as mock_settings:
        mock_settings.upload_dir = str(tmp_path / "uploads")
        mock_settings.sqlite_path = db
        mock_settings.max_upload_mb = 0

        resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("big.txt", b"any content", "text/plain")},
        )
        assert resp.status_code == 400


@patch("app.embeddings.cohere_cloud.CohereEmbeddingProvider.embed_chunks")
@patch("app.api.documents.parse_file")
def test_upload_streams_to_disk(mock_parse, mock_embed, client, tmp_path):
    mock_parse.return_value = [{"text": "streamed", "metadata": {}}]
    mock_embed.return_value = [MagicMock(tolist=lambda: [0.1] * 1024)]

    db = str(tmp_path / "test.db")
    init_db(db)

    with patch("app.api.documents.settings") as mock_settings:
        mock_settings.upload_dir = str(tmp_path / "uploads")
        mock_settings.sqlite_path = db
        mock_settings.qdrant_url = "http://localhost:6333"
        mock_settings.qdrant_collection = "rag_chatbot_cohere"
        mock_settings.max_upload_mb = 10
        mock_settings.max_chunks_per_doc = 150
        mock_settings.chunk_size = 1500
        mock_settings.chunk_overlap = 150

        with patch("app.api.documents.get_session_config") as mock_session:
            mock_session.return_value = {"cohere_api_key": "sk-test-key"}

            with patch("app.api.documents.create_collection"), \
                 patch("app.api.documents.upsert_chunks"):
                resp = client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("stream.txt", b"content here", "text/plain")},
                )
                assert resp.status_code == 202
                doc_id = resp.json()["id"]
                upload_dir = tmp_path / "uploads" / doc_id
                assert upload_dir.exists()
                assert (upload_dir / "stream.txt").exists()
                assert (upload_dir / "stream.txt").read_bytes() == b"content here"


@patch("app.api.documents.get_session_config")
def test_upload_without_cohere_key_returns_error(mock_session, client, tmp_path):
    mock_session.return_value = None
    db = str(tmp_path / "test.db")
    init_db(db)

    with patch("app.api.documents.settings") as mock_settings:
        mock_settings.upload_dir = str(tmp_path / "uploads")
        mock_settings.sqlite_path = db
        mock_settings.max_upload_mb = 10

        resp = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
        assert resp.status_code == 400
        assert "Cohere API key" in resp.json()["error"]["message"]