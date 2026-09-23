from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import create_chat, create_message, init_db


@pytest.fixture
def client():
    return TestClient(app)


@patch("app.api.chats.settings")
def test_list_chats(mock_settings, client, tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    mock_settings.sqlite_path = db
    create_chat("c1", "Chat 1", db)
    resp = client.get("/api/v1/chats")
    assert resp.status_code == 200
    assert len(resp.json()["chats"]) == 1


@patch("app.api.chats.settings")
def test_create_chat(mock_settings, client, tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    mock_settings.sqlite_path = db
    resp = client.post("/api/v1/chats", json={"title": "My Chat"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Chat"


@patch("app.api.chats.settings")
def test_get_messages(mock_settings, client, tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    mock_settings.sqlite_path = db
    create_chat("c1", "Chat 1", db)
    create_message("m1", "c1", "user", "hello", sqlite_path=db)
    resp = client.get("/api/v1/chats/c1/messages")
    assert resp.status_code == 200
    assert len(resp.json()["messages"]) == 1


@patch("app.api.chats.settings")
def test_delete_chat(mock_settings, client, tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    mock_settings.sqlite_path = db
    create_chat("c1", "Chat 1", db)
    resp = client.delete("/api/v1/chats/c1")
    assert resp.status_code == 204


@patch("app.api.chats.settings")
def test_delete_nonexistent_chat(mock_settings, client, tmp_path):
    db = str(tmp_path / "test.db")
    init_db(db)
    mock_settings.sqlite_path = db
    resp = client.delete("/api/v1/chats/nonexistent")
    assert resp.status_code == 404
