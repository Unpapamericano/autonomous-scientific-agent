"""
Phase 3: Database Models

SQLAlchemy models for storing:
  - Papers (metadata, full text)
  - Document chunks (for RAG)
  - Embeddings (vectors, Phase 4)
  - Searches (history, audit trail)
  - Research sessions (Phase 2 agent state)

Uses PostgreSQL + pgvector (Phase 4+).

Note: SQLAlchemy's Declarative API reserves the attribute name `metadata`
on model classes (it's used internally for `Base.metadata`, the schema
registry). All "extra metadata" JSON columns below are therefore exposed
as the Python attribute `extra_metadata`, while the actual database
column is still named `metadata` for readability in SQL.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    JSON,
    Index,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

try:
    # pgvector.sqlalchemy provides a proper Vector column type for PostgreSQL.
    # Falls back to JSON storage if pgvector isn't installed (e.g. in CI/local
    # SQLite testing), so Phase 4 code can still import/run without it.
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:  # pragma: no cover
    Vector = None
    PGVECTOR_AVAILABLE = False

from src.rag.embeddings import EMBEDDING_DIM

Base = declarative_base()


def embedding_column():
    """Return the appropriate column type for storing embeddings."""
    if PGVECTOR_AVAILABLE:
        return Column(Vector(EMBEDDING_DIM), nullable=True)
    return Column(JSON, nullable=True)  # fallback: list of floats as JSON


def metadata_column():
    """Return a JSON 'extra metadata' column, avoiding the reserved `metadata` attribute name."""
    return Column("metadata", JSON, nullable=True)


class Paper(Base):
    """Scientific paper metadata."""

    __tablename__ = "papers"

    id = Column(String(100), primary_key=True)  # doi, arxiv_id, pubmed_id
    title = Column(String(500), nullable=False, index=True)
    authors = Column(JSON, nullable=True)  # List of author names
    year = Column(Integer, nullable=True, index=True)
    abstract = Column(Text, nullable=True)

    source = Column(String(50), nullable=False, index=True)  # "pubmed", "arxiv", "openalex"
    url = Column(String(500), nullable=True)
    doi = Column(String(200), nullable=True, unique=True, index=True)
    journal = Column(String(200), nullable=True)
    publish_date = Column(String(50), nullable=True)

    full_text = Column(Text, nullable=True)  # Full paper text (optional, Phase 5+)
    retrieved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    extra_metadata = metadata_column()  # Additional fields

    # Phase 4: Abstract-level embedding (fast paper-level semantic search)
    abstract_embedding = embedding_column()
    embedding_model = Column(String(100), nullable=True)

    chunks = relationship("DocumentChunk", back_populates="paper", cascade="all, delete-orphan")
    search_results = relationship("SearchResult", back_populates="paper")

    __table_args__ = (
        Index("idx_paper_doi_source", "doi", "source"),
        Index("idx_paper_year", "year"),
    )

    def __repr__(self):
        return f"<Paper {self.id}: {self.title[:50]}...>"


class DocumentChunk(Base):
    """Text chunk from a paper (for RAG)."""

    __tablename__ = "document_chunks"

    id = Column(String(100), primary_key=True)
    paper_id = Column(String(100), ForeignKey("papers.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)  # Sequence number
    content = Column(Text, nullable=False)
    section = Column(String(100), nullable=True)  # e.g., "introduction", "methods", "results"
    page_number = Column(Integer, nullable=True)

    # Phase 4: Embedding vector (pgvector column, falls back to JSON)
    embedding = embedding_column()
    embedding_model = Column(String(100), nullable=True)  # which model generated it

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    extra_metadata = metadata_column()

    paper = relationship("Paper", back_populates="chunks")
    evidence_items = relationship("Evidence", back_populates="chunk")

    __table_args__ = (
        UniqueConstraint("paper_id", "chunk_index", name="uq_paper_chunk"),
        Index("idx_chunk_paper_section", "paper_id", "section"),
    )

    def __repr__(self):
        return f"<Chunk {self.id}: {self.content[:50]}...>"


class Search(Base):
    """Search query and results (audit trail)."""

    __tablename__ = "searches"

    id = Column(String(100), primary_key=True)
    query = Column(String(500), nullable=False)
    sources = Column(JSON, nullable=False)  # ["pubmed", "arxiv", ...]
    limit = Column(Integer, default=10, nullable=False)
    year_from = Column(Integer, nullable=True)
    year_to = Column(Integer, nullable=True)

    result_count = Column(Integer, default=0, nullable=False)
    duration_ms = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    session_id = Column(String(100), nullable=True, index=True)  # Links to agent session
    extra_metadata = metadata_column()

    search_results = relationship("SearchResult", back_populates="search", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Search {self.id}: '{self.query}' -> {self.result_count} results>"


class SearchResult(Base):
    """One paper in a search result."""

    __tablename__ = "search_results"

    id = Column(String(100), primary_key=True)
    search_id = Column(String(100), ForeignKey("searches.id"), nullable=False, index=True)
    paper_id = Column(String(100), ForeignKey("papers.id"), nullable=False, index=True)
    rank = Column(Integer, nullable=False)  # Position in results
    relevance_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    search = relationship("Search", back_populates="search_results")
    paper = relationship("Paper", back_populates="search_results")

    __table_args__ = (
        UniqueConstraint("search_id", "paper_id", name="uq_search_paper"),
        Index("idx_search_rank", "search_id", "rank"),
    )

    def __repr__(self):
        return f"<SearchResult {self.search_id} → {self.paper_id} (rank {self.rank})>"


class Claim(Base):
    """Scientific claim extracted from a paper."""

    __tablename__ = "claims"

    id = Column(String(100), primary_key=True)
    paper_id = Column(String(100), ForeignKey("papers.id"), nullable=False, index=True)
    claim_text = Column(Text, nullable=False)
    section = Column(String(100), nullable=True)  # Where in paper
    claim_type = Column(String(50), nullable=True)  # "finding", "hypothesis", "limitation", etc.

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    extra_metadata = metadata_column()

    evidence_items = relationship("Evidence", back_populates="claim", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Claim {self.id}: {self.claim_text[:50]}...>"


class Evidence(Base):
    """Supporting evidence for a claim (Phase 5+)."""

    __tablename__ = "evidence"

    id = Column(String(100), primary_key=True)
    claim_id = Column(String(100), ForeignKey("claims.id"), nullable=False, index=True)
    chunk_id = Column(String(100), ForeignKey("document_chunks.id"), nullable=False, index=True)

    evidence_type = Column(String(50), nullable=False)  # "direct", "indirect", "supports", "contradicts"
    confidence = Column(Float, nullable=False)  # 0.0–1.0
    explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    extra_metadata = metadata_column()

    claim = relationship("Claim", back_populates="evidence_items")
    chunk = relationship("DocumentChunk", back_populates="evidence_items")

    __table_args__ = (
        UniqueConstraint("claim_id", "chunk_id", name="uq_claim_evidence"),
        Index("idx_evidence_type_confidence", "evidence_type", "confidence"),
    )

    def __repr__(self):
        return f"<Evidence {self.id}: {self.evidence_type} (conf={self.confidence:.2f})>"


class ResearchSession(Base):
    """Research session (maps to Phase 2 AgentState)."""

    __tablename__ = "research_sessions"

    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), nullable=True, index=True)  # Optional user tracking
    topic = Column(String(500), nullable=True)
    initial_question = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed = Column(Boolean, default=False, nullable=False, index=True)

    # Trajectory state (serialized)
    state_json = Column(JSON, nullable=True)  # Serialized AgentState

    extra_metadata = metadata_column()

    def __repr__(self):
        return f"<ResearchSession {self.id}: {self.topic[:50] if self.topic else 'untagged'}>"


class ToolExecution(Base):
    """Tool execution log (Phase 2 + audit trail)."""

    __tablename__ = "tool_executions"

    id = Column(String(100), primary_key=True)
    session_id = Column(String(100), ForeignKey("research_sessions.id"), nullable=True, index=True)

    tool_name = Column(String(100), nullable=False, index=True)
    tool_input = Column(JSON, nullable=False)
    tool_output = Column(JSON, nullable=True)

    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    extra_metadata = metadata_column()

    def __repr__(self):
        status = "✓" if self.success else "✗"
        return f"<ToolExecution {status} {self.tool_name} ({self.duration_ms:.0f}ms)>"


class Evaluation(Base):
    """Benchmark evaluation result."""

    __tablename__ = "evaluations"

    id = Column(String(100), primary_key=True)
    benchmark_name = Column(String(100), nullable=False, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    quantization = Column(String(50), nullable=True)

    # Results
    accuracy = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    tokens_per_sec = Column(Float, nullable=True)
    vram_mb = Column(Float, nullable=True)
    ram_mb = Column(Float, nullable=True)
    cost_per_query = Column(Float, nullable=True)

    # Task-specific metrics
    metrics = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    extra_metadata = metadata_column()

    def __repr__(self):
        acc = f"{self.accuracy:.2f}" if self.accuracy is not None else "N/A"
        return f"<Evaluation {self.benchmark_name} / {self.model_name}: accuracy={acc}>"


# Summary models for analytics (Phase 4+)


class DocumentStatistics(Base):
    """Document collection statistics."""

    __tablename__ = "document_statistics"

    id = Column(String(100), primary_key=True)
    source = Column(String(50), nullable=False, unique=True)
    total_papers = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    avg_chunk_length = Column(Float, nullable=True)
    year_range = Column(JSON, nullable=True)  # {"min": 2015, "max": 2026}

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DocStats {self.source}: {self.total_papers} papers, {self.total_chunks} chunks>"
