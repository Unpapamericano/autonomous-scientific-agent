"""
Phase 3: Integration Tests for Literature APIs and Database

Tests for:
  - Literature API clients (PubMed, arXiv, OpenAlex)
  - Aggregated search
  - Database models & repositories
  - End-to-end search workflow
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.research.apis import (
    PaperMetadata,
    PubMedClient,
    ArxivClient,
    OpenAlexClient,
    AggregatedSearchClient,
)


class TestPaperMetadata:
    """Test PaperMetadata dataclass."""

    def test_create_paper_metadata(self):
        """Test creating paper metadata."""
        paper = PaperMetadata(
            paper_id="12345",
            title="Test Paper",
            authors=["Smith", "Doe"],
            year=2025,
            abstract="Test abstract",
            source="pubmed",
        )

        assert paper.paper_id == "12345"
        assert paper.title == "Test Paper"
        assert paper.source == "pubmed"
        assert paper.relevance_score == 1.0

    def test_paper_metadata_with_doi(self):
        """Test paper metadata with DOI."""
        paper = PaperMetadata(
            paper_id="arxiv:2501.12345",
            title="arXiv Paper",
            authors=["Johnson"],
            year=2025,
            abstract="Test",
            source="arxiv",
            doi="10.1234/test",
        )

        assert paper.doi == "10.1234/test"
        assert paper.source == "arxiv"


@pytest.mark.asyncio
class TestPubMedClient:
    """Test PubMed API client."""

    async def test_pubmed_client_initialization(self):
        """Test client initialization."""
        client = PubMedClient()

        assert client.name == "pubmed"
        assert client.rate_limit_per_sec == 2.0
        assert client.api_key is None

        await client.close()

    async def test_pubmed_client_with_api_key(self):
        """Test client initialization with API key."""
        client = PubMedClient(api_key="test_key")

        assert client.api_key == "test_key"

        await client.close()

    @pytest.mark.skip(reason="Requires live PubMed API")
    async def test_pubmed_search_live(self):
        """Test actual PubMed search (skipped by default)."""
        client = PubMedClient()

        results = await client.search("CRISPR", limit=5)

        assert len(results) <= 5
        assert all(isinstance(p, PaperMetadata) for p in results)
        assert all(p.source == "pubmed" for p in results)

        await client.close()


@pytest.mark.asyncio
class TestArxivClient:
    """Test arXiv API client."""

    async def test_arxiv_client_initialization(self):
        """Test client initialization."""
        client = ArxivClient()

        assert client.name == "arxiv"
        assert client.rate_limit_per_sec == 1.0

        await client.close()

    @pytest.mark.skip(reason="Requires live arXiv API")
    async def test_arxiv_search_live(self):
        """Test actual arXiv search (skipped by default)."""
        client = ArxivClient()

        results = await client.search("machine learning", limit=5)

        assert len(results) <= 5
        assert all(isinstance(p, PaperMetadata) for p in results)
        assert all(p.source == "arxiv" for p in results)

        await client.close()


@pytest.mark.asyncio
class TestOpenAlexClient:
    """Test OpenAlex API client."""

    async def test_openalex_client_initialization(self):
        """Test client initialization."""
        client = OpenAlexClient()

        assert client.name == "openalex"
        assert client.rate_limit_per_sec == 10.0

        await client.close()

    @pytest.mark.skip(reason="Requires live OpenAlex API")
    async def test_openalex_search_live(self):
        """Test actual OpenAlex search (skipped by default)."""
        client = OpenAlexClient()

        results = await client.search("climate change", limit=5)

        assert len(results) <= 5
        assert all(isinstance(p, PaperMetadata) for p in results)
        assert all(p.source == "openalex" for p in results)

        await client.close()


@pytest.mark.asyncio
class TestAggregatedSearchClient:
    """Test aggregated search client."""

    async def test_aggregated_client_initialization(self):
        """Test client initialization."""
        client = AggregatedSearchClient()

        assert client.pubmed is not None
        assert client.arxiv is not None
        assert client.openalex is not None

        await client.close()

    async def test_aggregated_search_empty_results(self):
        """Test aggregated search with mocked empty results."""
        client = AggregatedSearchClient()

        # Mock individual client searches to return empty
        client.pubmed.search = AsyncMock(return_value=[])
        client.arxiv.search = AsyncMock(return_value=[])
        client.openalex.search = AsyncMock(return_value=[])

        results = await client.search("nonexistent", limit=10)

        assert len(results) == 0

        await client.close()

    async def test_aggregated_search_deduplication(self):
        """Test that aggregated search deduplicates results."""
        client = AggregatedSearchClient()

        # Create duplicate papers
        paper1 = PaperMetadata(
            paper_id="1",
            title="Same Title",
            authors=["Smith"],
            year=2025,
            abstract="Test",
            source="pubmed",
            doi="10.1234/test",
        )

        paper2 = PaperMetadata(
            paper_id="2",
            title="Same Title",
            authors=["Smith"],
            year=2025,
            abstract="Test",
            source="arxiv",
            doi="10.1234/test",
        )

        # Mock searches to return duplicates
        client.pubmed.search = AsyncMock(return_value=[paper1])
        client.arxiv.search = AsyncMock(return_value=[paper2])
        client.openalex.search = AsyncMock(return_value=[])

        results = await client.search("test", limit=10)

        # Should deduplicate based on DOI
        assert len(results) == 1

        await client.close()

    async def test_aggregated_search_source_filtering(self):
        """Test filtering by sources."""
        client = AggregatedSearchClient()

        paper_pubmed = PaperMetadata(
            paper_id="1",
            title="PubMed Paper",
            authors=[],
            year=2025,
            abstract="",
            source="pubmed",
        )

        client.pubmed.search = AsyncMock(return_value=[paper_pubmed])
        client.arxiv.search = AsyncMock(return_value=[])
        client.openalex.search = AsyncMock(return_value=[])

        # Search only PubMed
        results = await client.search("test", limit=10, sources=["pubmed"])

        assert len(results) == 1
        assert results[0].source == "pubmed"

        await client.close()


@pytest.mark.asyncio
class TestLiteratureSearchIntegration:
    """End-to-end literature search tests."""

    async def test_search_with_year_filter(self):
        """Test search with year filtering."""
        client = AggregatedSearchClient()

        # Mock with year-filtered result
        paper = PaperMetadata(
            paper_id="1",
            title="Recent Paper",
            authors=["Smith"],
            year=2025,
            abstract="Test",
            source="pubmed",
        )

        client.pubmed.search = AsyncMock(return_value=[paper])
        client.arxiv.search = AsyncMock(return_value=[])
        client.openalex.search = AsyncMock(return_value=[])

        results = await client.search(
            "test",
            limit=10,
            year_from=2020,
            year_to=2026,
        )

        assert len(results) == 1
        assert results[0].year == 2025

        await client.close()

    async def test_search_limit_enforcement(self):
        """Test that search respects limit."""
        client = AggregatedSearchClient()

        # Create many papers
        papers = [
            PaperMetadata(
                paper_id=str(i),
                title=f"Paper {i}",
                authors=[],
                year=2025,
                abstract="",
                source="pubmed",
            )
            for i in range(20)
        ]

        client.pubmed.search = AsyncMock(return_value=papers)
        client.arxiv.search = AsyncMock(return_value=[])
        client.openalex.search = AsyncMock(return_value=[])

        results = await client.search("test", limit=5)

        # Should respect 3x limit rule
        assert len(results) <= 15

        await client.close()


@pytest.mark.asyncio
class TestRateLimiting:
    """Test rate limiting."""

    async def test_rate_limit_enforcement(self):
        """Test that rate limiting works."""
        import time

        client = PubMedClient()

        # Set aggressive rate limit (0.5 requests/sec = 2 seconds per request)
        client.rate_limit_per_sec = 0.5

        start = time.time()
        await client._rate_limit()
        await client._rate_limit()
        elapsed = time.time() - start

        # Should have ~2 second delay between requests
        assert elapsed >= 2.0

        await client.close()

    async def test_rate_limit_accumulation(self):
        """Test that rate limit accumulates over time."""
        import time

        client = PubMedClient()
        client.rate_limit_per_sec = 2.0  # 2 requests/sec = 0.5s per request

        # First request (immediate)
        start = time.time()
        await client._rate_limit()
        t1 = time.time() - start

        # Second request (should be delayed)
        start = time.time()
        await client._rate_limit()
        t2 = time.time() - start

        # First should be ~0, second should be ~0.5
        assert t1 < 0.2
        assert t2 >= 0.4

        await client.close()
