"""
Phase 4: RAG Retrieval Tool

Exposes RAGPipeline.retrieve() as an agent tool (`retrieve_context`),
so the ResearchAgent can pull grounded, cited context chunks instead
of relying purely on the LLM's parametric knowledge.

Registered separately from src/core/tools_impl.py because it requires
a database session, unlike the stateless Phase 2 tools.
"""

import logging
from typing import Any, Dict

from src.core.tools import (
    ToolDefinition,
    ToolType,
    ToolStatus,
    RetrieveContext,
    RetrieveContextResult,
)
from src.rag.database import get_session
from src.rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)


async def retrieve_context(
    question: str,
    top_k: int = 5,
    paper_id: str = None,
) -> Dict[str, Any]:
    """
    Retrieve grounded context chunks for a question from stored papers.

    Args:
        question: Natural language question
        top_k: Number of chunks to retrieve
        paper_id: Optionally restrict to a specific paper

    Returns:
        RetrieveContextResult dict with ranked chunks and formatted context
    """
    logger.info(f"Retrieving RAG context for: '{question}'")

    session = get_session()
    try:
        pipeline = RAGPipeline(session)
        rag_context = pipeline.retrieve(question, top_k=top_k, paper_id=paper_id)

        chunks = [
            {
                "chunk_id": c.chunk_id,
                "paper_id": c.paper_id,
                "content": c.content,
                "section": c.section,
                "score": c.score,
            }
            for c in rag_context.chunks
        ]

        return {
            "question": question,
            "chunks": chunks,
            "context_text": rag_context.to_prompt_context(),
        }
    finally:
        session.close()


RETRIEVE_CONTEXT_TOOL = ToolDefinition(
    name="retrieve_context",
    type=ToolType.RETRIEVE,
    description=(
        "Retrieve grounded, cited context chunks from previously ingested papers "
        "using semantic vector search. Use this AFTER search_literature has "
        "populated the database, to pull the most relevant passages for answering "
        "a specific question with citations rather than relying on memory."
    ),
    input_schema=RetrieveContext,
    output_schema=RetrieveContextResult,
    execution_fn=retrieve_context,
    status=ToolStatus.AVAILABLE,
    tags=["rag", "retrieval", "vector-search"],
)


def register_rag_tools(registry) -> None:
    """Register Phase 4 RAG tools to a registry."""
    registry.register(RETRIEVE_CONTEXT_TOOL)
    logger.info("Registered RAG tools (retrieve_context)")
