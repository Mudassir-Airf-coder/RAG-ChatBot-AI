from pathlib import Path


def test_startup_creates_required_directories(tmp_path, monkeypatch):
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "data" / "chatbot.db"))
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))

    from app.config import Settings
    fresh = Settings()
    Path(fresh.upload_dir).mkdir(parents=True, exist_ok=True)
    from app.storage import init_db
    init_db(fresh.sqlite_path)

    assert (tmp_path / "uploads").exists()
    assert (tmp_path / "data" / "chatbot.db").exists()
