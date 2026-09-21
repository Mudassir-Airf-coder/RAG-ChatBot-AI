import asyncio

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.config import settings
from app.exceptions import ValidationError, ProviderError
from app.llm import get_provider
from app.embeddings.cohere_cloud import CohereEmbeddingProvider
from app.rag.retriever import retrieve
from app.rag.generator import generate_answer
from app.rag.query_rewriter import rewrite_query
from app.api.provider import get_session_config

router = APIRouter(prefix="/api/v1", tags=["query"])


class QueryRequest(BaseModel):
    question: str


class Citation(BaseModel):
    citation_index: int
    document_id: str
    chunk_id: str
    document_name: str = ""
    page: int | None = None
    quote: str = ""


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    abstained: bool
    abstain_reason: str | None = None
    rewritten_query: str | None = None


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, req: Request) -> QueryResponse:
    session = get_session_config(req)
    if not session or not session.get("cohere_api_key"):
        raise ValidationError(
            "Configure Cohere API key first in the Embedding Provider section"
        )

    llm_config = {
        "base_url": session.get("base_url"),
        "api_key": session.get("api_key"),
        "model": session.get("model"),
    }
    if not all(llm_config.values()):
        raise ValidationError("Configure LLM provider first (Groq or OpenCode Zen)")

    provider = get_provider(llm_config["base_url"], llm_config["api_key"])
    model = llm_config["model"]
    embedder = CohereEmbeddingProvider(session["cohere_api_key"])

    # Step 1: rewrite query if vague
    rewritten = await rewrite_query(request.question, provider, model)

    # Step 2: retrieve
    chunks = retrieve(
        rewritten,
        top_k=settings.retrieval_top_k,
        collection_name=embedder.collection_name,
        embedder=embedder,
    )

    if not chunks:
        return QueryResponse(
            answer="I couldn't find any relevant information in the uploaded documents.",
            citations=[],
            abstained=True,
            abstain_reason="no_documents",
            rewritten_query=rewritten if rewritten != request.question else None,
        )

    # Step 3: trim context to top N
    chunks = chunks[: settings.max_context_chunks]

    # Step 4: generate
    try:
        result = await asyncio.wait_for(
            generate_answer(chunks, request.question, provider, model),
            timeout=45,
        )
    except asyncio.TimeoutError:
        raise ProviderError("LLM request timed out after 45 seconds")

    # Step 5: detect abstention
    answer_lower = result["answer"].lower()
    abstained = (
        "couldn't find" in answer_lower
        or "could not find" in answer_lower
        or "not in the uploaded documents" in answer_lower
    )

    # Step 6: build citations (only for chunks the LLM actually cited)
    cited_indices = result.get("used_indices", [])
    citations: list[Citation] = []
    for chunk_num in cited_indices:
        chunk = chunks[chunk_num - 1]
        metadata = chunk.get("metadata") or {}
        citations.append(
            Citation(
                citation_index=len(citations) + 1,
                document_id=chunk.get("document_id", ""),
                chunk_id=chunk.get("chunk_id", ""),
                document_name=metadata.get("filename")
                or metadata.get("source", ""),
                page=metadata.get("page"),
                quote=(chunk.get("chunk_text") or "")[:200],
            )
        )

    return QueryResponse(
        answer=result["answer"],
        citations=citations,
        abstained=abstained,
        abstain_reason="llm_abstained" if abstained else None,
        rewritten_query=rewritten if rewritten != request.question else None,
    )