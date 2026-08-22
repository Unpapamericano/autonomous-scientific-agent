"""
Phase 4: Integration Tests for Embeddings, Vector Search, and RAG Pipeline

Tests use small, fast, mocked or in-memory operations so they run
without requiring a GPU or a live PostgreSQL + pgvector instance.
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, AsyncMock, patch

from src.rag.embeddings import (
    EmbeddingGenerator,
    chunk_text,
    EMBEDDING_DIM,
)


class TestChunkText:
    """Test text chunking logic (pure function, no model needed)."""

    def test_short_text_single_chunk(self):
        """Short text should return as a single chunk."""
        text = "This is a short abstract about CRISPR."
        chunks = chunk_text(text, chunk_size=200, overlap=30)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_empty_text(self):
        """Empty text should return no chunks."""
        assert chunk_text("") == []
        assert chunk_text(None) == []

    def test_long_text_multiple_chunks(self):
        """Long text should be split into multiple overlapping chunks."""
        text = " ".join([f"word{i}" for i in range(1000)])
        chunks = chunk_text(text, chunk_size=200, overlap=30)

        assert len(chunks) > 1
        # Every chunk should have roughly chunk_size words (last one may be shorter)
        for chunk in chunks[:-1]:
            assert len(chunk.split()) <= 200

    def test_overlap_between_chunks(self):
        """Consecutive chunks should share some overlapping words."""
        text = " ".join([f"word{i}" for i in range(500)])
        chunks = chunk_text(text, chunk_size=100, overlap=20)

        assert len(chunks) >= 2
        first_words = set(chunks[0].split()[-20:])
        second_words = set(chunks[1].split()[:20])
        assert len(first_words & second_words) > 0


class TestEmbeddingGeneratorMocked:
    """Test EmbeddingGenerator with a mocked underlying model (no GPU/download)."""

    def _make_generator_with_mock_model(self, dim=EMBEDDING_DIM):
        gen = EmbeddingGenerator(model_name="mock-model")
        mock_model = MagicMock()

        def fake_encode(texts, **kwargs):
            if isinstance(texts, str):
                vec = np.ones(dim) / np.sqrt(dim)
                return vec
            arr = np.array([np.ones(dim) / np.sqrt(dim) for _ in texts])
            return arr

        mock_model.encode.side_effect = fake_encode
        mock_model.get_sentence_embedding_dimension.return_value = dim
        gen._model = mock_model
        return gen

    def test_embed_text_returns_correct_dimension(self):
        gen = self._make_generator_with_mock_model()
        embedding = gen.embed_text("CRISPR gene editing")

        assert len(embedding) == EMBEDDING_DIM
        assert isinstance(embedding, list)

    def test_embed_empty_text_returns_zero_vector(self):
        gen = self._make_generator_with_mock_model()
        embedding = gen.embed_text("")

        assert embedding == [0.0] * EMBEDDING_DIM

    def test_embed_batch(self):
        gen = self._make_generator_with_mock_model()
        embeddings = gen.embed_batch(["text one", "text two", "text three"])

        assert len(embeddings) == 3
        assert all(len(e) == EMBEDDING_DIM for e in embeddings)

    def test_embed_batch_empty_list(self):
        gen = self._make_generator_with_mock_model()
        assert gen.embed_batch([]) == []

    def test_similarity_identical_vectors(self):
        gen = self._make_generator_with_mock_model()
        v = [1.0] + [0.0] * (EMBEDDING_DIM - 1)

        score = gen.similarity(v, v)
        assert abs(score - 1.0) < 1e-6

    def test_similarity_orthogonal_vectors(self):
        gen = self._make_generator_with_mock_model()
        v1 = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
        v2 = [0.0, 1.0] + [0.0] * (EMBEDDING_DIM - 2)

        score = gen.similarity(v1, v2)
        assert abs(score - 0.0) < 1e-6

    def test_rank_by_similarity(self):
        gen = self._make_generator_with_mock_model()

        query = [1.0, 0.0, 0.0] + [0.0] * (EMBEDDING_DIM - 3)
        candidates = [
            [0.0, 1.0, 0.0] + [0.0] * (EMBEDDING_DIM - 3),  # orthogonal
            [1.0, 0.0, 0.0] + [0.0] * (EMBEDDING_DIM - 3),  # identical -> most similar
            [0.7, 0.7, 0.0] + [0.0] * (EMBEDDING_DIM - 3),  # partial match
        ]

        ranked = gen.rank_by_similarity(query, candidates, top_k=3)

        # Index 1 (identical vector) should rank first
        assert ranked[0] == 1

    def test_rank_by_similarity_top_k_limit(self):
        gen = self._make_generator_with_mock_model()

        query = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
        candidates = [query for _ in range(10)]

        ranked = gen.rank_by_similarity(query, candidates, top_k=3)
        assert len(ranked) == 3


@pytest.mark.asyncio
class TestRAGPipelineMocked:
    """Test RAGPipeline orchestration logic with mocked dependencies."""

    async def test_ingest_query_stores_papers_and_chunks(self):
        """Test that ingest_query creates papers, search records, and chunks."""
        from src.rag.pipeline import RAGPipeline
        from src.research.apis import PaperMetadata

        mock_session = MagicMock()

        with patch("src.rag.pipeline.AggregatedSearchClient") as MockClient:
            mock_client_instance = MockClient.return_value
            mock_client_instance.search = AsyncMock(
                return_value=[
                    PaperMetadata(
                        paper_id="p1",
                        title="Paper 1",
                        authors=["A"],
                        year=2024,
                        abstract="CRISPR is used to edit genes and treat inherited blindness.",
                        source="pubmed",
                    )
                ]
            )
            mock_client_instance.close = AsyncMock()

            pipeline = RAGPipeline(mock_session)

            # Mock embedder to avoid loading real model
            pipeline.embedder = MagicMock()
            pipeline.embedder.embed_batch.return_value = [[0.1] * EMBEDDING_DIM]
            pipeline.embedder.model_name = "mock-model"
            pipeline.vector_engine.embed_and_store_paper_abstract = MagicMock()

            # Mock repos
            pipeline.paper_repo.get = MagicMock(return_value=None)
            fake_paper = MagicMock(id="p1")
            pipeline.paper_repo.create = MagicMock(return_value=fake_paper)

            fake_search = MagicMock(id="s1")
            pipeline.search_repo.create = MagicMock(return_value=fake_search)
            pipeline.search_repo.add_result = MagicMock()

            count = await pipeline.ingest_query("CRISPR blindness", limit=5)

            assert count == 1
            pipeline.paper_repo.create.assert_called_once()
            pipeline.search_repo.add_result.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_retrieve_returns_rag_context(self):
        """Test retrieve() wraps vector search results into RAGContext."""
        from src.rag.pipeline import RAGPipeline
        from src.rag.vector_search import ScoredChunk

        mock_session = MagicMock()
        pipeline = RAGPipeline(mock_session)

        pipeline.vector_engine.search_chunks = MagicMock(
            return_value=[
                ScoredChunk(
                    chunk_id="c1",
                    paper_id="p1",
                    content="CRISPR success rate is 90% for RPE65 mutations.",
                    section="results",
                    score=0.92,
                )
            ]
        )

        context = pipeline.retrieve("What is the success rate?", top_k=5)

        assert context.query == "What is the success rate?"
        assert len(context.chunks) == 1
        assert "90%" in context.to_prompt_context()
        assert "[1]" in context.to_prompt_context()

    def test_retrieve_empty_context(self):
        """Test retrieve() with no matching chunks."""
        from src.rag.pipeline import RAGPipeline

        mock_session = MagicMock()
        pipeline = RAGPipeline(mock_session)
        pipeline.vector_engine.search_chunks = MagicMock(return_value=[])

        context = pipeline.retrieve("Unrelated question")

        assert context.chunks == []
        assert "No relevant context" in context.to_prompt_context()


class TestVectorSearchEngineInMemoryFallback:
    """Test VectorSearchEngine's in-memory fallback ranking logic."""

    def test_search_chunks_in_memory_ranks_correctly(self):
        from src.rag.vector_search import VectorSearchEngine

        mock_session = MagicMock()
        engine = VectorSearchEngine(mock_session, embedder=MagicMock())

        # Build fake chunk rows returned by the DB query
        chunk_a = MagicMock(id="a", paper_id="p1", content="low relevance", section=None)
        chunk_a.embedding = [0.0, 1.0] + [0.0] * (EMBEDDING_DIM - 2)

        chunk_b = MagicMock(id="b", paper_id="p1", content="high relevance", section=None)
        chunk_b.embedding = [1.0, 0.0] + [0.0] * (EMBEDDING_DIM - 2)

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [chunk_a, chunk_b]
        mock_session.query.return_value = mock_query

        query_embedding = [1.0, 0.0] + [0.0] * (EMBEDDING_DIM - 2)

        engine.embedder.rank_by_similarity.return_value = [1, 0]  # b first, a second
        engine.embedder.similarity.side_effect = [0.99, 0.1]

        results = engine._search_chunks_in_memory(query_embedding, top_k=2, paper_id=None)

        assert len(results) == 2
        assert results[0].chunk_id == "b"
        assert results[0].score == 0.99
