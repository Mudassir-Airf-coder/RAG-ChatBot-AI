import pytest
from app.config import Settings


def test_settings_loads_defaults():
    s = Settings()
    assert s.qdrant_url == "http://localhost:6333"
    assert s.qdrant_collection == "rag_chatbot"
    assert s.sqlite_path == "./data/chatbot.db"
    assert s.upload_dir == "./uploads"
    assert s.groq_base_url == "https://api.groq.com/openai/v1"
    assert s.log_level == "INFO"
