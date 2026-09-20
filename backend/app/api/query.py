import asyncio

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.exceptions import ValidationError, ProviderError
from app.llm import get_provider
from app.embeddings.cohere_cloud import CohereEmbeddingProvider
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.api.provider import get_session_config

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
    session = get_session_config(req)
    if not session or session.get("cohere_api_key") is None:
        raise ValidationError("Configure Cohere API key first in the Embedding Provider section")

    cohere_key = session["cohere_api_key"]
    llm_config = {
        "base_url": session.get("base_url"),
        "api_key": session.get("api_key"),
        "model": session.get("model"),
    }
    if not llm_config["base_url"] or not llm_config["api_key"] or not llm_config["model"]:
        raise ValidationError("Configure LLM provider first (Groq or OpenCode Zen)")

    provider = get_provider(llm_config["base_url"], llm_config["api_key"])
    model = llm_config["model"]
    embedder = CohereEmbeddingProvider(cohere_key)

    chunks = retrieve(request.question, top_k=5, embedder=embedder)
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