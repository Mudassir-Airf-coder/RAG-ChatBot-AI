"""Rewrite user queries into search-friendly forms.

The LLM (Groq/OpenCode) does the actual rewriting. This module
contains the prompt and the fallback logic.
"""

import re

from app.llm.base import LLMProvider


REWRITE_PROMPT = """You rewrite user questions into search queries for a document retrieval system.

Rules:
1. If the question is already clear and specific, return it UNCHANGED.
2. If the question is vague, short, or conversational (e.g. "hi", "tell me more", "what is this"), rewrite it into a specific question about the documents.
3. Keep the rewrite under 25 words.
4. Do NOT add information not implied by the question.
5. Return ONLY the rewritten question, no explanation, no quotes.

Examples:
- "hi" -> "What is this document about?"
- "tell me more" -> "What are the main points of this document?"
- "?" -> "What is the content of this document?"
- "What was the revenue growth in 2025?" -> "What was the revenue growth in 2025?"
- "compare them" -> "What are the differences between the compared items?"

Question: {question}
Rewrite:"""


async def rewrite_query(question: str, provider: LLMProvider, model: str) -> str:
    """Rewrite a query for better retrieval.

    Falls back to the original question on any error.
    """
    if not question or not question.strip():
        return "What is this document about?"

    # Skip rewriting for specific, detailed questions
    word_count = len(question.split())
    if word_count >= 5 and any(
        kw in question.lower()
        for kw in ("what", "how", "why", "when", "where", "which", "who", "explain")
    ):
        return question

    try:
        prompt = REWRITE_PROMPT.format(question=question)
        raw = await provider.chat(
            model,
            [{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.0,
        )
        rewritten = _clean_rewrite(raw)
        if rewritten and len(rewritten) >= 3:
            return rewritten
    except Exception:
        pass

    return question


def _clean_rewrite(raw: str) -> str:
    """Strip quotes, prefixes, and trailing filler from LLM output."""
    text = raw.strip()
    # Remove common prefixes
    for prefix in ("Rewrite:", "Rewritten:", "Answer:", "Question:"):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    # Remove wrapping quotes
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1].strip()
    # Take only the first line
    text = text.split("\n")[0].strip()
    return text