import pytest
from unittest.mock import AsyncMock

from app.rag.generator import generate_answer
from app.exceptions import ValidationError


@pytest.mark.asyncio
async def test_generates_answer_from_context():
    provider = AsyncMock()
    provider.chat.return_value = "The answer is 42 [1]."

    chunks = [
        {"chunk_id": "c1", "document_id": "d1", "chunk_index": 0, "chunk_text": "context one"},
        {"chunk_id": "c2", "document_id": "d1", "chunk_index": 1, "chunk_text": "context two"},
    ]

    result = await generate_answer(chunks, "What is the answer?", provider, "test-model")

    assert result["answer"] == "The answer is 42 [1]."
    assert len(result["citations"]) == 1
    assert result["citations"][0]["citation_index"] == 1
    assert result["citations"][0]["excerpt_index"] == 1
    assert result["citations"][0]["document_id"] == "d1"
    assert result["citations"][0]["chunk_id"] == "c1"
    assert result["used_indices"] == [1]


@pytest.mark.asyncio
async def test_empty_context_raises():
    provider = AsyncMock()
    with pytest.raises(ValidationError, match="No document context"):
        await generate_answer([], "question", provider, "model")