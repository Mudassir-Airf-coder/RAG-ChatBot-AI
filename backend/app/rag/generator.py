from app.exceptions import ValidationError
from app.llm.base import LLMProvider


async def generate_answer(
    context_chunks: list[dict],
    question: str,
    provider: LLMProvider,
    model: str,
) -> dict:
    if not context_chunks:
        raise ValidationError("No document context available for answering")

    context_text = "\n\n".join(
        f"[{i + 1}] {c['chunk_text']}" for i, c in enumerate(context_chunks)
    )

    messages = [
        {
            "role": "system",
            "content": (
                "Answer the user's question using ONLY the provided context. "
                "If the context does not contain enough information, say so. "
                "Cite your sources using [1], [2], etc."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\nQuestion: {question}",
        },
    ]

    answer = await provider.chat(model, messages)

    citations = [
        {
            "citation_index": i + 1,
            "document_id": c["document_id"],
            "chunk_id": c["chunk_id"],
        }
        for i, c in enumerate(context_chunks)
    ]

    return {"answer": answer, "citations": citations}
