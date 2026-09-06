"""Governed Coach knowledge and evidence construction.

This is intentionally a small, versioned domain body rather than an opaque
prompt. Rules are inspectable, testable, and replaceable as the product learns
from validated coaching outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import AnalysisReport, EvidenceItem


@dataclass(frozen=True)
class CoachBody:
    name: str = "Trombone Coach AI"
    version: str = "0.2.0"
    mission: str = "Turn practice recordings into honest, actionable performance feedback."
    principles: tuple[str, ...] = (
        "Measured values are separate from interpretation.",
        "Low confidence withholds precision instead of guessing.",
        "Recommendations are bounded practice actions, not promises.",
        "Practice memory remains portable and auditable.",
    )


COACH_BODY = CoachBody()


def build_evidence(report: AnalysisReport) -> list[EvidenceItem]:
    """Create a provenance ledger from one analysis report."""

    items: list[EvidenceItem] = []
    if report.detected_notes:
        for index, note in enumerate(report.detected_notes, start=1):
            cents = (
                f"{note.cents_deviation:+.1f} cents"
                if note.cents_deviation is not None
                else "cents withheld at low confidence"
            )
            items.append(
                EvidenceItem(
                    id=f"pitch-{index}",
                    kind="measured",
                    text=f"{note.note}: {cents}; confidence {note.confidence:.2f}.",
                    source=f"audio-engine:{report.engine}",
                    confidence=note.confidence,
                )
            )
    for index, interpretation in enumerate(report.interpretation, start=1):
        items.append(
            EvidenceItem(
                id=f"interpretation-{index}",
                kind="interpreted",
                text=interpretation,
                source="coach-rulebook:v1",
                confidence=report.performance_score.confidence,
            )
        )
    for index, recommendation in enumerate(report.recommendations, start=1):
        items.append(
            EvidenceItem(
                id=f"recommendation-{index}",
                kind="recommended",
                text=recommendation,
                source="coach-rulebook:v1",
                confidence=report.performance_score.confidence,
            )
        )
    return items


def with_evidence(report: AnalysisReport) -> AnalysisReport:
    """Return a report with its immutable provenance ledger attached."""

    return report.model_copy(update={"evidence": build_evidence(report)})
