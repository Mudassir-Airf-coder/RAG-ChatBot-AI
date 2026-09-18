from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def __init__(self, api_key: str) -> None:
        ...

    @abstractmethod
    async def get_models(self) -> list[str]:
        ...

    @abstractmethod
    async def chat(self, model: str, messages: list[dict], max_tokens: int = 400, temperature: float = 0.2) -> str:
        ...
