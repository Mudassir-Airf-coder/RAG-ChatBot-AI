import asyncio
import shutil
import threading
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Request
from pydantic import BaseModel

from app.config import settings
from app.exceptions import NotFoundError, ValidationError
from app.logging import get_logger
from app.embeddings.cohere_cloud import CohereEmbeddingProvider
from app.rag.parser import parse_file
from app.rag.chunker import chunk_text
from app.rag.vectorstore import create_collection, upsert_chunks, delete_by_document_id
from app.storage import (
    create_document,
    delete_document as storage_delete_document,
    get_document,
    list_documents,
    update_document_status,
)
from app.api.provider import get_session_config

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
logger = get_logger(__name__)

MAX_CHUNKS_PER_DOC = settings.max_chunks_per_doc

# Serial ingestion queue - only one document processes at a time
_ingest_semaphore = threading.Semaphore(1)


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


def _ingest_pipeline(
    doc_id: str,
    dest: str,
    safe_name: str,
    embedder,
    collection_name: str,
) -> None:
    """Synchronous ingestion pipeline executed in background thread."""
    t0 = time.perf_counter()
    logger.info("parse_started", document_id=doc_id)
    pages = parse_file(dest)
    logger.info("parse_done", document_id=doc_id, pages=len(pages),
                duration_ms=int((time.perf_counter() - t0) * 1000))

    t1 = time.perf_counter()
    all_chunks = []
    chunk_index = 0
    for page in pages:
        chunks = chunk_text(page["text"])
        for c in chunks:
            c["metadata"] = page.get("metadata", {})
            c["index"] = chunk_index
            chunk_index += 1
        all_chunks.extend(chunks)
    logger.info("chunk_done", document_id=doc_id, chunk_count=len(all_chunks),
                duration_ms=int((time.perf_counter() - t1) * 1000))

    if not all_chunks:
        update_document_status(
            doc_id, "FAILED",
            error_message="No text could be extracted from this document. "
                          "It may be scanned, empty, or corrupted.",
            sqlite_path=settings.sqlite_path,
        )
        logger.warning("ingestion_no_chunks", document_id=doc_id)
        return

    if len(all_chunks) > MAX_CHUNKS_PER_DOC:
        logger.warning("ingestion_rejected_too_many_chunks",
                       document_id=doc_id, chunk_count=len(all_chunks),
                       limit=settings.max_chunks_per_doc)
        update_document_status(
            doc_id, "FAILED",
            error_message=f"Document produces {len(all_chunks)} chunks, "
                          f"exceeds limit of {settings.max_chunks_per_doc}. "
                          f"Split the file or increase max_chunks_per_doc.",
            sqlite_path=settings.sqlite_path,
        )
        raise ValidationError(
            f"Document too large: {len(all_chunks)} chunks exceeds limit "
            f"of {settings.max_chunks_per_doc}"
        )

    t2 = time.perf_counter()
    logger.info("embed_started", document_id=doc_id, chunk_count=len(all_chunks))
    texts = [c["text"] for c in all_chunks]
    # Embed with progress logging
    batch = 64
    embeddings = []
    for i in range(0, len(texts), batch):
        # Check if document was deleted
        if get_document(doc_id, settings.sqlite_path) is None:
            logger.info("ingestion_cancelled_doc_deleted", document_id=doc_id)
            return
        batch_texts = texts[i:i+batch]
        batch_embeddings = embedder.embed_chunks(batch_texts)
        embeddings.extend(batch_embeddings)
        logger.info("embed_progress", document_id=doc_id,
                    done=min(i+batch, len(texts)),
                    total=len(texts))
    logger.info("embed_done", document_id=doc_id,
                duration_ms=int((time.perf_counter() - t2) * 1000))

    t3 = time.perf_counter()
    create_collection(embedder.dimension, collection_name)
    upsert_chunks(collection_name, doc_id, all_chunks, embeddings)
    logger.info("index_done", document_id=doc_id,
                duration_ms=int((time.perf_counter() - t3) * 1000))

    update_document_status(doc_id, "READY", sqlite_path=settings.sqlite_path)


def run_ingestion(doc_id: str, dest: str, safe_name: str, settings_obj,
                  embedder, collection_name: str) -> None:
    """Background task wrapper that runs ingestion with semaphore."""
    try:
        with _ingest_semaphore:
            update_document_status(doc_id, "PROCESSING", sqlite_path=settings_obj.sqlite_path)
            _ingest_pipeline(doc_id, dest, safe_name, embedder, collection_name)
    except Exception as e:
        logger.exception("ingestion_failed", document_id=doc_id, filename=safe_name)
        update_document_status(doc_id, "FAILED", error_message=str(e),
                               sqlite_path=settings_obj.sqlite_path)
        raise


@router.post("/upload", response_model=DocumentResponse, status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    background: BackgroundTasks = None,
    req: Request = None,
) -> DocumentResponse:
    # Get session config with Cohere API key
    session = get_session_config(req)
    if not session or not session.get("cohere_api_key"):
        raise ValidationError("Configure Cohere API key first in the Embedding Provider section")

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

    # Create document with UPLOADED status (not PROCESSING yet)
    doc = create_document(doc_id, safe_name, status="UPLOADED", sqlite_path=settings.sqlite_path)

    # Create Cohere embedder from session
    embedder = CohereEmbeddingProvider(session["cohere_api_key"])
    collection_name = embedder.collection_name

    # Queue background ingestion
    if background is not None:
        background.add_task(run_ingestion, doc_id, str(dest), safe_name, settings,
                            embedder, collection_name)
    else:
        # Fallback for testing without BackgroundTasks
        import asyncio
        asyncio.create_task(asyncio.to_thread(run_ingestion, doc_id, str(dest), safe_name, settings,
                                              embedder, collection_name))

    logger.info("upload_queued", document_id=doc_id, filename=safe_name)

    return DocumentResponse(id=doc_id, filename=safe_name, status="UPLOADED")


@router.get("", response_model=DocumentsListResponse)
async def list_docs() -> DocumentsListResponse:
    docs = list_documents(settings.sqlite_path)
    return DocumentsListResponse(documents=docs)


@router.get("/{id}")
async def get_document_by_id(id: str) -> dict:
    doc = get_document(id, settings.sqlite_path)
    if not doc:
        raise NotFoundError(f"Document {id} not found")
    return doc


@router.delete("/{id}", status_code=204)
async def delete_doc(id: str, req: Request) -> None:
    doc = get_document(id, settings.sqlite_path)
    if not doc:
        raise NotFoundError(f"Document {id} not found")
    session = get_session_config(req)
    collection_name = "rag_chatbot_cohere"
    if session and session.get("cohere_api_key"):
        embedder = CohereEmbeddingProvider(session["cohere_api_key"])
        collection_name = embedder.collection_name
    try:
        delete_by_document_id(collection_name, id)
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
    result = client.retrieve(collection_name="rag_chatbot_cohere", ids=[chunk_id], with_payload=True)
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