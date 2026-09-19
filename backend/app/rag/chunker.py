from app.exceptions import ValidationError


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    if not text:
        return []
    if chunk_size <= 0:
        raise ValidationError("chunk_size must be positive")
    if overlap < 0:
        raise ValidationError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValidationError(f"overlap ({overlap}) must be < chunk_size ({chunk_size})")

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

        # Force progress: next start must be > current start
        next_start = end - overlap
        if next_start <= start:
            # Force minimal progress to avoid infinite loop
            next_start = start + 1
        start = next_start

    return chunks


def _find_break_point(text: str, start: int, end: int) -> int:
    for sep in ["\n\n", "\n", ". ", " "]:
        last = text.rfind(sep, start, end)
        if last > start:
            return last + len(sep)
    return end