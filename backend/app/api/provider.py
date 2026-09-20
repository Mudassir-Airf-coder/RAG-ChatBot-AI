import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Response, Request
from pydantic import BaseModel

from app.exceptions import ValidationError
from app.llm import get_provider
from app.embeddings.cohere_cloud import CohereEmbeddingProvider

router = APIRouter(prefix="/api/v1/provider", tags=["provider"])

SESSIONS_FILE = Path("data/sessions.json")


def _load_sessions() -> dict:
    if not SESSIONS_FILE.exists():
        return {}
    try:
        return json.loads(SESSIONS_FILE.read_text())
    except Exception:
        return {}


def _save_sessions(s: dict) -> None:
    SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSIONS_FILE.write_text(json.dumps(s))
    try:
        os.chmod(SESSIONS_FILE, 0o600)
    except Exception:
        pass


sessions: dict[str, dict] = _load_sessions()


def get_session_config(req) -> dict | None:
    session_id = req.cookies.get("rag_session")
    if not session_id:
        return None
    return sessions.get(session_id)


class ModelsRequest(BaseModel):
    base_url: str
    api_key: str


class TestRequest(BaseModel):
    base_url: str
    api_key: str
    model: str


class ConfigRequest(BaseModel):
    name: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    model: str | None = None
    cohere_api_key: str | None = None


@router.post("/models")
async def get_models(request: ModelsRequest) -> dict:
    provider = get_provider(request.base_url, request.api_key)
    models = await provider.get_models()
    return {"models": models}


@router.post("/test")
async def test_connection(request: TestRequest) -> dict:
    provider = get_provider(request.base_url, request.api_key)
    try:
        await provider.chat(
            request.model,
            [{"role": "user", "content": "Reply with the single word: OK"}],
        )
        return {"ok": True, "message": "Connection successful"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/test/cohere")
async def test_cohere(request: TestRequest) -> dict:
    try:
        embedder = CohereEmbeddingProvider(request.api_key)
        embedder.embed_query("test")
        return {"ok": True, "message": "Cohere connection successful"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/config")
async def save_config(request: ConfigRequest, response: Response, req: Request) -> dict:
    existing_id = req.cookies.get("rag_session")
    session_id = existing_id if existing_id and existing_id in sessions else uuid.uuid4().hex

    existing = sessions.get(session_id, {})
    merged = {
        "name": request.name or existing.get("name", ""),
        "base_url": request.base_url or existing.get("base_url", ""),
        "api_key": request.api_key or existing.get("api_key", ""),
        "model": request.model or existing.get("model", ""),
        "cohere_api_key": request.cohere_api_key or existing.get("cohere_api_key", ""),
    }

    # At least one config must be complete
    llm_configured = all([merged["name"], merged["base_url"],
                          merged["api_key"], merged["model"]])
    cohere_configured = bool(merged["cohere_api_key"])

    if not llm_configured and not cohere_configured:
        raise ValidationError(
            "Nothing to save. Provide LLM fields or Cohere key."
        )

    sessions[session_id] = merged
    _save_sessions(sessions)

    response.set_cookie(
        key="rag_session",
        value=session_id,
        httponly=True,
        samesite="lax",
    )
    return {
        "ok": True,
        "llm_configured": llm_configured,
        "cohere_configured": cohere_configured,
    }