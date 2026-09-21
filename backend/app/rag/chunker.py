from app.exceptions import ValidationError


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[dict]:
    """Split text into overlapping chunks.

    Prefers paragraph boundaries, then sentence boundaries, then word
    boundaries. Never splits mid-word unless the input has no whitespace.

    Returns a list of {"index": int, "text": str} dicts.
    """
    if not text:
        return []
    if chunk_size <= 0:
        raise ValidationError("chunk_size must be positive")
    if overlap < 0:
        raise ValidationError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValidationError(
            f"overlap ({overlap}) must be < chunk_size ({chunk_size})"
        )

    chunks = []
    start = 0
    index = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)

        if end < n:
            break_point = _find_break_point(text, start, end)
            if break_point > start:
                end = break_point

        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"index": index, "text": chunk})
            index += 1

        if end >= n:
            break

        next_start = end - overlap
        if next_start <= start:
            next_start = start + 1
        start = next_start

    return chunks


def _find_break_point(text: str, start: int, end: int) -> int:
    """Find the best split point between start and end.

    Priority: paragraph break → sentence break → word break.
    Falls back to end if nothing found.
    """
    for sep in ("\n\n", "\n", ". ", "! ", "? ", "; ", ", "):
        last = text.rfind(sep, start, end)
        if last > start + (end - start) // 2:
            return last + len(sep)
    return end