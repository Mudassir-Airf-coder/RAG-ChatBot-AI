from app.rag.chunker import chunk_text


def test_short_text_returns_one_chunk():
    result = chunk_text("Hello world", chunk_size=500, overlap=50)
    assert len(result) == 1
    assert result[0]["text"] == "Hello world"
    assert result[0]["index"] == 0


def test_long_text_returns_multiple_chunks():
    text = "word " * 200
    result = chunk_text(text, chunk_size=500, overlap=50)
    assert len(result) > 1


def test_overlap_exists():
    text = "a" * 600
    result = chunk_text(text, chunk_size=500, overlap=50)
    assert len(result) >= 2
    tail = result[0]["text"][-50:]
    assert tail in result[1]["text"]


def test_empty_text():
    result = chunk_text("")
    assert result == []


def test_exact_chunk_size():
    text = "x" * 500
    result = chunk_text(text, chunk_size=500, overlap=50)
    assert len(result) >= 1
    assert result[0]["text"] == text
    assert result[0]["index"] == 0
