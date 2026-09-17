from app.exceptions import ValidationError
from app.llm.groq import GroqProvider
from app.llm.opencode_zen import OpenCodeZenProvider
from app.llm.base import LLMProvider


def get_provider(base_url: str, api_key: str) -> LLMProvider:
    if "groq.com" in base_url:
        return GroqProvider(api_key)
    if "opencode.ai" in base_url:
        return OpenCodeZenProvider(api_key)
    raise ValidationError("Unsupported provider URL. Use Groq or OpenCode Zen.")
