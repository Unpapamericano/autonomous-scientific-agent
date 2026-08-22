"""
Phase 4: RAG Pipeline

Connects literature search (Phase 3), embeddings (Phase 4), and
vector search (Phase 4) into a single retrieval-augmented generation
pipeline usable by the ResearchAgent.

Flow:
    1. Search literature (Phase 3 APIs)
    2. Store papers in DB
    3. Chunk abstracts / full text
    4. Embed chunks
    5. Store embeddings (pgvector)
    6. On a question, embed the question and retrieve top-K chunks
    7. Return chunks as grounded context for the LLM
"""

import logging
import uuid
from typing import List, Optional
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from src.research.apis import AggregatedSearchClient, PaperMetadata
from src.rag.embeddings import get_embedding_generator, chunk_text
from src.rag.vector_search import VectorSearchEngine, ScoredChunk
from src.rag.repositories import PaperRepository, SearchRepository
from src.rag.models import DocumentChunk

logger = logging.getLogger(__name__)


@dataclass
class RAGContext:
    """Grounded context retrieved for a query, ready to feed an LLM."""
    query: str
    chunks: List[ScoredChunk] = field(default_factory=list)

    def to_prompt_context(self) -> str:
        """Format retrieved chunks as a citation-friendly context block."""
        if not self.chunks:
            return "No relevant context found."

        lines = []
        for i, chunk in enumerate(self.chunks, 1):
            lines.append(
                f"[{i}] (paper: {chunk.paper_id}, section: {chunk.section or 'n/a'}, "
                f"relevance: {chunk.score:.2f})\n{chunk.content}"
            )
        return "\n\n".join(lines)


class RAGPipeline:
    """
    End-to-end retrieval-augmented generation pipeline.

    Usage:
        pipeline = RAGPipeline(session)
        await pipeline.ingest_query("CRISPR inherited blindness", limit=10)
        context = pipeline.retrieve("What is the success rate of RPE65 therapy?")
    """

    def __init__(self, session: Session):
        self.session = session
        self.embedder = get_embedding_generator()
        self.vector_engine = VectorSearchEngine(session, self.embedder)
        self.paper_repo = PaperRepository(session)
        self.search_repo = SearchRepository(session)

    async def ingest_query(
        self,
        query: str,
        limit: int = 10,
        sources: Optional[List[str]] = None,
        year_from: Optional[int] = None,
    ) -> int:
        """
        Search literature, store papers + chunks + embeddings.

        Args:
            query: Literature search query
            limit: Max papers to ingest
            sources: Which APIs to search (default: all)
            year_from: Optional year filter

        Returns:
            Number of papers ingested
        """
        client = AggregatedSearchClient()
        try:
            papers_metadata = await client.search(
                query=query,
                limit=limit,
                year_from=year_from,
                sources=sources,
            )
        finally:
            await client.close()

        logger.info(f"Ingesting {len(papers_metadata)} papers for query: {query}")

        search_record = self.search_repo.create(
            query=query,
            sources=sources or ["pubmed", "arxiv", "openalex"],
            limit=limit,
            year_from=year_from,
        )

        ingested = 0
        for rank, meta in enumerate(papers_metadata, 1):
            paper = self.paper_repo.get(meta.paper_id)
            if paper is None:
                paper = self.paper_repo.create(meta)

            self.search_repo.add_result(search_record.id, paper.id, rank=rank)
            self._chunk_and_embed_paper(paper, meta)
            ingested += 1

        self.session.commit()
        logger.info(f"Ingested {ingested} papers with embeddings")
        return ingested

    def _chunk_and_embed_paper(self, paper, meta: PaperMetadata) -> None:
        """Chunk a paper's abstract/text and store embedded chunks."""
        text = meta.abstract or ""
        if not text.strip():
            return

        chunks = chunk_text(text, chunk_size=200, overlap=30)
        if not chunks:
            return

        embeddings = self.embedder.embed_batch(chunks)

        # Remove existing chunks for this paper to avoid duplicates on re-ingest
        self.session.query(DocumentChunk).filter(DocumentChunk.paper_id == paper.id).delete()

        for idx, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                paper_id=paper.id,
                chunk_index=idx,
                content=chunk_content,
                section="abstract",
                embedding=embedding,
                embedding_model=self.embedder.model_name,
            )
            self.session.add(chunk)

        # Also embed the paper abstract directly for paper-level search
        self.vector_engine.embed_and_store_paper_abstract(paper)

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
        paper_id: Optional[str] = None,
    ) -> RAGContext:
        """
        Retrieve the most relevant chunks for a question.

        Args:
            question: Natural language question
            top_k: Number of chunks to retrieve
            paper_id: Optionally restrict to a specific paper

        Returns:
            RAGContext with ranked chunks
        """
        chunks = self.vector_engine.search_chunks(question, top_k=top_k, paper_id=paper_id)
        return RAGContext(query=question, chunks=chunks)

    def backfill_embeddings(self) -> dict:
        """Backfill embeddings for any papers/chunks missing them."""
        chunks_updated = self.vector_engine.backfill_chunk_embeddings()
        papers_updated = self.vector_engine.backfill_paper_embeddings()
        self.session.commit()

        return {
            "chunks_updated": chunks_updated,
            "papers_updated": papers_updated,
        }
