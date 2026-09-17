import asyncio

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.exceptions import ValidationError, ProviderError
from app.llm import get_provider
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.api.provider import sessions

router = APIRouter(prefix="/api/v1", tags=["query"])


class QueryRequest(BaseModel):
    question: str


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page: int | None = None
    quote: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    abstained: bool
    abstain_reason: str | None = None


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, req: Request) -> QueryResponse:
    session_id = req.cookies.get("rag_session")
    if not session_id or session_id not in sessions:
        raise ValidationError("No provider configured. Save provider settings first.")

    config = sessions[session_id]
    provider = get_provider(config["base_url"], config["api_key"])
    model = config["model"]

    chunks = retrieve(request.question, top_k=5)
    if not chunks:
        return QueryResponse(
            answer="I could not find any relevant information in the uploaded documents.",
            citations=[],
            abstained=True,
            abstain_reason="no_documents",
        )

    try:
        result = await asyncio.wait_for(
            generate_answer(chunks, request.question, provider, model),
            timeout=30,
        )
    except asyncio.TimeoutError:
        raise ProviderError("LLM request timed out after 30 seconds")

    citations = [
        Citation(
            chunk_id=c.get("chunk_id", ""),
            document_id=c.get("document_id", ""),
            document_name=c.get("metadata", {}).get("filename", ""),
            page=c.get("metadata", {}).get("page"),
            quote=c.get("chunk_text", "")[:200],
        )
        for c in chunks
    ]

    return QueryResponse(
        answer=result["answer"],
        citations=citations,
        abstained=False,
    )
