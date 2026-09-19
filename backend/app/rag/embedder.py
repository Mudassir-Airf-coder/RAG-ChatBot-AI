from functools import lru_cache
import os
from pathlib import Path

from fastembed import TextEmbedding
from numpy import ndarray

from app.config import settings

_MODEL_NAME = "BAAI/bge-small-en-v1.5"
_EMBED_BATCH_SIZE = 64
_EMBED_THREADS = min(4, os.cpu_count() or 1)
_EMBED_CACHE_DIR = Path(settings.sqlite_path).parent / "fastembed_cache"


@lru_cache(maxsize=1)
def _get_model() -> TextEmbedding:
    _EMBED_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return TextEmbedding(
        model_name=_MODEL_NAME,
        cache_dir=str(_EMBED_CACHE_DIR),
        threads=_EMBED_THREADS,
    )


def embed_chunks(texts: list[str]) -> list[ndarray]:
    if not texts:
        return []
    model = _get_model()
    return list(model.embed(texts, batch_size=_EMBED_BATCH_SIZE, parallel=_EMBED_THREADS))


def embed_query(text: str) -> ndarray:
    model = _get_model()
    return list(model.embed([text], batch_size=1, parallel=1))[0]