"""
Phase 5: Evidence Graph & Contradiction Detection

Builds a graph connecting:
  - Claim -> DocumentChunk  (Evidence: does this chunk support/contradict the claim?)
  - Claim -> Claim          (ClaimRelation: do these two claims agree or conflict?)

Contradiction detection strategy (heuristic, no GPU required):
  1. Compute embedding similarity between claim texts to find claims that are
     TOPICALLY related (same subject matter) - this uses Phase 4's embedder.
  2. Among topically related claims, look for polarity signals (negation,
     opposite-direction word pairs like increase/decrease, effective/
     ineffective) to decide "supports" vs "contradicts" vs "neutral".

This is intentionally conservative and explainable: every relation stores
its similarity_score, confidence, and a human-readable explanation, and is
meant to be reviewed rather than trusted blindly (RQ4 in RESEARCH.md).
"""

import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from src.rag.embeddings import get_embedding_generator, EmbeddingGenerator
from src.rag.models import Claim, Evidence, ClaimRelation, DocumentChunk
from src.rag.claim_extraction import extract_claims_heuristic

logger = logging.getLogger(__name__)


# Opposite-direction word pairs used to flag polarity conflicts between
# topically-similar claims.
OPPOSITE_PAIRS = [
    ("increase", "decrease"),
    ("increased", "decreased"),
    ("improve", "worsen"),
    ("improved", "worsened"),
    ("effective", "ineffective"),
    ("efficacious", "inefficacious"),
    ("success", "failure"),
    ("successful", "unsuccessful"),
    ("safe", "unsafe"),
    ("significant", "insignificant"),
    ("positive", "negative"),
    ("higher", "lower"),
    ("supports", "refutes"),
    ("confirmed", "disproved"),
]

NEGATION_CUES = ["not ", "no ", "did not", "failed to", "did not show", "no evidence", "n't "]

TOPICAL_SIMILARITY_THRESHOLD = 0.55  # claims must be at least this similar to be "about the same thing"
CONTRADICTION_CONFIDENCE_BASE = 0.6
SUPPORT_CONFIDENCE_BASE = 0.55


@dataclass
class ContradictionResult:
    """Result of comparing two claims for agreement/conflict."""
    claim_a_id: str
    claim_b_id: str
    relation_type: str  # "supports", "contradicts", "neutral"
    similarity_score: float
    confidence: float
    explanation: str


def _has_polarity_conflict(text_a: str, text_b: str) -> bool:
    """Check whether two claim texts contain opposite-direction language."""
    a_lower = text_a.lower()
    b_lower = text_b.lower()

    for word_a, word_b in OPPOSITE_PAIRS:
        if (word_a in a_lower and word_b in b_lower) or (word_b in a_lower and word_a in b_lower):
            return True

    a_negated = any(cue in a_lower for cue in NEGATION_CUES)
    b_negated = any(cue in b_lower for cue in NEGATION_CUES)
    if a_negated != b_negated:
        return True

    return False


def compare_claims(
    claim_a_text: str,
    claim_b_text: str,
    embedder: Optional[EmbeddingGenerator] = None,
) -> Tuple[str, float, float, str]:
    """
    Compare two claim texts and classify their relationship.

    Args:
        claim_a_text: First claim
        claim_b_text: Second claim
        embedder: EmbeddingGenerator (created if not provided)

    Returns:
        (relation_type, similarity_score, confidence, explanation)
    """
    embedder = embedder or get_embedding_generator()

    emb_a = embedder.embed_text(claim_a_text)
    emb_b = embedder.embed_text(claim_b_text)
    similarity = embedder.similarity(emb_a, emb_b)

    if similarity < TOPICAL_SIMILARITY_THRESHOLD:
        return (
            "neutral",
            similarity,
            0.9,
            f"Claims are not topically related (similarity={similarity:.2f}).",
        )

    if _has_polarity_conflict(claim_a_text, claim_b_text):
        confidence = min(0.95, CONTRADICTION_CONFIDENCE_BASE + similarity * 0.3)
        return (
            "contradicts",
            similarity,
            confidence,
            f"Claims are topically similar (similarity={similarity:.2f}) but contain "
            "opposite-direction language, suggesting a contradiction.",
        )

    confidence = min(0.9, SUPPORT_CONFIDENCE_BASE + similarity * 0.3)
    return (
        "supports",
        similarity,
        confidence,
        f"Claims are topically similar (similarity={similarity:.2f}) with consistent "
        "language, suggesting mutual support.",
    )


class EvidenceGraphBuilder:
    """
    Builds and queries the evidence graph: Claim <-> DocumentChunk and
    Claim <-> Claim relationships.
    """

    def __init__(self, session: Session, embedder: Optional[EmbeddingGenerator] = None):
        self.session = session
        self.embedder = embedder or get_embedding_generator()

    def extract_and_store_claims(
        self,
        paper_id: str,
        text: str,
        source_chunk_id: Optional[str] = None,
        min_confidence: float = 0.5,
    ) -> List[Claim]:
        """
        Extract candidate claims from text and store them (with embeddings).

        Args:
            paper_id: Paper the claims belong to
            text: Source text to extract from (abstract or chunk content)
            source_chunk_id: Optional chunk this text came from
            min_confidence: Minimum heuristic confidence to store

        Returns:
            List of stored Claim ORM objects
        """
        extracted = extract_claims_heuristic(text, source_chunk_id=source_chunk_id, min_confidence=min_confidence)
        if not extracted:
            return []

        embeddings = self.embedder.embed_batch([c.claim_text for c in extracted])

        claims = []
        for candidate, embedding in zip(extracted, embeddings):
            claim = Claim(
                id=str(uuid.uuid4()),
                paper_id=paper_id,
                source_chunk_id=candidate.source_chunk_id,
                claim_text=candidate.claim_text,
                claim_type=candidate.claim_type,
                claim_embedding=embedding,
                embedding_model=self.embedder.model_name,
            )
            self.session.add(claim)
            claims.append(claim)

        logger.info(f"Stored {len(claims)} claims for paper {paper_id}")
        return claims

    def link_claim_to_chunk(
        self,
        claim: Claim,
        chunk: DocumentChunk,
        min_similarity: float = 0.5,
    ) -> Optional[Evidence]:
        """
        Create an Evidence link between a claim and a chunk if they are
        semantically related enough to count as supporting evidence.

        Args:
            claim: Claim ORM object (must have claim_embedding set)
            chunk: DocumentChunk ORM object (must have embedding set)
            min_similarity: Minimum similarity to create a link

        Returns:
            Evidence object if created, else None
        """
        if not claim.claim_embedding or not chunk.embedding:
            logger.warning("Cannot link claim to chunk without embeddings")
            return None

        similarity = self.embedder.similarity(claim.claim_embedding, chunk.embedding)
        if similarity < min_similarity:
            return None

        evidence = Evidence(
            id=str(uuid.uuid4()),
            claim_id=claim.id,
            chunk_id=chunk.id,
            evidence_type="direct" if similarity >= 0.75 else "indirect",
            confidence=similarity,
            explanation=f"Chunk semantically supports claim (similarity={similarity:.2f}).",
        )
        self.session.add(evidence)
        return evidence

    def find_related_claims(
        self,
        claim: Claim,
        candidates: List[Claim],
        top_k: int = 5,
    ) -> List[Claim]:
        """Rank candidate claims by embedding similarity to the given claim."""
        if not candidates:
            return []

        candidate_embeddings = [c.claim_embedding for c in candidates if c.claim_embedding]
        if not candidate_embeddings:
            return []

        ranked_indices = self.embedder.rank_by_similarity(
            claim.claim_embedding, candidate_embeddings, top_k=top_k
        )
        return [candidates[i] for i in ranked_indices]

    def detect_contradiction(self, claim_a: Claim, claim_b: Claim) -> ContradictionResult:
        """Compare two stored claims and classify their relationship."""
        relation_type, similarity, confidence, explanation = compare_claims(
            claim_a.claim_text, claim_b.claim_text, embedder=self.embedder
        )
        return ContradictionResult(
            claim_a_id=claim_a.id,
            claim_b_id=claim_b.id,
            relation_type=relation_type,
            similarity_score=similarity,
            confidence=confidence,
            explanation=explanation,
        )

    def store_relation(self, result: ContradictionResult) -> ClaimRelation:
        """Persist a ContradictionResult as a ClaimRelation row."""
        relation = ClaimRelation(
            id=str(uuid.uuid4()),
            claim_id_a=result.claim_a_id,
            claim_id_b=result.claim_b_id,
            relation_type=result.relation_type,
            similarity_score=result.similarity_score,
            confidence=result.confidence,
            explanation=result.explanation,
        )
        self.session.add(relation)
        return relation

    def build_relations_for_claim(
        self,
        claim: Claim,
        other_claims: List[Claim],
        store_neutral: bool = False,
    ) -> List[ClaimRelation]:
        """
        Compare a claim against a set of other claims (e.g. from other papers)
        and store any non-neutral (or all, if store_neutral=True) relations.

        Args:
            claim: The claim to compare
            other_claims: Claims to compare against (typically from other papers)
            store_neutral: Whether to persist "neutral" relations too

        Returns:
            List of created ClaimRelation objects
        """
        relations = []
        for other in other_claims:
            if other.id == claim.id:
                continue

            result = self.detect_contradiction(claim, other)
            if result.relation_type == "neutral" and not store_neutral:
                continue

            relation = self.store_relation(result)
            relations.append(relation)

        logger.info(f"Built {len(relations)} relations for claim {claim.id}")
        return relations

    def get_contradictions_for_paper(self, paper_id: str) -> List[ClaimRelation]:
        """Get all 'contradicts' relations involving claims from a given paper."""
        claim_ids = [
            c.id for c in self.session.query(Claim).filter(Claim.paper_id == paper_id).all()
        ]
        if not claim_ids:
            return []

        return (
            self.session.query(ClaimRelation)
            .filter(
                ClaimRelation.relation_type == "contradicts",
                (ClaimRelation.claim_id_a.in_(claim_ids)) | (ClaimRelation.claim_id_b.in_(claim_ids)),
            )
            .all()
        )
