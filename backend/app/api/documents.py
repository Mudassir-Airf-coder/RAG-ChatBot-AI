import json
import shutil
import traceback
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from app.config import settings
from app.exceptions import NotFoundError, ValidationError
from app.logging import get_logger
from app.rag.parser import parse_file
from app.rag.chunker import chunk_text
from app.rag.embedder import embed_chunks
from app.rag.vectorstore import create_collection, upsert_chunks, delete_by_document_id
from app.storage import (
    create_document,
    delete_document as storage_delete_document,
    get_document,
    list_documents,
    update_document_status,
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
logger = get_logger(__name__)

MAX_CHUNKS_PER_DOC = settings.max_chunks_per_doc


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str


class DocumentsListResponse(BaseModel):
    documents: list[dict]


class ChunkResponse(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    text: str
    metadata: dict


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(file: UploadFile = File(...)) -> DocumentResponse:
    doc_id = f"doc_{uuid.uuid4().hex[:12]}"
    safe_name = Path(file.filename or "upload.bin").name

    upload_dir = Path(settings.upload_dir) / doc_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / safe_name

    size = 0
    chunk_size = 1024 * 1024

    try:
        with dest.open("wb") as out:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                size += len(chunk)
                if size > settings.max_upload_mb * 1024 * 1024:
                    raise ValidationError(f"File exceeds {settings.max_upload_mb} MB limit")
                out.write(chunk)
    except Exception:
        shutil.rmtree(upload_dir, ignore_errors=True)
        raise

    logger.info("upload_streamed", document_id=doc_id, size_bytes=size, filename=safe_name)

    doc = create_document(doc_id, safe_name, status="PROCESSING", sqlite_path=settings.sqlite_path)

    try:
        pages = parse_file(str(dest))
        all_chunks = []
        for page in pages:
            chunks = chunk_text(page["text"])
            for c in chunks:
                c["metadata"] = page.get("metadata", {})
            all_chunks.extend(chunks)

        if all_chunks:
            texts = [c["text"] for c in all_chunks]
            embeddings = embed_chunks(texts)
            create_collection()
            upsert_chunks(None, doc_id, all_chunks, embeddings)

        update_document_status(doc_id, "READY", sqlite_path=settings.sqlite_path)
    except Exception as e:
        update_document_status(doc_id, "FAILED", error_message=str(e), sqlite_path=settings.sqlite_path)

    return DocumentResponse(id=doc_id, filename=safe_name, status=get_document(doc_id, settings.sqlite_path)["status"])


@router.get("", response_model=DocumentsListResponse)
async def list_docs() -> DocumentsListResponse:
    docs = list_documents(settings.sqlite_path)
    return DocumentsListResponse(documents=docs)


@router.delete("/{id}", status_code=204)
async def delete_doc(id: str) -> None:
    doc = get_document(id, settings.sqlite_path)
    if not doc:
        raise NotFoundError(f"Document {id} not found")
    try:
        delete_by_document_id(id)
    except Exception as e:
        logger.warning("qdrant_delete_failed", document_id=id, error=str(e))
    upload_dir = Path(settings.upload_dir) / id
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)
    storage_delete_document(id, settings.sqlite_path)


@router.get("/{id}/chunks/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(id: str, chunk_id: str) -> ChunkResponse:
    from qdrant_client import QdrantClient
    client = QdrantClient(url=settings.qdrant_url)
    result = client.retrieve(collection_name=settings.qdrant_collection, ids=[chunk_id], with_payload=True)
    if not result:
        raise NotFoundError(f"Chunk {chunk_id} not found")
    point = result[0]
    payload = point.payload
    return ChunkResponse(
        id=payload["chunk_id"],
        document_id=payload["document_id"],
        chunk_index=payload["chunk_index"],
        text=payload["chunk_text"],
        metadata=payload.get("metadata", {}),
    )
