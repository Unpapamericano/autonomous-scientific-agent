from src.research.adaptive_analysis import (
    ProcessingMode,
    create_plan,
)


def test_adaptive_plan_prioritizes_relevant_evidence():
    units = [
        {"source_id": "video-1", "kind": "timestamp", "locator": "00:01", "relevance": 0.2},
        {"source_id": "video-1", "kind": "timestamp", "locator": "00:42", "relevance": 0.95},
        {"source_id": "video-1", "kind": "timestamp", "locator": "01:15", "relevance": 0.7},
    ]

    plan = create_plan(ProcessingMode.FAST, units, query="main argument")

    assert plan.evidence_locations[0].locator == "00:42"
    assert plan.telemetry is not None
    assert plan.telemetry.inspection_ratio == 1.0
    assert plan.to_dict()["mode"] == "fast"


def test_adaptive_plan_has_explicit_budget_by_mode():
    fast = create_plan("fast", [])
    deep = create_plan("deep", [])

    assert fast.scan_limit < deep.scan_limit
    assert fast.inspect_limit < deep.inspect_limit
    assert fast.rationale.startswith("Scan up to 20 units")
