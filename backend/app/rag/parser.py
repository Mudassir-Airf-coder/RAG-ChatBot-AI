from pathlib import Path
import os

import fitz
from docx import Document as DocxDocument

from app.exceptions import ParsingError


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
    page_count = doc.page_count

    # Refuse very large PDFs for OCR
    if page_count > 200:
        doc.close()
        raise ParsingError(
            f"PDF has {page_count} pages. OCR on files this large is "
            "not supported. Split the file or use a text-based PDF."
        )

    pages = []

    for i, page in enumerate(doc):
        text = ""

        # Method 1: standard text extraction
        try:
            text = page.get_text("text")
        except Exception:
            text = ""

        # Method 2: try blocks mode if text mode returned nothing
        if not text.strip():
            try:
                blocks = page.get_text("blocks")
                if blocks:
                    text = "\n".join(b[4] for b in blocks if len(b) > 4 and isinstance(b[4], str))
            except Exception:
                pass

        # Method 3: try dict mode as last resort
        if not text.strip():
            try:
                d = page.get_text("dict")
                parts = []
                for block in d.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span.get("text"):
                                parts.append(span["text"])
                    text = " ".join(parts)
            except Exception:
                pass

        if text.strip():
            pages.append({
                "text": text,
                "metadata": {"source": path.name, "page": i + 1},
            })

    doc.close()

    if not pages:
        # No text extracted — likely a scanned/image PDF, try OCR
        try:
            pages = _parse_pdf_ocr(path)
        except ImportError:
            raise ParsingError(
                f"PDF has {page_count} pages but no extractable text. "
                "It appears to be a scanned/image-only PDF. Install "
                "pytesseract and Tesseract OCR to enable OCR: "
                "apt install tesseract-ocr && uv add pytesseract pillow"
            )
        except Exception as e:
            raise ParsingError(
                f"PDF has {page_count} pages but OCR also failed: {e}"
            )

    if not pages:
        raise ParsingError(
            f"PDF has {page_count} pages but no extractable text even "
            "after OCR. The file may be corrupt or unreadable."
        )

    return pages


def _parse_pdf_ocr(path: Path) -> list[dict]:
    """OCR fallback for scanned PDFs."""
    try:
        import pytesseract
    except ImportError:
        raise ImportError("pytesseract not installed")

    try:
        from PIL import Image
    except ImportError:
        raise ImportError("Pillow not installed")

    doc = fitz.open(str(path))
    pages = []
    for i, page in enumerate(doc):
        # Render page to image at 200 DPI
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img)
        if text.strip():
            pages.append({
                "text": text,
                "metadata": {"source": path.name, "page": i + 1, "ocr": True},
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