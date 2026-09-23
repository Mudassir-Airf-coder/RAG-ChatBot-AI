import tempfile
from pathlib import Path

from app.rag.parser import parse_file


def test_parse_txt():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello world\nSecond line")
        path = f.name

    result = parse_file(path)
    assert len(result) == 1
    assert result[0]["text"] == "Hello world\nSecond line"
    assert result[0]["metadata"]["source"].endswith(".txt")
    Path(path).unlink()


def test_parse_markdown():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Title\n\nFirst section.\n\n## Sub\n\nSecond section.")
        path = f.name

    result = parse_file(path)
    assert len(result) >= 1
    assert any("Title" in r["text"] for r in result)
    Path(path).unlink()


def test_parse_txt_empty():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("")
        path = f.name

    result = parse_file(path)
    assert len(result) == 1
    assert result[0]["text"] == ""
    Path(path).unlink()


def test_parse_unsupported():
    import pytest

    with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
        path = f.name

    with pytest.raises(ValueError, match="Unsupported"):
        parse_file(path)
    Path(path).unlink()
