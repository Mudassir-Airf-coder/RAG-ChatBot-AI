import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from app.config import settings
from app.exceptions import NotFoundError, ValidationError
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
    filename = file.filename or "unknown"

    upload_dir = Path(settings.upload_dir) / doc_id / "original"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename
    file_path.write_bytes(await file.read())

    doc = create_document(doc_id, filename, status="PROCESSING", sqlite_path=settings.sqlite_path)

    try:
        pages = parse_file(str(file_path))
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

    return DocumentResponse(id=doc_id, filename=filename, status=get_document(doc_id, settings.sqlite_path)["status"])


@router.get("", response_model=DocumentsListResponse)
async def list_docs() -> DocumentsListResponse:
    docs = list_documents(settings.sqlite_path)
    return DocumentsListResponse(documents=docs)


@router.delete("/{id}", status_code=204)
async def delete_doc(id: str) -> None:
    doc = get_document(id, settings.sqlite_path)
    if not doc:
        raise NotFoundError(f"Document {id} not found")
    delete_by_document_id(id)
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
