from src.research.source_governance import (
    EvidenceClaim,
    get_ms_source_registry,
    validate_claim_sources,
)


def test_ms_registry_contains_global_authoritative_and_research_sources():
    sources = get_ms_source_registry()
    names = {source.name for source in sources}

    assert "WHO multiple sclerosis" in names
    assert "PubMed/MEDLINE" in names
    assert "ClinicalTrials.gov" in names
    assert len(sources) >= 6


def test_claim_validation_rejects_uncited_or_unknown_sources():
    sources = get_ms_source_registry()
    claims = [
        EvidenceClaim("supported", "MS is multifactorial.", ["WHO multiple sclerosis"], "overview"),
        EvidenceClaim("missing", "Uncited statement.", [], "hypothesis"),
        EvidenceClaim("unknown", "Unsupported source.", ["Unknown blog"], "overview"),
    ]

    assert validate_claim_sources(claims, sources) == ["missing", "unknown"]
