import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings
from app.exceptions import ValidationError
from app.llm.groq import GroqProvider
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.storage import create_message, create_chat, update_chat_timestamp

router = APIRouter(prefix="/api/v1", tags=["query"])


class QueryRequest(BaseModel):
    chat_id: str
    question: str
    provider: str
    api_key: str
    model: str


class Citation(BaseModel):
    citation_index: int
    document_id: str
    chunk_id: str


class QueryResponse(BaseModel):
    chat_id: str
    answer: str
    citations: list[Citation]


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    if request.provider != "groq":
        raise ValidationError("Unsupported provider. Use 'groq'.")

    llm = GroqProvider(request.api_key)

    chunks = retrieve(request.question, top_k=5)
    if not chunks:
        raise ValidationError("No document context available. Upload documents first.")

    result = generate_answer(chunks, request.question, llm, request.model)

    msg_id = f"msg_{uuid.uuid4().hex[:12]}"
    create_message(
        message_id=msg_id,
        chat_id=request.chat_id,
        role="user",
        content=request.question,
        sqlite_path=settings.sqlite_path,
    )

    ans_id = f"msg_{uuid.uuid4().hex[:12]}"
    create_message(
        message_id=ans_id,
        chat_id=request.chat_id,
        role="assistant",
        content=result["answer"],
        citations=result["citations"],
        sqlite_path=settings.sqlite_path,
    )

    update_chat_timestamp(request.chat_id, settings.sqlite_path)

    return QueryResponse(
        chat_id=request.chat_id,
        answer=result["answer"],
        citations=[Citation(**c) for c in result["citations"]],
    )
