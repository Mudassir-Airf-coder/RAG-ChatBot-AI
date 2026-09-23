from dataclasses import dataclass

FOLLOWUP_PHRASES = [
    "do this",
    "do that",
    "continue",
    "go on",
    "tell me more",
    "elaborate",
    "expand",
    "more details",
    "and then",
    "what about",
    "how about",
    "the same",
    "as above",
    "summarize that",
    "explain that",
]

ANALYTICAL_KEYWORDS = [
    "count",
    "how many",
    "most common",
    "most frequent",
    "top ",
    "frequency",
    "list all",
    "list every",
    "tally",
]


@dataclass
class Intent:
    category: str  # "knowledge", "summarize", "verbatim", "teach", "compare", "followup", "analytical"
    rewrite_needed: bool
    max_chunks: int
    temperature: float


def classify_intent(question: str, has_history: bool = False) -> Intent:
    q = question.lower().strip()

    # Follow-up detection — only if there IS history
    if has_history:
        for phrase in FOLLOWUP_PHRASES:
            if phrase in q:
                return Intent("followup", rewrite_needed=False, max_chunks=10, temperature=0.1)
        # Very short vague queries with history → also follow-up
        if len(q.split()) <= 3:
            return Intent("followup", rewrite_needed=False, max_chunks=10, temperature=0.1)

    # Analytical queries
    if any(kw in q for kw in ANALYTICAL_KEYWORDS):
        return Intent("analytical", rewrite_needed=False, max_chunks=15, temperature=0.0)

    # Verbatim / as-is / raw extraction
    if any(
        kw in q
        for kw in [
            "as is",
            "as-is",
            "verbatim",
            "exact text",
            "raw text",
            "copy paste",
            "quote",
            "without changes",
            "write this docs",
            "print the document",
            "show me the full text",
        ]
    ):
        return Intent("verbatim", rewrite_needed=False, max_chunks=15, temperature=0.0)

    # Teaching / explanation mode
    if any(
        kw in q
        for kw in [
            "act as teacher",
            "teach me",
            "explain like",
            "explain to me",
            "for beginner",
            "in simple terms",
            "eli5",
            "step by step",
        ]
    ):
        return Intent("teach", rewrite_needed=False, max_chunks=10, temperature=0.2)

    # Summarization
    if any(
        kw in q
        for kw in [
            "summarize",
            "summary",
            "overview",
            "tl;dr",
            "in short",
        ]
    ):
        return Intent("summarize", rewrite_needed=False, max_chunks=12, temperature=0.1)

    # Comparison
    if any(kw in q for kw in ["compare", "difference", "vs", "versus"]):
        return Intent("compare", rewrite_needed=False, max_chunks=10, temperature=0.1)

    # Default: knowledge query
    # Only rewrite if short/vague
    words = q.split()
    vague = len(words) < 5 or not any(
        w in q for w in ["what", "how", "why", "when", "where", "which", "who", "explain"]
    )
    return Intent("knowledge", rewrite_needed=vague, max_chunks=10, temperature=0.1)
