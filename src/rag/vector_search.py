"""
Phase 4: Vector Search

Semantic similarity search over papers and document chunks using
pgvector (PostgreSQL) or an in-memory fallback for environments
without pgvector installed.

Two search modes:
  - Database mode: uses pgvector's `<->` / `cosine_distance` operator
    for fast indexed search directly in PostgreSQL.
  - In-memory mode: fallback that loads embeddings and ranks with
    numpy (used in tests / when pgvector isn't available).
"""

import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.rag.embeddings import get_embedding_generator, EmbeddingGenerator
from src.rag.models import Paper, DocumentChunk, PGVECTOR_AVAILABLE

logger = logging.getLogger(__name__)


@dataclass
class ScoredChunk:
    """A document chunk with its similarity score."""
    chunk_id: str
    paper_id: str
    content: str
    section: Optional[str]
    score: float


@dataclass
class ScoredPaper:
    """A paper with its similarity score."""
    paper_id: str
    title: str
    abstract: str
    score: float


class VectorSearchEngine:
    """
    Semantic search over papers and chunks.

    Usage:
        engine = VectorSearchEngine(session)
        results = engine.search_chunks("What causes retinitis pigmentosa?", top_k=5)
    """

    def __init__(self, session: Session, embedder: Optional[EmbeddingGenerator] = None):
        self.session = session
        self.embedder = embedder or get_embedding_generator()

    def embed_and_store_chunk(self, chunk: DocumentChunk) -> DocumentChunk:
        """Compute and store an embedding for a single chunk."""
        embedding = self.embedder.embed_text(chunk.content)
        chunk.embedding = embedding
        chunk.embedding_model = self.embedder.model_name
        return chunk

    def embed_and_store_paper_abstract(self, paper: Paper) -> Paper:
        """Compute and store an embedding for a paper's abstract."""
        text = paper.abstract or paper.title
        embedding = self.embedder.embed_text(text)
        paper.abstract_embedding = embedding
        paper.embedding_model = self.embedder.model_name
        return paper

    def backfill_chunk_embeddings(self, batch_size: int = 64) -> int:
        """
        Compute embeddings for any chunks that don't have one yet.

        Returns:
            Number of chunks updated.
        """
        chunks = (
            self.session.query(DocumentChunk)
            .filter(DocumentChunk.embedding.is_(None))
            .limit(batch_size)
            .all()
        )

        if not chunks:
            return 0

        texts = [c.content for c in chunks]
        embeddings = self.embedder.embed_batch(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
            chunk.embedding_model = self.embedder.model_name

        logger.info(f"Backfilled embeddings for {len(chunks)} chunks")
        return len(chunks)

    def backfill_paper_embeddings(self, batch_size: int = 64) -> int:
        """Compute abstract embeddings for papers missing one."""
        papers = (
            self.session.query(Paper)
            .filter(Paper.abstract_embedding.is_(None))
            .limit(batch_size)
            .all()
        )

        if not papers:
            return 0

        texts = [p.abstract or p.title for p in papers]
        embeddings = self.embedder.embed_batch(texts)

        for paper, embedding in zip(papers, embeddings):
            paper.abstract_embedding = embedding
            paper.embedding_model = self.embedder.model_name

        logger.info(f"Backfilled embeddings for {len(papers)} papers")
        return len(papers)

    def search_chunks(
        self,
        query: str,
        top_k: int = 5,
        paper_id: Optional[str] = None,
    ) -> List[ScoredChunk]:
        """
        Semantic search over document chunks.

        Args:
            query: Natural language query
            top_k: Number of results to return
            paper_id: Optionally restrict search to a single paper

        Returns:
            List of ScoredChunk, sorted by similarity descending
        """
        query_embedding = self.embedder.embed_text(query)

        if PGVECTOR_AVAILABLE:
            return self._search_chunks_pgvector(query_embedding, top_k, paper_id)
        return self._search_chunks_in_memory(query_embedding, top_k, paper_id)

    def _search_chunks_pgvector(
        self,
        query_embedding: List[float],
        top_k: int,
        paper_id: Optional[str],
    ) -> List[ScoredChunk]:
        """Use pgvector's cosine distance operator for fast DB-side search."""
        q = self.session.query(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        ).filter(DocumentChunk.embedding.isnot(None))

        if paper_id:
            q = q.filter(DocumentChunk.paper_id == paper_id)

        q = q.order_by("distance").limit(top_k)

        results = []
        for chunk, distance in q.all():
            score = 1.0 - float(distance)  # cosine distance -> similarity
            results.append(
                ScoredChunk(
                    chunk_id=chunk.id,
                    paper_id=chunk.paper_id,
                    content=chunk.content,
                    section=chunk.section,
                    score=score,
                )
            )
        return results

    def _search_chunks_in_memory(
        self,
        query_embedding: List[float],
        top_k: int,
        paper_id: Optional[str],
    ) -> List[ScoredChunk]:
        """Fallback: load embeddings into memory and rank with numpy."""
        q = self.session.query(DocumentChunk).filter(DocumentChunk.embedding.isnot(None))
        if paper_id:
            q = q.filter(DocumentChunk.paper_id == paper_id)

        chunks = q.all()
        if not chunks:
            return []

        embeddings = [c.embedding for c in chunks]
        ranked_indices = self.embedder.rank_by_similarity(query_embedding, embeddings, top_k=top_k)

        results = []
        for idx in ranked_indices:
            chunk = chunks[idx]
            score = self.embedder.similarity(query_embedding, chunk.embedding)
            results.append(
                ScoredChunk(
                    chunk_id=chunk.id,
                    paper_id=chunk.paper_id,
                    content=chunk.content,
                    section=chunk.section,
                    score=score,
                )
            )
        return results

    def search_papers(self, query: str, top_k: int = 5) -> List[ScoredPaper]:
        """
        Semantic search over paper abstracts.

        Args:
            query: Natural language query
            top_k: Number of results to return

        Returns:
            List of ScoredPaper, sorted by similarity descending
        """
        query_embedding = self.embedder.embed_text(query)

        if PGVECTOR_AVAILABLE:
            q = self.session.query(
                Paper,
                Paper.abstract_embedding.cosine_distance(query_embedding).label("distance"),
            ).filter(Paper.abstract_embedding.isnot(None))
            q = q.order_by("distance").limit(top_k)

            results = []
            for paper, distance in q.all():
                score = 1.0 - float(distance)
                results.append(
                    ScoredPaper(
                        paper_id=paper.id,
                        title=paper.title,
                        abstract=paper.abstract or "",
                        score=score,
                    )
                )
            return results

        # In-memory fallback
        papers = self.session.query(Paper).filter(Paper.abstract_embedding.isnot(None)).all()
        if not papers:
            return []

        embeddings = [p.abstract_embedding for p in papers]
        ranked_indices = self.embedder.rank_by_similarity(query_embedding, embeddings, top_k=top_k)

        results = []
        for idx in ranked_indices:
            paper = papers[idx]
            score = self.embedder.similarity(query_embedding, paper.abstract_embedding)
            results.append(
                ScoredPaper(
                    paper_id=paper.id,
                    title=paper.title,
                    abstract=paper.abstract or "",
                    score=score,
                )
            )
        return results
