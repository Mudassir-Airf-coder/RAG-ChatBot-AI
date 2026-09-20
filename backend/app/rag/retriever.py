from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config import settings
from app.rag.vectorstore import _get_client


def retrieve(
    query: str,
    top_k: int = 5,
    collection_name: str = "rag_chatbot_cohere",
    embedder=None,
) -> list[dict]:
    client = _get_client()
    if embedder is None:
        from app.embeddings.cohere_cloud import CohereEmbeddingProvider
        # This should not happen in production, but provides a fallback for testing
        raise ValueError("Embedder must be provided")
    query_vector = embedder.embed_query(query)

    results = client.query_points(
        collection_name=collection_name,
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