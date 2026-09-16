import pytest
from unittest.mock import MagicMock

from app.rag.generator import generate_answer
from app.exceptions import ValidationError


def test_generates_answer_from_context():
    provider = MagicMock()
    provider.chat = MagicMock(return_value="The answer is 42.")

    chunks = [
        {"chunk_id": "c1", "document_id": "d1", "chunk_index": 0, "chunk_text": "context one"},
        {"chunk_id": "c2", "document_id": "d1", "chunk_index": 1, "chunk_text": "context two"},
    ]

    result = generate_answer(chunks, "What is the answer?", provider, "test-model")

    assert result["answer"] == "The answer is 42."
    assert len(result["citations"]) == 2
    assert result["citations"][0]["citation_index"] == 1
    assert result["citations"][0]["document_id"] == "d1"
    assert result["citations"][0]["chunk_id"] == "c1"


def test_empty_context_raises():
    provider = MagicMock()
    with pytest.raises(ValidationError, match="No document context"):
        generate_answer([], "question", provider, "model")
