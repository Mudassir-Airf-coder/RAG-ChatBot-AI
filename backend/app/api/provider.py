import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Response
from pydantic import BaseModel

from app.exceptions import ValidationError
from app.llm import get_provider

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


class ModelsRequest(BaseModel):
    base_url: str
    api_key: str


class TestRequest(BaseModel):
    base_url: str
    api_key: str
    model: str


class ConfigRequest(BaseModel):
    name: str
    base_url: str
    api_key: str
    model: str


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


@router.post("/config")
async def save_config(request: ConfigRequest, response: Response) -> dict:
    if not request.name or not request.base_url or not request.api_key or not request.model:
        raise ValidationError("All fields are required")

    session_id = uuid.uuid4().hex
    sessions[session_id] = {
        "name": request.name,
        "base_url": request.base_url,
        "api_key": request.api_key,
        "model": request.model,
    }
    _save_sessions(sessions)
    response.set_cookie(
        key="rag_session",
        value=session_id,
        httponly=True,
        samesite="lax",
    )
    return {"ok": True}
