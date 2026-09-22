from app.exceptions import ValidationError
from app.llm.base import LLMProvider


PROMPTS = {
    "knowledge": """You are a helpful assistant that answers questions using the provided document excerpts.

Rules:
1. If the excerpts contain information relevant to the question, use it. Extract specific facts, names, numbers, and quotes.
2. Answer in 2-4 sentences. Be direct and specific.
3. When you use information from an excerpt, cite it inline like [1] or [2] -- use the number shown before each excerpt.
4. Only say "I couldn't find this in the uploaded documents." if the excerpts are COMPLETELY unrelated to the question. Do not abstain just because the answer is partial.
5. Do not repeat the question. Do not add filler like "Sure!" or "Great question!".
6. Do not use bullet points or lists unless the user asks for them.
7. If excerpts conflict, mention the conflict in one sentence.
8. Reply in the same language as the question (Hindi in -> Hindi out, English in -> English out).
9. If you cite, cite only the excerpts you actually used. Do not cite every excerpt.""",

    "summarize": """You are a helpful assistant that summarizes documents.

Rules:
1. Provide a clear overview in 3-6 sentences or bullet points.
2. Organize logically (main topic -> key points -> details).
3. Cite as [1] [2] when using specific excerpts.
4. Reply in the same language as the question.""",

    "verbatim": """You are a strict text extractor.

Rules:
1. Output the excerpt text VERBATIM. Do not summarize, paraphrase, or shorten.
2. Preserve formatting, headings, line breaks, and exact wording.
3. If multiple excerpts are provided, output them in order, separated by a line of "---".
4. Do NOT add commentary, intro, or outro. Only the raw text.
5. Do NOT cite or add [1] [2] markers.""",

    "teach": """You are a patient teacher explaining a topic to a beginner.

Rules:
1. Explain in simple, clear language. Avoid jargon.
2. Use a step-by-step structure: what it is -> why it matters -> how it works -> example.
3. Use short sentences and everyday examples.
4. Cite source excerpts as [1] [2] at the end of relevant paragraphs.
5. Reply in the same language as the question.""",

    "compare": """You are a helpful assistant that compares items.

Rules:
1. Structure the answer as: similarities -> differences -> recommendation (if asked).
2. Use concise sentences. Bullet points are OK.
3. Cite sources as [1] [2].
4. Reply in the same language as the question.""",
}


def _get_system_prompt(intent_category: str) -> str:
    return PROMPTS.get(intent_category, PROMPTS["knowledge"])


def _format_context(chunks: list[dict], intent_category: str = "knowledge") -> str:
    """Format chunks as numbered excerpts for the LLM."""
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        text = chunk.get("chunk_text", "").strip()
        if not text:
            continue
        # For verbatim mode, don't truncate
        parts.append(f"[{i}] {text}")
    return "\n\n".join(parts)


async def generate_answer(
    context_chunks: list[dict],
    question: str,
    provider: LLMProvider,
    model: str,
    intent_category: str = "knowledge",
    max_tokens: int = 500,
    temperature: float = 0.1,
) -> dict:
    """Generate a grounded answer with citations.

    Returns:
        {"answer": str, "citations": list[dict], "used_indices": list[int]}
        where used_indices are the 1-based excerpt numbers the LLM actually
        referenced in its answer.
    """
    if not context_chunks:
        raise ValidationError("No document context available for answering")

    context_text = _format_context(context_chunks, intent_category)
    system_prompt = _get_system_prompt(intent_category)
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Excerpts:\n{context_text}\n\nQuestion: {question}",
        },
    ]

    answer = await provider.chat(
        model,
        messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    used_indices = _extract_used_indices(answer, max_index=len(context_chunks))

    citations = []
    for i, chunk in enumerate(context_chunks, start=1):
        if i not in used_indices:
            continue
        citations.append(
            {
                "citation_index": len(citations) + 1,
                "excerpt_index": i,
                "document_id": chunk.get("document_id", ""),
                "chunk_id": chunk.get("chunk_id", ""),
            }
        )

    return {
        "answer": answer,
        "citations": citations,
        "used_indices": sorted(used_indices),
    }


def _extract_used_indices(answer: str, max_index: int) -> set[int]:
    """Parse [N] references from the answer text."""
    import re
    used: set[int] = set()
    for match in re.finditer(r"\[(\d+)\]", answer):
        try:
            n = int(match.group(1))
        except ValueError:
            continue
        if 1 <= n <= max_index:
            used.add(n)
    return used