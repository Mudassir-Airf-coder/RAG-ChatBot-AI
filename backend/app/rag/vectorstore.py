import uuid

from numpy import ndarray
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

_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def create_collection(collection_name: str | None = None) -> None:
    name = collection_name or settings.qdrant_collection
    client = _get_client()
    collections = client.get_collections().collections
    existing = [c.name for c in collections]

    if name not in existing:
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


def upsert_chunks(
    collection_name: str | None,
    document_id: str,
    chunks: list[dict],
    embeddings: list[ndarray],
) -> None:
    name = collection_name or settings.qdrant_collection
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

    client.upsert(collection_name=name, points=points)


def delete_by_document_id(document_id: str, collection_name: str | None = None) -> None:
    name = collection_name or settings.qdrant_collection
    client = _get_client()
    client.delete(
        collection_name=name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
    )
