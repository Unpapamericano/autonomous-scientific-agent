"""
Phase 5: Claim Extraction

Extracts candidate scientific claims (findings, hypotheses, limitations)
from paper text (abstracts or chunks). Two extraction strategies:

  1. Heuristic sentence-level extraction (Phase 5 default): splits text into
     sentences and classifies each using cue-phrase heuristics. No GPU or
     LLM call required — works everywhere, good enough as a first pass.

  2. LLM-based extraction (optional, Phase 5+): if a ResearchAgent/LLM is
     available, delegate to it for higher-quality claim extraction. Left
     as an extension point (`llm_extract_claims`) since it requires the
     Phase 1 model to be loaded.

A "claim" here means an assertive, checkable statement — as opposed to
background/citation sentences, questions, or purely descriptive text.
"""

import logging
import re
import uuid
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


# Cue phrases that suggest a sentence is reporting a finding/result.
FINDING_CUES = [
    "we found", "we show", "we demonstrate", "results show", "results indicate",
    "our results", "we observed", "was associated with", "significantly",
    "increased", "decreased", "improved", "reduced", "outperform",
    "achieved", "success rate", "efficacy", "efficacious",
]

HYPOTHESIS_CUES = [
    "we hypothesize", "we propose", "we suggest", "may lead to", "could result in",
    "it is possible that", "we predict", "is expected to",
]

LIMITATION_CUES = [
    "limitation", "limited by", "future work", "further research is needed",
    "did not", "failed to", "unable to", "small sample size", "caveat",
]

# Sentences containing these are usually NOT standalone claims (background/citations).
NON_CLAIM_CUES = [
    "et al.", "previously reported", "for example", "in contrast to prior work",
    "?",
]

MIN_CLAIM_WORDS = 6


@dataclass
class ExtractedClaim:
    """A candidate claim extracted from text."""
    claim_text: str
    claim_type: str  # "finding", "hypothesis", "limitation"
    confidence: float  # heuristic confidence 0.0-1.0
    source_chunk_id: Optional[str] = None


def _split_sentences(text: str) -> List[str]:
    """Simple sentence splitter (regex-based, no external NLP dependency)."""
    if not text:
        return []

    # Split on '.', '!', '?' followed by whitespace + capital letter, but
    # avoid splitting on common abbreviations like "et al." or "e.g."
    text = text.replace("et al.", "et al")
    raw_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text.strip())
    return [s.strip() for s in raw_sentences if s.strip()]


def _classify_sentence(sentence: str) -> Optional[tuple]:
    """
    Classify a sentence as a claim type, or None if it's not claim-like.

    Returns:
        (claim_type, confidence) tuple, or None
    """
    lower = sentence.lower()

    if len(sentence.split()) < MIN_CLAIM_WORDS:
        return None

    if any(cue in lower for cue in NON_CLAIM_CUES):
        return None

    finding_hits = sum(1 for cue in FINDING_CUES if cue in lower)
    hypothesis_hits = sum(1 for cue in HYPOTHESIS_CUES if cue in lower)
    limitation_hits = sum(1 for cue in LIMITATION_CUES if cue in lower)

    if limitation_hits > 0:
        confidence = min(0.9, 0.5 + limitation_hits * 0.2)
        return ("limitation", confidence)

    if hypothesis_hits > 0:
        confidence = min(0.85, 0.5 + hypothesis_hits * 0.15)
        return ("hypothesis", confidence)

    if finding_hits > 0:
        confidence = min(0.9, 0.5 + finding_hits * 0.15)
        return ("finding", confidence)

    return None


def extract_claims_heuristic(
    text: str,
    source_chunk_id: Optional[str] = None,
    min_confidence: float = 0.5,
) -> List[ExtractedClaim]:
    """
    Extract candidate claims from text using cue-phrase heuristics.

    Args:
        text: Source text (abstract or chunk content)
        source_chunk_id: Optional chunk ID this text came from (for provenance)
        min_confidence: Minimum heuristic confidence to include

    Returns:
        List of ExtractedClaim
    """
    sentences = _split_sentences(text)
    claims = []

    for sentence in sentences:
        classification = _classify_sentence(sentence)
        if classification is None:
            continue

        claim_type, confidence = classification
        if confidence < min_confidence:
            continue

        claims.append(
            ExtractedClaim(
                claim_text=sentence,
                claim_type=claim_type,
                confidence=confidence,
                source_chunk_id=source_chunk_id,
            )
        )

    logger.info(f"Extracted {len(claims)} candidate claims from {len(sentences)} sentences")
    return claims


async def llm_extract_claims(
    text: str,
    agent=None,
    source_chunk_id: Optional[str] = None,
) -> List[ExtractedClaim]:
    """
    Extract claims using an LLM (Phase 1 ResearchAgent) for higher quality.

    Falls back to the heuristic extractor if no agent is provided, so this
    function is always safe to call regardless of whether a GPU/model is
    available.

    Args:
        text: Source text
        agent: A ResearchAgent instance (Phase 2), or None
        source_chunk_id: Optional chunk ID for provenance

    Returns:
        List of ExtractedClaim
    """
    if agent is None:
        logger.info("No agent provided; falling back to heuristic claim extraction")
        return extract_claims_heuristic(text, source_chunk_id=source_chunk_id)

    prompt = (
        "Extract the key scientific claims from the following text. "
        "For each claim, classify it as 'finding', 'hypothesis', or 'limitation'. "
        "Return one claim per line in the format: TYPE | CLAIM_TEXT\n\n"
        f"Text:\n{text}"
    )

    try:
        response, _ = await agent.query(prompt)
    except Exception as e:
        logger.error(f"LLM claim extraction failed, falling back to heuristics: {e}")
        return extract_claims_heuristic(text, source_chunk_id=source_chunk_id)

    claims = []
    for line in response.splitlines():
        if "|" not in line:
            continue
        claim_type, _, claim_text = line.partition("|")
        claim_type = claim_type.strip().lower()
        claim_text = claim_text.strip()

        if claim_type not in {"finding", "hypothesis", "limitation"} or not claim_text:
            continue

        claims.append(
            ExtractedClaim(
                claim_text=claim_text,
                claim_type=claim_type,
                confidence=0.75,  # LLM extraction assumed more reliable than heuristics
                source_chunk_id=source_chunk_id,
            )
        )

    logger.info(f"LLM extracted {len(claims)} claims")
    return claims or extract_claims_heuristic(text, source_chunk_id=source_chunk_id)
