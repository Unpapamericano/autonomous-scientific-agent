"""
Phase 3: Updated Tool Implementations with Real API Integration

This module updates Phase 2 tools with Phase 3 real API capabilities.
Integrates with PubMed, arXiv, and OpenAlex via apis.py.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional

from src.core.tools import (
    SearchQuery,
    SearchResult,
)
from src.research.apis import AggregatedSearchClient

logger = logging.getLogger(__name__)


async def search_literature_phase3(
    input_data: SearchQuery,
    _registry: "ToolRegistry" = None,
) -> SearchResult:
    """
    Search scientific literature with real APIs (Phase 3).

    Searches PubMed, arXiv, and OpenAlex in parallel.
    
    Args:
        input_data: SearchQuery with query, limit, filters
        _registry: Tool registry (unused)
        
    Returns:
        SearchResult with papers from multiple sources
    """
    start_time = time.time()
    logger.info(f"Searching literature (Phase 3): {input_data.query}")

    try:
        # Initialize aggregated client
        client = AggregatedSearchClient()

        # Determine which sources to search
        sources = input_data.source if isinstance(input_data.source, list) else [input_data.source]
        if "all" in sources or len(sources) == 0 or input_data.source == "all":
            sources = ["pubmed", "arxiv", "openalex"]

        logger.info(f"Searching sources: {sources}")

        # Execute aggregated search
        papers_metadata = await client.search(
            query=input_data.query,
            limit=input_data.limit,
            year_from=input_data.year_from,
            year_to=input_data.year_to,
            sources=sources,
        )

        logger.info(f"Retrieved {len(papers_metadata)} papers")

        # Convert to SearchResult format
        papers = [
            {
                "paper_id": p.paper_id,
                "title": p.title,
                "authors": p.authors,
                "year": p.year,
                "abstract": p.abstract,
                "source": p.source,
                "url": p.url,
                "doi": p.doi,
                "journal": p.journal,
                "relevance_score": p.relevance_score,
            }
            for p in papers_metadata[: input_data.limit]
        ]

        elapsed_ms = (time.time() - start_time) * 1000

        logger.info(f"Literature search complete: {len(papers)} papers in {elapsed_ms:.0f}ms")

        await client.close()

        return SearchResult(
            papers=papers,
            total_count=len(papers),
            query=input_data.query,
            search_time_ms=elapsed_ms,
            source_breakdown={
                "pubmed": sum(1 for p in papers if p["source"] == "pubmed"),
                "arxiv": sum(1 for p in papers if p["source"] == "arxiv"),
                "openalex": sum(1 for p in papers if p["source"] == "openalex"),
            },
        )

    except Exception as e:
        logger.error(f"Literature search error: {e}", exc_info=True)

        # Fallback to empty results on error
        elapsed_ms = (time.time() - start_time) * 1000
        return SearchResult(
            papers=[],
            total_count=0,
            query=input_data.query,
            search_time_ms=elapsed_ms,
            error=str(e),
        )
