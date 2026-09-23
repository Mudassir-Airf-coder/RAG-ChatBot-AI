from app.rag.vectorstore import _get_client


def retrieve(
    query: str,
    top_k: int = 10,
    collection_name: str = "rag_chatbot_cohere",
    embedder=None,
) -> list[dict]:
    """Retrieve chunks for a query. embedder is required."""
    if embedder is None:
        raise ValueError("embedder is required")

    client = _get_client()
    query_vector = embedder.embed_query(query)

    try:
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector.tolist(),
            limit=top_k,
            with_payload=True,
        )
    except Exception as e:
        # Collection might not exist yet (no documents uploaded)
        if "doesn't exist" in str(e) or "not found" in str(e).lower():
            return []
        raise

    chunks = []
    for point in results.points:
        payload = point.payload or {}
        chunks.append(
            {
                "chunk_id": payload.get("chunk_id", ""),
                "document_id": payload.get("document_id", ""),
                "chunk_index": payload.get("chunk_index", 0),
                "chunk_text": payload.get("chunk_text", ""),
                "metadata": payload.get("metadata", {}),
                "score": point.score,
            }
        )

    return chunks
