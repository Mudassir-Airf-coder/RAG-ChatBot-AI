import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config import settings
from app.exceptions import VectorDBError

_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def create_collection(dimension: int, collection_name: str) -> None:
    client = _get_client()
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )


def upsert_chunks(
    collection_name: str,
    document_id: str,
    chunks: list[dict],
    embeddings: list,
) -> None:
    from app.logging import get_logger

    logger = get_logger(__name__)

    client = _get_client()
    points = []

    for chunk, embedding in zip(chunks, embeddings):
        chunk_id = f"chunk_{document_id}_{chunk['index']}"
        point_id = str(uuid.uuid5(_NAMESPACE, chunk_id))
        points.append(
            PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload={
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "chunk_index": chunk["index"],
                    "chunk_text": chunk["text"],
                    "metadata": chunk.get("metadata", {}),
                },
            )
        )

    if not points:
        raise VectorDBError("Cannot upsert empty points list to Qdrant")

    logger.info(
        "upsert_start",
        collection=collection_name,
        doc_id=document_id,
        point_count=len(points),
    )
    try:
        result = client.upsert(collection_name=collection_name, points=points)
        logger.info(
            "upsert_done",
            collection=collection_name,
            doc_id=document_id,
            status=getattr(result, "status", "unknown"),
        )
    except Exception as e:
        logger.exception(
            "upsert_failed",
            collection=collection_name,
            doc_id=document_id,
            error=str(e),
        )
        raise


def delete_by_document_id(collection_name: str, document_id: str) -> None:
    from app.logging import get_logger

    logger = get_logger(__name__)

    client = _get_client()

    # Count before
    before_count = client.count(collection_name=collection_name).count

    client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
    )

    # Count after
    after_count = client.count(collection_name=collection_name).count
    logger.info(
        "delete_done",
        collection=collection_name,
        document_id=document_id,
        removed=before_count - after_count,
        remaining=after_count,
    )
