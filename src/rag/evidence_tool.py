"""
Phase 5: Evidence Graph Agent Tools

Exposes claim extraction and contradiction detection as agent tools:
  - extract_claims: pull candidate claims out of an ingested paper
  - check_contradictions: compare a paper's claims against claims from
    other ingested papers and report agreements/conflicts

Both tools require a database session (papers/chunks/claims must already
be ingested via the Phase 3/4 pipeline), so they're registered separately
from the stateless Phase 2 tools, same pattern as rag_tool.py.
"""

import logging
from typing import Any, Dict, List

from src.core.tools import (
    ToolDefinition,
    ToolType,
    ToolStatus,
    ExtractClaims,
    ExtractClaimsResult,
    CheckContradictions,
    CheckContradictionsResult,
)
from src.rag.database import get_session
from src.rag.models import Paper, Claim, DocumentChunk
from src.rag.evidence_graph import EvidenceGraphBuilder

logger = logging.getLogger(__name__)


async def extract_claims(
    paper_id: str,
    min_confidence: float = 0.5,
) -> Dict[str, Any]:
    """
    Extract candidate claims from an ingested paper's abstract/chunks.

    Args:
        paper_id: ID of the paper (must exist in the database)
        min_confidence: Minimum heuristic confidence to keep a claim

    Returns:
        ExtractClaimsResult dict
    """
    logger.info(f"Extracting claims for paper: {paper_id}")

    session = get_session()
    try:
        paper = session.query(Paper).filter(Paper.id == paper_id).first()
        if paper is None:
            return {"paper_id": paper_id, "claims": []}

        builder = EvidenceGraphBuilder(session)

        # Prefer extracting from stored chunks (more granular); fall back to abstract.
        chunks = session.query(DocumentChunk).filter(DocumentChunk.paper_id == paper_id).all()

        all_claims = []
        if chunks:
            for chunk in chunks:
                claims = builder.extract_and_store_claims(
                    paper_id=paper_id,
                    text=chunk.content,
                    source_chunk_id=chunk.id,
                    min_confidence=min_confidence,
                )
                all_claims.extend(claims)
        else:
            claims = builder.extract_and_store_claims(
                paper_id=paper_id,
                text=paper.abstract or "",
                min_confidence=min_confidence,
            )
            all_claims.extend(claims)

        session.commit()

        return {
            "paper_id": paper_id,
            "claims": [
                {
                    "claim_id": c.id,
                    "claim_text": c.claim_text,
                    "claim_type": c.claim_type,
                    "confidence": 0.0,  # heuristic confidence not stored on Claim; see extraction log
                }
                for c in all_claims
            ],
        }
    finally:
        session.close()


async def check_contradictions(
    paper_id: str,
    compare_against_paper_ids: List[str] = None,
) -> Dict[str, Any]:
    """
    Compare a paper's claims against claims from other papers to detect
    supports/contradictions.

    Args:
        paper_id: Paper whose claims to check
        compare_against_paper_ids: Specific papers to compare against
            (empty/None = compare against all other papers with claims)

    Returns:
        CheckContradictionsResult dict
    """
    logger.info(f"Checking contradictions for paper: {paper_id}")

    session = get_session()
    try:
        builder = EvidenceGraphBuilder(session)

        source_claims = session.query(Claim).filter(Claim.paper_id == paper_id).all()
        if not source_claims:
            return {
                "paper_id": paper_id,
                "relations": [],
                "contradiction_count": 0,
                "support_count": 0,
            }

        other_query = session.query(Claim).filter(Claim.paper_id != paper_id)
        if compare_against_paper_ids:
            other_query = other_query.filter(Claim.paper_id.in_(compare_against_paper_ids))
        other_claims = other_query.all()

        if not other_claims:
            return {
                "paper_id": paper_id,
                "relations": [],
                "contradiction_count": 0,
                "support_count": 0,
            }

        relation_outputs = []
        contradiction_count = 0
        support_count = 0

        claims_by_id = {c.id: c for c in source_claims + other_claims}

        for claim in source_claims:
            relations = builder.build_relations_for_claim(claim, other_claims)
            for relation in relations:
                claim_a = claims_by_id.get(relation.claim_id_a)
                claim_b = claims_by_id.get(relation.claim_id_b)

                relation_outputs.append(
                    {
                        "claim_id_a": relation.claim_id_a,
                        "claim_text_a": claim_a.claim_text if claim_a else "",
                        "claim_id_b": relation.claim_id_b,
                        "claim_text_b": claim_b.claim_text if claim_b else "",
                        "relation_type": relation.relation_type,
                        "similarity_score": relation.similarity_score,
                        "confidence": relation.confidence,
                        "explanation": relation.explanation,
                    }
                )

                if relation.relation_type == "contradicts":
                    contradiction_count += 1
                elif relation.relation_type == "supports":
                    support_count += 1

        session.commit()

        return {
            "paper_id": paper_id,
            "relations": relation_outputs,
            "contradiction_count": contradiction_count,
            "support_count": support_count,
        }
    finally:
        session.close()


EXTRACT_CLAIMS_TOOL = ToolDefinition(
    name="extract_claims",
    type=ToolType.EXTRACT,
    description=(
        "Extract candidate scientific claims (findings, hypotheses, limitations) from an "
        "already-ingested paper's text. Use this AFTER search_literature/retrieve_context "
        "has ingested a paper, before checking for contradictions."
    ),
    input_schema=ExtractClaims,
    output_schema=ExtractClaimsResult,
    execution_fn=extract_claims,
    status=ToolStatus.EXPERIMENTAL,  # heuristic extraction, improves with LLM in later phases
    tags=["evidence", "claims", "extraction"],
)

CHECK_CONTRADICTIONS_TOOL = ToolDefinition(
    name="check_contradictions",
    type=ToolType.VALIDATE,
    description=(
        "Compare a paper's extracted claims against claims from other ingested papers to "
        "detect agreements (supports) and conflicts (contradicts). Use this to surface "
        "disagreements in the literature before synthesizing an answer."
    ),
    input_schema=CheckContradictions,
    output_schema=CheckContradictionsResult,
    execution_fn=check_contradictions,
    status=ToolStatus.EXPERIMENTAL,
    tags=["evidence", "contradiction-detection", "validation"],
)


def register_evidence_tools(registry) -> None:
    """Register Phase 5 evidence-graph tools to a registry."""
    registry.register(EXTRACT_CLAIMS_TOOL)
    registry.register(CHECK_CONTRADICTIONS_TOOL)
    logger.info("Registered evidence graph tools (extract_claims, check_contradictions)")
