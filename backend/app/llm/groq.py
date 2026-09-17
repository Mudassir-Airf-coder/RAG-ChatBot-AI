import httpx

from app.exceptions import ProviderError, ValidationError
from app.llm.base import LLMProvider


class GroqProvider(LLMProvider):
    BASE_URL = "https://api.groq.com/openai/v1"

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
                    f"{self.BASE_URL}/models",
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

    async def chat(self, model: str, messages: list[dict]) -> str:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=self.headers,
                    json={"model": model, "messages": messages},
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
