import httpx

from app.config import settings
from app.exceptions import ProviderError, ValidationError
from app.llm.base import LLMProvider


class GroqProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        api_key = api_key.strip()
        try:
            api_key.encode("ascii")
        except UnicodeEncodeError:
            raise ValidationError("API key contains invalid characters")
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def get_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{settings.groq_base_url}/models",
                    headers=self.headers,
                    timeout=10,
                )
                if resp.status_code == 401:
                    raise ProviderError("Invalid API key")
                if resp.status_code != 200:
                    raise ProviderError(f"Groq returned status {resp.status_code}")
                data = resp.json()
                return [m["id"] for m in data.get("data", [])]
        except UnicodeEncodeError:
            raise ValidationError("API key contains invalid characters")

    async def chat(self, model: str, messages: list[dict], max_tokens: int = 400, temperature: float = 0.2) -> str:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{settings.groq_base_url}/chat/completions",
                    headers=self.headers,
                    json={"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature},
                    timeout=60,
                )
                if resp.status_code == 401:
                    raise ProviderError("Invalid API key")
                if resp.status_code != 200:
                    raise ProviderError(f"Groq returned status {resp.status_code}")
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except UnicodeEncodeError:
            raise ValidationError("API key contains invalid characters")
