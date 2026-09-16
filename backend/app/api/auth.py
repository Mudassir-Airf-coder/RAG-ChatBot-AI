from pydantic import BaseModel

from app.exceptions import ProviderError
from app.llm.groq import GroqProvider
from app.llm.opencode_zen import OpenCodeZenProvider

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class AuthRequest(BaseModel):
    provider: str
    api_key: str


class ModelsResponse(BaseModel):
    provider: str
    models: list[str]


@router.post("/models", response_model=ModelsResponse)
async def get_models(request: AuthRequest) -> ModelsResponse:
    provider = _get_provider(request.provider, request.api_key)
    models = await provider.get_models()
    return ModelsResponse(provider=request.provider, models=models)


def _get_provider(name: str, api_key: str):
    if name == "groq":
        return GroqProvider(api_key)
    elif name == "opencode_zen":
        return OpenCodeZenProvider(api_key)
    else:
        raise ProviderError(f"Unknown provider: {name}")
