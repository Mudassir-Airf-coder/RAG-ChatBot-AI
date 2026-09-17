from pydantic import BaseModel

from app.exceptions import ValidationError
from app.llm.groq import GroqProvider

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
    if request.provider != "groq":
        raise ValidationError("Unsupported provider. Use 'groq'.")
    provider = GroqProvider(request.api_key)
    models = await provider.get_models()
    return ModelsResponse(provider=request.provider, models=models)
