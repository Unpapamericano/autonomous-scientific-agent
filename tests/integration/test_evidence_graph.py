"""
Phase 5: Integration Tests for Claim Extraction & Evidence Graph

Tests use heuristic extraction (no LLM required) and mocked embedders
(no GPU/model download required) so they run fast and offline.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from src.rag.claim_extraction import (
    extract_claims_heuristic,
    _split_sentences,
    _classify_sentence,
    ExtractedClaim,
)
from src.rag.evidence_graph import (
    compare_claims,
    _has_polarity_conflict,
    EvidenceGraphBuilder,
    ContradictionResult,
)
from src.rag.embeddings import EMBEDDING_DIM


# ============================================================================
# CLAIM EXTRACTION TESTS
# ============================================================================

class TestSentenceSplitting:
    """Test sentence splitting utility."""

    def test_split_simple_sentences(self):
        text = "CRISPR is a gene editing tool. It was discovered in bacteria."
        sentences = _split_sentences(text)
        assert len(sentences) == 2

    def test_split_empty_text(self):
        assert _split_sentences("") == []
        assert _split_sentences(None) == []

    def test_split_handles_et_al(self):
        text = "Smith et al. showed CRISPR efficacy. The results were significant."
        sentences = _split_sentences(text)
        # "et al." should not cause an incorrect split
        assert len(sentences) == 2
        assert "et al" in sentences[0].lower()


class TestClassifySentence:
    """Test sentence classification heuristics."""

    def test_classify_finding(self):
        sentence = "We found that CRISPR significantly increased success rates in patients."
        result = _classify_sentence(sentence)
        assert result is not None
        claim_type, confidence = result
        assert claim_type == "finding"
        assert confidence > 0.5

    def test_classify_hypothesis(self):
        sentence = "We hypothesize that this mechanism may lead to improved outcomes."
        result = _classify_sentence(sentence)
        assert result is not None
        claim_type, _ = result
        assert claim_type == "hypothesis"

    def test_classify_limitation(self):
        sentence = "This study has a limitation due to small sample size in the cohort."
        result = _classify_sentence(sentence)
        assert result is not None
        claim_type, _ = result
        assert claim_type == "limitation"

    def test_classify_non_claim_too_short(self):
        assert _classify_sentence("CRISPR is great.") is None

    def test_classify_non_claim_citation(self):
        sentence = "As shown by Smith et al. the treatment increased survival significantly."
        assert _classify_sentence(sentence) is None

    def test_classify_background_sentence(self):
        sentence = "CRISPR-Cas9 is a widely used gene editing technology in laboratories today."
        assert _classify_sentence(sentence) is None


class TestExtractClaimsHeuristic:
    """Test the full heuristic extraction pipeline."""

    def test_extract_from_abstract(self):
        abstract = (
            "CRISPR-Cas9 has emerged as a powerful gene editing tool. "
            "We found that CRISPR significantly increased correction rates in RPE65 mutations. "
            "We hypothesize that this approach may lead to broader applications in retinal disease. "
            "This study has a limitation due to the small sample size of only 12 patients."
        )
        claims = extract_claims_heuristic(abstract)

        assert len(claims) == 3
        types = {c.claim_type for c in claims}
        assert types == {"finding", "hypothesis", "limitation"}

    def test_extract_empty_text(self):
        assert extract_claims_heuristic("") == []

    def test_extract_respects_min_confidence(self):
        abstract = "We found that CRISPR significantly increased success rates."
        claims_low = extract_claims_heuristic(abstract, min_confidence=0.0)
        claims_high = extract_claims_heuristic(abstract, min_confidence=0.99)

        assert len(claims_low) >= len(claims_high)

    def test_extract_attaches_source_chunk_id(self):
        abstract = "We found that treatment significantly improved patient outcomes overall."
        claims = extract_claims_heuristic(abstract, source_chunk_id="chunk-123")

        assert len(claims) == 1
        assert claims[0].source_chunk_id == "chunk-123"


# ============================================================================
# EVIDENCE GRAPH / CONTRADICTION DETECTION TESTS
# ============================================================================

class TestPolarityConflict:
    """Test polarity-conflict detection between claim texts."""

    def test_opposite_pair_detected(self):
        a = "The treatment significantly increased survival rates in patients."
        b = "The treatment significantly decreased survival rates in patients."
        assert _has_polarity_conflict(a, b) is True

    def test_no_conflict_same_direction(self):
        a = "The treatment significantly increased survival rates in patients."
        b = "The treatment significantly increased survival rates in the cohort."
        assert _has_polarity_conflict(a, b) is False

    def test_negation_mismatch_detected(self):
        a = "The drug did not show any significant effect on tumor growth."
        b = "The drug showed a significant effect on tumor growth in mice."
        assert _has_polarity_conflict(a, b) is True

    def test_effective_ineffective_pair(self):
        a = "Gene therapy was effective in treating inherited blindness."
        b = "Gene therapy was ineffective in treating inherited blindness."
        assert _has_polarity_conflict(a, b) is True


def _make_mock_embedder(similarity_value: float):
    """Create a mock embedder that returns a fixed similarity value."""
    embedder = MagicMock()
    embedder.embed_text.return_value = [0.1] * EMBEDDING_DIM
    embedder.similarity.return_value = similarity_value
    embedder.model_name = "mock-model"
    return embedder


class TestCompareClaims:
    """Test compare_claims() classification logic with mocked embeddings."""

    def test_neutral_when_not_topically_related(self):
        embedder = _make_mock_embedder(similarity_value=0.2)

        relation_type, similarity, confidence, explanation = compare_claims(
            "CRISPR treats inherited blindness.",
            "Machine learning improves image recognition.",
            embedder=embedder,
        )

        assert relation_type == "neutral"
        assert similarity == 0.2
        assert "not topically related" in explanation

    def test_contradicts_when_similar_and_opposite_polarity(self):
        embedder = _make_mock_embedder(similarity_value=0.8)

        relation_type, similarity, confidence, explanation = compare_claims(
            "The treatment significantly increased survival rates.",
            "The treatment significantly decreased survival rates.",
            embedder=embedder,
        )

        assert relation_type == "contradicts"
        assert confidence > 0.6
        assert "contradiction" in explanation

    def test_supports_when_similar_and_same_polarity(self):
        embedder = _make_mock_embedder(similarity_value=0.85)

        relation_type, similarity, confidence, explanation = compare_claims(
            "The treatment significantly increased survival rates in the trial.",
            "The treatment significantly increased survival rates in follow-up.",
            embedder=embedder,
        )

        assert relation_type == "supports"
        assert confidence > 0.5


class TestEvidenceGraphBuilder:
    """Test EvidenceGraphBuilder with a mocked DB session and embedder."""

    def _make_builder(self, similarity_value=0.8):
        mock_session = MagicMock()
        embedder = _make_mock_embedder(similarity_value)
        embedder.embed_batch.return_value = [[0.1] * EMBEDDING_DIM]
        embedder.rank_by_similarity.return_value = [0]
        return EvidenceGraphBuilder(mock_session, embedder=embedder), mock_session

    def test_extract_and_store_claims(self):
        builder, session = self._make_builder()

        text = "We found that CRISPR significantly increased correction rates in patients."
        claims = builder.extract_and_store_claims(paper_id="p1", text=text)

        assert len(claims) == 1
        assert claims[0].paper_id == "p1"
        assert claims[0].claim_embedding == [0.1] * EMBEDDING_DIM
        session.add.assert_called()

    def test_extract_and_store_claims_no_candidates(self):
        builder, session = self._make_builder()

        claims = builder.extract_and_store_claims(paper_id="p1", text="Too short.")
        assert claims == []

    def test_link_claim_to_chunk_creates_evidence(self):
        builder, session = self._make_builder(similarity_value=0.8)

        claim = MagicMock(id="c1", claim_embedding=[0.1] * EMBEDDING_DIM)
        chunk = MagicMock(id="ch1", embedding=[0.1] * EMBEDDING_DIM)

        evidence = builder.link_claim_to_chunk(claim, chunk, min_similarity=0.5)

        assert evidence is not None
        assert evidence.claim_id == "c1"
        assert evidence.chunk_id == "ch1"
        assert evidence.evidence_type == "direct"  # similarity 0.8 >= 0.75
        session.add.assert_called_with(evidence)

    def test_link_claim_to_chunk_below_threshold(self):
        builder, session = self._make_builder(similarity_value=0.2)

        claim = MagicMock(id="c1", claim_embedding=[0.1] * EMBEDDING_DIM)
        chunk = MagicMock(id="ch1", embedding=[0.1] * EMBEDDING_DIM)

        evidence = builder.link_claim_to_chunk(claim, chunk, min_similarity=0.5)
        assert evidence is None

    def test_link_claim_to_chunk_missing_embeddings(self):
        builder, session = self._make_builder()

        claim = MagicMock(id="c1", claim_embedding=None)
        chunk = MagicMock(id="ch1", embedding=[0.1] * EMBEDDING_DIM)

        evidence = builder.link_claim_to_chunk(claim, chunk)
        assert evidence is None

    def test_detect_contradiction_returns_result(self):
        builder, session = self._make_builder(similarity_value=0.8)

        claim_a = MagicMock(
            id="a", claim_text="Treatment increased survival significantly."
        )
        claim_b = MagicMock(
            id="b", claim_text="Treatment decreased survival significantly."
        )

        result = builder.detect_contradiction(claim_a, claim_b)

        assert isinstance(result, ContradictionResult)
        assert result.relation_type == "contradicts"
        assert result.claim_a_id == "a"
        assert result.claim_b_id == "b"

    def test_build_relations_for_claim_skips_neutral_by_default(self):
        builder, session = self._make_builder(similarity_value=0.1)  # low sim -> neutral

        claim = MagicMock(id="a", claim_text="Some unrelated claim about biology.")
        other = MagicMock(id="b", claim_text="Something about astrophysics research.")

        relations = builder.build_relations_for_claim(claim, [other], store_neutral=False)
        assert relations == []

    def test_build_relations_for_claim_stores_neutral_when_requested(self):
        builder, session = self._make_builder(similarity_value=0.1)

        claim = MagicMock(id="a", claim_text="Some unrelated claim about biology.")
        other = MagicMock(id="b", claim_text="Something about astrophysics research.")

        relations = builder.build_relations_for_claim(claim, [other], store_neutral=True)
        assert len(relations) == 1
        assert relations[0].relation_type == "neutral"

    def test_build_relations_skips_self_comparison(self):
        builder, session = self._make_builder(similarity_value=0.9)

        claim = MagicMock(id="a", claim_text="Same claim text.")
        relations = builder.build_relations_for_claim(claim, [claim], store_neutral=True)

        assert relations == []

    def test_find_related_claims_ranks_by_similarity(self):
        builder, session = self._make_builder()
        builder.embedder.rank_by_similarity.return_value = [1, 0]

        claim = MagicMock(id="a", claim_embedding=[0.1] * EMBEDDING_DIM)
        candidate_1 = MagicMock(id="b", claim_embedding=[0.2] * EMBEDDING_DIM)
        candidate_2 = MagicMock(id="c", claim_embedding=[0.3] * EMBEDDING_DIM)

        ranked = builder.find_related_claims(claim, [candidate_1, candidate_2], top_k=2)

        assert ranked[0].id == "c"
        assert ranked[1].id == "b"

    def test_find_related_claims_empty_candidates(self):
        builder, session = self._make_builder()
        claim = MagicMock(id="a", claim_embedding=[0.1] * EMBEDDING_DIM)

        assert builder.find_related_claims(claim, []) == []

    def test_get_contradictions_for_paper_no_claims(self):
        builder, session = self._make_builder()

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        session.query.return_value = mock_query

        result = builder.get_contradictions_for_paper("p1")
        assert result == []
