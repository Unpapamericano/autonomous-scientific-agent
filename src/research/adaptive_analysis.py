"""Adaptive, evidence-localized research planning.

This module captures the generalizable part of agentic video understanding:
scan cheaply first, then spend effort only on relevant evidence. It is
backend-agnostic and works for papers, PDFs, datasets, images, and videos.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List


class ProcessingMode(str, Enum):
    """Trade latency and cost for deeper inspection."""

    FAST = "fast"
    BALANCED = "balanced"
    DEEP = "deep"


@dataclass(frozen=True)
class EvidenceLocation:
    """A precise pointer into a source artifact."""

    source_id: str
    kind: str
    locator: str
    relevance: float
    excerpt: str = ""


@dataclass
class AnalysisTelemetry:
    """Metrics needed to compare adaptive and static processing."""

    mode: str
    scanned_units: int = 0
    inspected_units: int = 0
    tool_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    evidence_coverage: float = 0.0
    confidence: float = 0.0

    @property
    def inspection_ratio(self) -> float:
        if self.scanned_units == 0:
            return 0.0
        return self.inspected_units / self.scanned_units

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["inspection_ratio"] = round(self.inspection_ratio, 4)
        return payload


@dataclass
class AdaptiveAnalysisPlan:
    """Plan produced before expensive multimodal or tool-based analysis."""

    mode: ProcessingMode
    scan_limit: int
    inspect_limit: int
    rationale: str
    evidence_locations: List[EvidenceLocation] = field(default_factory=list)
    telemetry: AnalysisTelemetry | None = None

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["mode"] = self.mode.value
        payload["evidence_locations"] = [
            asdict(location) for location in self.evidence_locations
        ]
        if self.telemetry is not None:
            payload["telemetry"] = self.telemetry.to_dict()
        return payload


_LIMITS = {
    ProcessingMode.FAST: (20, 5),
    ProcessingMode.BALANCED: (100, 20),
    ProcessingMode.DEEP: (500, 100),
}


def create_plan(
    mode: ProcessingMode | str,
    units: Iterable[Dict[str, Any]],
    *,
    query: str = "",
) -> AdaptiveAnalysisPlan:
    """Rank candidate evidence and select a bounded inspection budget.

    ``units`` may represent pages, transcript segments, timestamps, figures,
    or data partitions. Each unit can provide ``source_id``, ``kind``,
    ``locator``, ``relevance``, and ``excerpt``.
    """

    selected_mode = ProcessingMode(mode)
    scan_limit, inspect_limit = _LIMITS[selected_mode]
    candidates = list(units)[:scan_limit]
    ranked = sorted(
        candidates,
        key=lambda unit: float(unit.get("relevance", 0.0)),
        reverse=True,
    )[:inspect_limit]
    locations = [
        EvidenceLocation(
            source_id=str(unit.get("source_id", "unknown")),
            kind=str(unit.get("kind", "unknown")),
            locator=str(unit.get("locator", "")),
            relevance=max(0.0, min(1.0, float(unit.get("relevance", 0.0)))),
            excerpt=str(unit.get("excerpt", "")),
        )
        for unit in ranked
    ]
    rationale = (
        f"Scan up to {scan_limit} units, then inspect the {len(locations)} "
        f"highest-relevance units"
        + (f" for query: {query}" if query else "")
        + "."
    )
    telemetry = AnalysisTelemetry(
        mode=selected_mode.value,
        scanned_units=len(candidates),
        inspected_units=len(locations),
    )
    return AdaptiveAnalysisPlan(
        mode=selected_mode,
        scan_limit=scan_limit,
        inspect_limit=inspect_limit,
        rationale=rationale,
        evidence_locations=locations,
        telemetry=telemetry,
    )
