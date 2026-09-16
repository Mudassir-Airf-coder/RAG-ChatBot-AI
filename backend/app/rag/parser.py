from pathlib import Path

import fitz
from docx import Document as DocxDocument


def parse_file(file_path: str) -> list[dict]:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _parse_pdf(path)
    elif suffix == ".md":
        return _parse_markdown(path)
    elif suffix == ".txt":
        return _parse_text(path)
    elif suffix == ".docx":
        return _parse_docx(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _parse_pdf(path: Path) -> list[dict]:
    doc = fitz.open(str(path))
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append({
                "text": text,
                "metadata": {"source": path.name, "page": i + 1},
            })
    doc.close()
    return pages


def _parse_markdown(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    sections = []
    current_section = []
    current_heading = None

    for line in text.split("\n"):
        if line.startswith("#"):
            if current_section:
                sections.append(_build_md_section(current_section, current_heading, path.name))
            current_heading = line.lstrip("#").strip()
            current_section = []
        else:
            current_section.append(line)

    if current_section:
        sections.append(_build_md_section(current_section, current_heading, path.name))

    if not sections:
        return [{"text": text, "metadata": {"source": path.name}}]

    return sections


def _build_md_section(lines: list[str], heading: str | None, source: str) -> dict:
    body = "\n".join(lines).strip()
    if heading:
        text = f"# {heading}\n\n{body}" if body else f"# {heading}"
    else:
        text = body
    metadata = {"source": source}
    if heading:
        metadata["heading"] = heading
    return {"text": text, "metadata": metadata}


def _parse_text(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    return [{"text": text, "metadata": {"source": path.name}}]


def _parse_docx(path: Path) -> list[dict]:
    doc = DocxDocument(str(path))
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append({
                "text": text,
                "metadata": {"source": path.name},
            })
    return paragraphs if paragraphs else [{"text": "", "metadata": {"source": path.name}}]
