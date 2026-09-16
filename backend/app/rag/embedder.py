from numpy import ndarray

_model = None


def _get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding
        _model = TextEmbedding("BAAI/bge-small-en-v1.5")
    return _model


def embed_chunks(chunks: list[str]) -> list[ndarray]:
    model = _get_model()
    return list(model.embed(chunks))


def embed_query(query: str) -> ndarray:
    model = _get_model()
    return list(model.embed([query]))[0]
