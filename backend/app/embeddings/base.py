from abc import ABC, abstractmethod

from numpy import ndarray


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int: ...

    @property
    @abstractmethod
    def collection_name(self) -> str: ...

    @abstractmethod
    def embed_chunks(self, texts: list[str]) -> list[ndarray]: ...

    @abstractmethod
    def embed_query(self, text: str) -> ndarray: ...