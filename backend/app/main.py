from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.exceptions import AppError
from app.logging import configure_logging, get_logger
from app.storage import init_db, mark_stale_processing_as_failed

from app.api.provider import router as provider_router
from app.api.documents import router as documents_router
from app.api.query import router as query_router
from app.api.chats import router as chats_router

configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    init_db(settings.sqlite_path)
    stale = mark_stale_processing_as_failed(settings.sqlite_path, max_age_seconds=300)
    if stale:
        logger.info("stale_docs_marked_failed", count=stale)

    from app.rag.embedder import _get_model
    logger.info("loading_embedding_model")
    _get_model()
    logger.info("embedding_model_ready")

    logger.info("startup_complete")
    yield
    logger.info("shutdown")


app = FastAPI(title="RAG Chatbot", version="0.1.0", lifespan=lifespan)

MAX_BODY_BYTES = settings.max_upload_mb * 1024 * 1024


class LimitUploadSize(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path.endswith("/documents/upload"):
            cl = request.headers.get("content-length")
            if cl and int(cl) > MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"error": {"code": "FILE_TOO_LARGE",
                                       "message": f"File exceeds {settings.max_upload_mb} MB limit",
                                       "details": {}}}
                )
        return await call_next(request)


app.add_middleware(LimitUploadSize)

app.include_router(provider_router)
app.include_router(documents_router)
app.include_router(query_router)
app.include_router(chats_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


@app.get("/api/v1/health")
async def health() -> dict:
    logger.info("health_check")
    return {"status": "ok"}


static_dir = Path(__file__).parent.parent / "static"
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
