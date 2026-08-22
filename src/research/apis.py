"""
Phase 3: Literature Search API Clients

Clients for multiple scientific literature sources:
  - PubMed (biomedical)
  - arXiv (preprints)
  - OpenAlex (comprehensive)

Each client handles:
  - API authentication
  - Request formatting
  - Response parsing
  - Error handling
  - Rate limiting
  - Result normalization
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


@dataclass
class PaperMetadata:
    """Normalized paper metadata from any source."""
    paper_id: str              # Unique ID (doi, arxiv_id, openalex_id)
    title: str
    authors: List[str]
    year: int
    abstract: str
    source: str                # "pubmed", "arxiv", "openalex"
    url: Optional[str] = None
    doi: Optional[str] = None
    journal: Optional[str] = None
    publish_date: Optional[str] = None
    relevance_score: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LiteratureClient(ABC):
    """Base class for literature API clients."""

    def __init__(
        self,
        name: str,
        api_key: Optional[str] = None,
        rate_limit_per_sec: float = 1.0,
        timeout: int = 30,
    ):
        """
        Initialize literature client.

        Args:
            name: Client name (pubmed, arxiv, openalex)
            api_key: API key if required
            rate_limit_per_sec: Max requests per second
            timeout: HTTP request timeout in seconds
        """
        self.name = name
        self.api_key = api_key
        self.rate_limit_per_sec = rate_limit_per_sec
        self.timeout = timeout
        self.last_request_time = 0.0
        self.client = httpx.AsyncClient(timeout=timeout)

        logger.info(f"Initialized {name} client (rate limit: {rate_limit_per_sec} req/s)")

    async def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        min_interval = 1.0 / self.rate_limit_per_sec
        elapsed = time.time() - self.last_request_time

        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)

        self.last_request_time = time.time()

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[PaperMetadata]:
        """
        Search literature.

        Args:
            query: Search query
            limit: Max results
            year_from: Filter by year range
            year_to: Filter by year range

        Returns:
            List of PaperMetadata objects
        """
        pass

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


class PubMedClient(LiteratureClient):
    """PubMed/MEDLINE literature client."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize PubMed client."""
        super().__init__(
            name="pubmed",
            api_key=api_key,
            rate_limit_per_sec=2.0,  # 2 requests/sec
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[PaperMetadata]:
        """
        Search PubMed.

        Args:
            query: Search query
            limit: Max results
            year_from: Filter by year range
            year_to: Filter by year range

        Returns:
            List of PubMed papers as PaperMetadata
        """
        await self._rate_limit()

        try:
            # Build query with year filters
            search_query = query
            if year_from:
                search_query += f' AND {year_from}[PDAT]'
            if year_to:
                search_query += f':{year_to}[PDAT]'

            logger.info(f"PubMed search: {search_query}")

            # Search (get UIDs)
            search_params = {
                "db": "pubmed",
                "term": search_query,
                "retmax": min(limit, 100),
                "rettype": "json",
            }
            if self.api_key:
                search_params["api_key"] = self.api_key

            response = await self.client.get(f"{self.BASE_URL}/esearch.fcgi", params=search_params)
            response.raise_for_status()

            search_result = response.json()
            uids = search_result.get("esearchresult", {}).get("idlist", [])

            if not uids:
                logger.info("No PubMed results")
                return []

            logger.info(f"Found {len(uids)} PubMed UIDs, fetching details...")

            # Fetch full records
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(uids[:limit]),
                "rettype": "json",
            }
            if self.api_key:
                fetch_params["api_key"] = self.api_key

            await self._rate_limit()
            response = await self.client.get(f"{self.BASE_URL}/efetch.fcgi", params=fetch_params)
            response.raise_for_status()

            fetch_result = response.json()
            articles = fetch_result.get("result", {}).get("uids", [])

            papers = []
            for uid in articles[:limit]:
                article_data = fetch_result["result"].get(uid, {})

                # Extract metadata
                title = article_data.get("title", "")
                authors = [
                    f"{a.get('name', '')}"
                    for a in article_data.get("authors", [])
                ][:10]

                # Parse year from publication date
                pub_date = article_data.get("pubdate", "")
                year = int(pub_date.split()[0]) if pub_date and pub_date[0].isdigit() else datetime.now().year

                abstract = article_data.get("abstract", "")[:1000]

                paper = PaperMetadata(
                    paper_id=uid,
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    source="pubmed",
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                    doi=article_data.get("doi", ""),
                    journal=article_data.get("source", ""),
                    publish_date=pub_date,
                )
                papers.append(paper)

            logger.info(f"Retrieved {len(papers)} papers from PubMed")
            return papers

        except Exception as e:
            logger.error(f"PubMed search error: {e}")
            return []


class ArxivClient(LiteratureClient):
    """arXiv preprint client."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self):
        """Initialize arXiv client."""
        super().__init__(
            name="arxiv",
            rate_limit_per_sec=1.0,  # arXiv requests 1 per 3 seconds, being conservative
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[PaperMetadata]:
        """
        Search arXiv.

        Args:
            query: Search query
            limit: Max results
            year_from: Filter by year range
            year_to: Filter by year range

        Returns:
            List of arXiv papers as PaperMetadata
        """
        await self._rate_limit()

        try:
            # Build arXiv query
            search_query = f"all:{query}"
            if year_from:
                search_query += f" AND submittedDate:[{year_from}010100000000 TO 99991231235959]"

            logger.info(f"arXiv search: {search_query}")

            params = {
                "search_query": search_query,
                "max_results": min(limit, 100),
                "sortBy": "relevance",
                "sortOrder": "descending",
                "start": 0,
            }

            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            # Parse Atom XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            papers = []
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            for entry in root.findall("atom:entry", ns)[:limit]:
                arxiv_id = entry.findtext("atom:id", "", ns).split("/abs/")[-1]
                title = entry.findtext("atom:title", "", ns).replace("\n", " ").strip()
                authors = [
                    author.findtext("atom:name", "", ns)
                    for author in entry.findall("atom:author", ns)
                ][:10]

                # Parse publication date
                published = entry.findtext("atom:published", "", ns)
                year = int(published[:4]) if published else datetime.now().year

                summary = entry.findtext("atom:summary", "", ns).replace("\n", " ").strip()[:1000]

                paper = PaperMetadata(
                    paper_id=arxiv_id,
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=summary,
                    source="arxiv",
                    url=f"https://arxiv.org/abs/{arxiv_id}",
                    doi="",
                    publish_date=published,
                )
                papers.append(paper)

            logger.info(f"Retrieved {len(papers)} papers from arXiv")
            return papers

        except Exception as e:
            logger.error(f"arXiv search error: {e}")
            return []


class OpenAlexClient(LiteratureClient):
    """OpenAlex comprehensive literature client."""

    BASE_URL = "https://api.openalex.org/works"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAlex client."""
        super().__init__(
            name="openalex",
            api_key=api_key,
            rate_limit_per_sec=10.0,  # OpenAlex is generous
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
    ) -> List[PaperMetadata]:
        """
        Search OpenAlex.

        Args:
            query: Search query
            limit: Max results
            year_from: Filter by year range
            year_to: Filter by year range

        Returns:
            List of OpenAlex papers as PaperMetadata
        """
        await self._rate_limit()

        try:
            logger.info(f"OpenAlex search: {query}")

            # Build filters
            filters = [f'title.search:"{query}"']
            if year_from:
                filters.append(f"publication_year:>={year_from}")
            if year_to:
                filters.append(f"publication_year:<={year_to}")

            params = {
                "filter": ",".join(filters),
                "limit": min(limit, 50),
                "sort": "cited_by_count:desc",
            }

            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            result = response.json()
            works = result.get("results", [])

            papers = []
            for work in works[:limit]:
                # Extract metadata
                openalex_id = work.get("id", "").split("/")[-1]
                title = work.get("title", "")
                authors = [
                    a["author"].get("display_name", "")
                    for a in work.get("authorships", [])
                ][:10]

                year = work.get("publication_year", datetime.now().year)
                abstract = work.get("abstract", "")[:1000] if work.get("abstract") else ""

                # Get DOI
                doi = ""
                ids = work.get("ids", {})
                if "doi" in ids:
                    doi = ids["doi"].replace("https://doi.org/", "")

                paper = PaperMetadata(
                    paper_id=openalex_id,
                    title=title,
                    authors=authors,
                    year=year,
                    abstract=abstract,
                    source="openalex",
                    url=work.get("landing_page_url", ""),
                    doi=doi,
                    journal=work.get("primary_location", {}).get("source", {}).get("display_name", ""),
                    publish_date=work.get("publication_date", ""),
                )
                papers.append(paper)

            logger.info(f"Retrieved {len(papers)} papers from OpenAlex")
            return papers

        except Exception as e:
            logger.error(f"OpenAlex search error: {e}")
            return []


class AggregatedSearchClient:
    """
    Aggregate searches across multiple literature sources.

    Searches PubMed, arXiv, and OpenAlex in parallel.
    Returns deduplicated, ranked results.
    """

    def __init__(
        self,
        pubmed_key: Optional[str] = None,
        openalex_key: Optional[str] = None,
    ):
        """Initialize aggregated client."""
        self.pubmed = PubMedClient(api_key=pubmed_key)
        self.arxiv = ArxivClient()
        self.openalex = OpenAlexClient(api_key=openalex_key)

        logger.info("Initialized AggregatedSearchClient with PubMed, arXiv, OpenAlex")

    async def search(
        self,
        query: str,
        limit: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        sources: Optional[List[str]] = None,
    ) -> List[PaperMetadata]:
        """
        Search all configured sources in parallel.

        Args:
            query: Search query
            limit: Max results per source
            year_from: Filter by year range
            year_to: Filter by year range
            sources: Which sources to search ("pubmed", "arxiv", "openalex")
                     Default: all

        Returns:
            Deduplicated, ranked list of papers
        """
        if sources is None:
            sources = ["pubmed", "arxiv", "openalex"]

        logger.info(f"Aggregated search: query='{query}', sources={sources}")

        tasks = []
        if "pubmed" in sources:
            tasks.append(self.pubmed.search(query, limit, year_from, year_to))
        if "arxiv" in sources:
            tasks.append(self.arxiv.search(query, limit, year_from, year_to))
        if "openalex" in sources:
            tasks.append(self.openalex.search(query, limit, year_from, year_to))

        # Execute searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect all papers
        all_papers = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Search failed: {result}")
                continue
            all_papers.extend(result)

        # Deduplicate by DOI and title
        seen = set()
        unique_papers = []

        for paper in all_papers:
            key = (paper.doi.lower() if paper.doi else "", paper.title.lower())
            if key not in seen:
                seen.add(key)
                unique_papers.append(paper)

        # Limit and return
        logger.info(f"Aggregated search returned {len(unique_papers)} unique papers")
        return unique_papers[:limit * 3]  # Return up to 3x limit (user can filter)

    async def close(self):
        """Close all clients."""
        await asyncio.gather(
            self.pubmed.close(),
            self.arxiv.close(),
            self.openalex.close(),
        )
