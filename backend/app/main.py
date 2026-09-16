from fastapi import FastAPI
from app.config import settings
from app.logging import configure_logging, get_logger

configure_logging(settings.log_level)
logger = get_logger(__name__)

app = FastAPI(title="RAG Chatbot", version="0.1.0")


@app.get("/api/v1/health")
async def health() -> dict:
    logger.info("health_check")
    return {"status": "ok"}
