from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def __init__(self, api_key: str) -> None:
        ...

    @abstractmethod
    async def get_models(self) -> list[str]:
        ...

    @abstractmethod
    async def chat(self, model: str, messages: list[dict]) -> str:
        ...
