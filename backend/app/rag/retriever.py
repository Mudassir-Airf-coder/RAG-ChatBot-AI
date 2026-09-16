from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config import settings
from app.rag.embedder import embed_query
from app.rag.vectorstore import _get_client


def retrieve(
    query: str,
    top_k: int = 5,
    collection_name: str | None = None,
) -> list[dict]:
    name = collection_name or settings.qdrant_collection
    client = _get_client()
    query_vector = embed_query(query)

    results = client.query_points(
        collection_name=name,
        query=query_vector.tolist(),
        limit=top_k,
        with_payload=True,
    )

    chunks = []
    for point in results.points:
        payload = point.payload
        chunks.append({
            "chunk_id": payload["chunk_id"],
            "document_id": payload["document_id"],
            "chunk_index": payload["chunk_index"],
            "chunk_text": payload["chunk_text"],
            "metadata": payload.get("metadata", {}),
            "score": point.score,
        })

    return chunks
