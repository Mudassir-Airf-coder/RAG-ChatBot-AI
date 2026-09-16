from app.config import Settings


def test_settings_loads_defaults():
    """Settings loads correct defaults when no env vars are set."""
    s = Settings()
    assert s.qdrant_url == "http://localhost:6333"
    assert s.qdrant_collection == "rag_chatbot"
    assert s.sqlite_path == "./data/chatbot.db"
    assert s.upload_dir == "./uploads"
    assert s.opencode_zen_base_url == ""
    assert s.log_level == "INFO"


def test_settings_env_override(monkeypatch):
    """Env vars override defaults."""
    monkeypatch.setenv("QDRANT_URL", "http://custom:6334")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    s = Settings()
    assert s.qdrant_url == "http://custom:6334"
    assert s.log_level == "DEBUG"
