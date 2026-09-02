"""Recognized-source governance for evidence-based research workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, Iterable, List


class SourceTier(str, Enum):
    """Evidence-source role, not a judgment about an individual paper."""

    AUTHORITY = "authority"
    INDEX = "index"
    GUIDELINE = "guideline"
    PRIMARY_RESEARCH = "primary_research"


@dataclass(frozen=True)
class RecognizedSource:
    name: str
    organization: str
    url: str
    tier: SourceTier
    use_for: str
    notes: str = ""

    def to_dict(self) -> Dict[str, str]:
        payload = asdict(self)
        payload["tier"] = self.tier.value
        return payload


@dataclass(frozen=True)
class EvidenceClaim:
    claim_id: str
    statement: str
    source_ids: List[str]
    evidence_type: str
    status: str = "unreviewed"

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


MS_RECOGNIZED_SOURCES = (
    RecognizedSource(
        "WHO multiple sclerosis",
        "World Health Organization",
        "https://www.who.int/news-room/fact-sheets/detail/multiple-sclerosis",
        SourceTier.AUTHORITY,
        "global disease definitions, burden, and public-health context",
    ),
    RecognizedSource(
        "NINDS multiple sclerosis",
        "U.S. National Institute of Neurological Disorders and Stroke",
        "https://www.ninds.nih.gov/health-information/disorders/multiple-sclerosis",
        SourceTier.AUTHORITY,
        "clinical overview, symptoms, diagnosis, and treatment context",
    ),
    RecognizedSource(
        "PubMed/MEDLINE",
        "U.S. National Library of Medicine",
        "https://pubmed.ncbi.nlm.nih.gov/",
        SourceTier.INDEX,
        "retrievable biomedical primary studies and reviews",
    ),
    RecognizedSource(
        "Cochrane Library",
        "Cochrane",
        "https://www.cochranelibrary.com/",
        SourceTier.GUIDELINE,
        "systematic reviews and evidence-quality synthesis",
    ),
    RecognizedSource(
        "ECTRIMS",
        "European Committee for Treatment and Research in Multiple Sclerosis",
        "https://ectrims.eu/",
        SourceTier.GUIDELINE,
        "specialist consensus, clinical research, and treatment guidance",
    ),
    RecognizedSource(
        "MS International Federation",
        "Multiple Sclerosis International Federation",
        "https://www.msif.org/about-ms/",
        SourceTier.AUTHORITY,
        "international patient-facing context and global MS information",
    ),
    RecognizedSource(
        "ClinicalTrials.gov",
        "U.S. National Library of Medicine",
        "https://clinicaltrials.gov/",
        SourceTier.PRIMARY_RESEARCH,
        "trial registration, status, eligibility, and outcome reporting",
    ),
    RecognizedSource(
        "FDA",
        "U.S. Food and Drug Administration",
        "https://www.fda.gov/",
        SourceTier.AUTHORITY,
        "regulatory approvals, safety communications, and labels",
    ),
    RecognizedSource(
        "EMA",
        "European Medicines Agency",
        "https://www.ema.europa.eu/",
        SourceTier.AUTHORITY,
        "European regulatory assessments and medicine safety information",
    ),
)


def get_ms_source_registry() -> List[RecognizedSource]:
    """Return a copy of the curated MS source registry."""

    return list(MS_RECOGNIZED_SOURCES)


def validate_claim_sources(
    claims: Iterable[EvidenceClaim],
    sources: Iterable[RecognizedSource],
) -> List[str]:
    """Return claim IDs that lack a recognized source or evidence type."""

    source_ids = {source.name for source in sources}
    invalid: List[str] = []
    for claim in claims:
        if not claim.source_ids or not set(claim.source_ids).issubset(source_ids):
            invalid.append(claim.claim_id)
        elif not claim.evidence_type.strip():
            invalid.append(claim.claim_id)
    return invalid
