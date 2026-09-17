import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.provider import sessions


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup():
    sessions.clear()
    yield
    sessions.clear()


def setup_session(client, session_id="test_session"):
    sessions[session_id] = {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": "gsk_test",
        "model": "llama-3.1-8b-instant",
    }
    client.cookies.set("rag_session", session_id)


@patch("app.api.query.retrieve")
def test_query_no_session_returns_error(mock_retrieve, client):
    resp = client.post("/api/v1/query", json={"question": "What?"})
    assert resp.status_code == 400
    assert "No provider configured" in resp.json()["error"]["message"]


@patch("app.api.query.retrieve")
def test_query_no_documents_returns_abstained(mock_retrieve, client):
    mock_retrieve.return_value = []
    setup_session(client)

    resp = client.post("/api/v1/query", json={"question": "What?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["abstained"] is True
    assert data["abstain_reason"] == "no_documents"
    assert data["citations"] == []


@patch("app.api.query.generate_answer", new_callable=AsyncMock)
@patch("app.api.query.retrieve")
def test_query_with_documents_returns_answer(mock_retrieve, mock_generate, client):
    mock_retrieve.return_value = [
        {"chunk_id": "c1", "document_id": "d1", "chunk_index": 0,
         "chunk_text": "Context text", "metadata": {"filename": "test.md"}, "score": 0.9}
    ]
    mock_generate.return_value = {
        "answer": "The answer is 42.",
        "citations": [{"citation_index": 1, "document_id": "d1", "chunk_id": "c1"}],
    }
    setup_session(client)

    resp = client.post("/api/v1/query", json={"question": "What is the answer?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"] == "The answer is 42."
    assert data["abstained"] is False
    assert len(data["citations"]) == 1
