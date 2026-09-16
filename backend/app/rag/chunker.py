def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    if not text:
        return []

    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            break_point = _find_break_point(text, start, end)
            if break_point > start:
                end = break_point

        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"index": index, "text": chunk})
            index += 1

        start = end - overlap
        if start >= len(text):
            break

    return chunks


def _find_break_point(text: str, start: int, end: int) -> int:
    for sep in ["\n\n", "\n", ". ", " "]:
        last = text.rfind(sep, start, end)
        if last > start:
            return last + len(sep)
    return end
