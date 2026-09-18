from app.config import settings
from app.exceptions import ValidationError
from app.llm.base import LLMProvider


async def generate_answer(
    context_chunks: list[dict],
    question: str,
    provider: LLMProvider,
    model: str,
    concise: bool = True,
) -> dict:
    if not context_chunks:
        raise ValidationError("No document context available for answering")

    filtered = [c for c in context_chunks if c.get("score", 0) >= 0.3]
    if not filtered:
        filtered = context_chunks[:3]

    context_text = "\n\n".join(
        f"[{i + 1}] {c['chunk_text']}" for i, c in enumerate(filtered)
    )

    if concise:
        system_prompt = (
            "You are a RAG assistant. Answer questions strictly from the uploaded documents.\n\n"
            "RULES:\n"
            "1. Answer in 1-3 sentences. Only expand if user explicitly asks for detail.\n"
            "2. Use ONLY provided context. Never invent facts.\n"
            "3. If context lacks the answer, reply exactly: \"I couldn't find this in the uploaded documents.\"\n"
            "4. Cite source filename inline when relevant, like [filename.md].\n"
            "5. No filler. No \"Sure!\", \"Great question!\", \"Based on the context...\".\n"
            "6. No bullet points unless user asks for a list.\n"
            "7. If chunks conflict, say so in one sentence.\n"
            "8. Reply in the user's language (Hindi → Hindi, English → English).\n"
            "9. Do not restate the question."
        )
        max_tokens = settings.max_tokens_concise
    else:
        system_prompt = (
            "You are a RAG assistant. Answer questions from the uploaded documents. "
            "Cite sources. If context lacks the answer, say so."
        )
        max_tokens = settings.max_tokens_verbose

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {question}"},
    ]

    answer = await provider.chat(model, messages, max_tokens=max_tokens, temperature=0.2)

    citations = [
        {
            "citation_index": i + 1,
            "document_id": c["document_id"],
            "chunk_id": c["chunk_id"],
        }
        for i, c in enumerate(filtered)
    ]

    return {"answer": answer, "citations": citations}
