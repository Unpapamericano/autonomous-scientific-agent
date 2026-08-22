"""
Database Repositories

Data access layer for papers, searches, and other entities.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.rag.models import (
    Paper,
    DocumentChunk,
    Search,
    SearchResult,
    ResearchSession,
    ToolExecution,
)
from src.research.apis import PaperMetadata

logger = logging.getLogger(__name__)


class PaperRepository:
    """Access layer for papers."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, metadata: PaperMetadata) -> Paper:
        """Create paper from metadata."""
        paper = Paper(
            id=metadata.paper_id,
            title=metadata.title,
            authors=metadata.authors,
            year=metadata.year,
            abstract=metadata.abstract,
            source=metadata.source,
            url=metadata.url,
            doi=metadata.doi,
            journal=metadata.journal,
            publish_date=metadata.publish_date,
            extra_metadata=metadata.metadata,
        )
        self.session.add(paper)
        self.session.flush()
        logger.info(f"Created paper: {paper.id}")
        return paper

    def get(self, paper_id: str) -> Optional[Paper]:
        """Get paper by ID."""
        return self.session.query(Paper).filter(Paper.id == paper_id).first()

    def get_by_doi(self, doi: str) -> Optional[Paper]:
        """Get paper by DOI."""
        return self.session.query(Paper).filter(Paper.doi == doi).first()

    def list_by_source(self, source: str, limit: int = 100) -> List[Paper]:
        """List papers by source."""
        return (
            self.session.query(Paper)
            .filter(Paper.source == source)
            .order_by(Paper.retrieved_at.desc())
            .limit(limit)
            .all()
        )

    def list_by_year(self, year_from: int, year_to: int) -> List[Paper]:
        """List papers by year range."""
        return (
            self.session.query(Paper)
            .filter(Paper.year >= year_from, Paper.year <= year_to)
            .order_by(Paper.year.desc())
            .all()
        )

    def search_by_title(self, title_query: str) -> List[Paper]:
        """Search papers by title."""
        return (
            self.session.query(Paper)
            .filter(Paper.title.ilike(f"%{title_query}%"))
            .all()
        )

    def count_by_source(self) -> Dict[str, int]:
        """Count papers by source."""
        counts = (
            self.session.query(Paper.source, func.count(Paper.id))
            .group_by(Paper.source)
            .all()
        )
        return {source: count for source, count in counts}


class SearchRepository:
    """Access layer for searches."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        query: str,
        sources: List[str],
        limit: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        session_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ) -> Search:
        """Create search record."""
        search = Search(
            id=str(uuid.uuid4()),
            query=query,
            sources=sources,
            limit=limit,
            year_from=year_from,
            year_to=year_to,
            session_id=session_id,
            duration_ms=duration_ms,
            result_count=0,
        )
        self.session.add(search)
        self.session.flush()
        logger.info(f"Created search: {search.id}")
        return search

    def get(self, search_id: str) -> Optional[Search]:
        """Get search by ID."""
        return self.session.query(Search).filter(Search.id == search_id).first()

    def list_by_session(self, session_id: str) -> List[Search]:
        """List searches in a session."""
        return (
            self.session.query(Search)
            .filter(Search.session_id == session_id)
            .order_by(Search.created_at.desc())
            .all()
        )

    def add_result(
        self,
        search_id: str,
        paper_id: str,
        rank: int,
        relevance_score: Optional[float] = None,
    ) -> SearchResult:
        """Add paper to search results."""
        result = SearchResult(
            id=str(uuid.uuid4()),
            search_id=search_id,
            paper_id=paper_id,
            rank=rank,
            relevance_score=relevance_score,
        )
        self.session.add(result)

        # Update search result count
        search = self.session.query(Search).filter(Search.id == search_id).first()
        if search:
            search.result_count += 1

        return result

    def get_results(self, search_id: str) -> List[SearchResult]:
        """Get all results for a search."""
        return (
            self.session.query(SearchResult)
            .filter(SearchResult.search_id == search_id)
            .order_by(SearchResult.rank)
            .all()
        )


class ResearchSessionRepository:
    """Access layer for research sessions."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        topic: Optional[str] = None,
        initial_question: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> ResearchSession:
        """Create research session."""
        session_obj = ResearchSession(
            id=str(uuid.uuid4()),
            topic=topic,
            initial_question=initial_question,
            user_id=user_id,
        )
        self.session.add(session_obj)
        self.session.flush()
        logger.info(f"Created research session: {session_obj.id}")
        return session_obj

    def get(self, session_id: str) -> Optional[ResearchSession]:
        """Get session by ID."""
        return (
            self.session.query(ResearchSession)
            .filter(ResearchSession.id == session_id)
            .first()
        )

    def list_active(self, limit: int = 50) -> List[ResearchSession]:
        """List active (uncompleted) sessions."""
        return (
            self.session.query(ResearchSession)
            .filter(ResearchSession.completed == False)
            .order_by(ResearchSession.created_at.desc())
            .limit(limit)
            .all()
        )

    def complete(self, session_id: str):
        """Mark session as completed."""
        session_obj = self.get(session_id)
        if session_obj:
            session_obj.completed = True
            session_obj.updated_at = datetime.utcnow()
            logger.info(f"Completed session: {session_id}")

    def update_state(self, session_id: str, state_json: Dict[str, Any]):
        """Update session state JSON."""
        session_obj = self.get(session_id)
        if session_obj:
            session_obj.state_json = state_json
            session_obj.updated_at = datetime.utcnow()


class ToolExecutionRepository:
    """Access layer for tool executions."""

    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> ToolExecution:
        """Create tool execution record."""
        execution = ToolExecution(
            id=str(uuid.uuid4()),
            session_id=session_id,
            tool_name=tool_name,
            tool_input=tool_input,
            success=False,
        )
        self.session.add(execution)
        self.session.flush()
        return execution

    def complete(
        self,
        execution_id: str,
        success: bool,
        tool_output: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ):
        """Mark tool execution as complete."""
        execution = (
            self.session.query(ToolExecution)
            .filter(ToolExecution.id == execution_id)
            .first()
        )
        if execution:
            execution.success = success
            execution.tool_output = tool_output
            execution.error_message = error_message
            execution.duration_ms = duration_ms

    def get_session_executions(self, session_id: str) -> List[ToolExecution]:
        """Get all executions in a session."""
        return (
            self.session.query(ToolExecution)
            .filter(ToolExecution.session_id == session_id)
            .order_by(ToolExecution.created_at)
            .all()
        )

    def get_tool_stats(self, tool_name: str) -> Dict[str, Any]:
        """Get statistics for a tool."""
        executions = self.session.query(ToolExecution).filter(
            ToolExecution.tool_name == tool_name
        )

        total = executions.count()
        successful = executions.filter(ToolExecution.success == True).count()
        avg_duration = self.session.query(
            func.avg(ToolExecution.duration_ms)
        ).filter(ToolExecution.tool_name == tool_name).scalar()

        return {
            "tool_name": tool_name,
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "avg_duration_ms": avg_duration or 0,
        }
