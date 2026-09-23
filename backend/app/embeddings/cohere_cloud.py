import httpx
import numpy as np
from numpy import ndarray

from app.embeddings.base import EmbeddingProvider
from app.exceptions import ProviderError, ValidationError


class CohereEmbeddingProvider(EmbeddingProvider):
    API_URL = "https://api.cohere.com/v1/embed"
    MAX_BATCH = 96

    def __init__(self, api_key: str, model: str = "embed-english-v3.0"):
        api_key = api_key.strip()
        if not api_key:
            raise ValidationError("Cohere API key is required")
        try:
            api_key.encode("ascii")
        except UnicodeEncodeError:
            raise ValidationError("API key contains invalid characters")
        self.api_key = api_key
        self.model = model

    @property
    def dimension(self) -> int:
        return 1024

    @property
    def collection_name(self) -> str:
        return "rag_chatbot_cohere"

    def _embed(self, texts: list[str], input_type: str) -> list[ndarray]:
        out: list[ndarray] = []
        for i in range(0, len(texts), self.MAX_BATCH):
            batch = texts[i : i + self.MAX_BATCH]
            resp = httpx.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "texts": batch,
                    "model": self.model,
                    "input_type": input_type,
                    "truncate": "END",
                },
                timeout=60,
            )
            if resp.status_code == 401:
                raise ProviderError("Invalid Cohere API key")
            if resp.status_code == 429:
                raise ProviderError("Cohere rate limit exceeded")
            if resp.status_code != 200:
                raise ProviderError(f"Cohere returned {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            out.extend(np.array(v, dtype="float32") for v in data["embeddings"])
        return out

    def embed_chunks(self, texts: list[str]) -> list[ndarray]:
        if not texts:
            return []
        return self._embed(texts, "search_document")

    def embed_query(self, text: str) -> ndarray:
        return self._embed([text], "search_query")[0]
