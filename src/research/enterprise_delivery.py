"""Enterprise-inspired software and AI delivery workflow.

This is an original, lightweight adaptation of public industry practices. It
is not a representation of any company's proprietary process.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class DeliveryStage(str, Enum):
    DISCOVER = "discover"
    DESIGN = "design"
    BUILD = "build"
    VALIDATE = "validate"
    RELEASE = "release"
    OPERATE = "operate"
    EVOLVE = "evolve"


@dataclass
class DeliveryGate:
    """Evidence required before moving to the next delivery stage."""

    stage: DeliveryStage
    required_checks: List[str]
    completed_checks: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return set(self.required_checks).issubset(self.completed_checks)

    def complete(self, check: str) -> None:
        if check not in self.required_checks:
            raise ValueError(f"Unknown check for {self.stage.value}: {check}")
        if check not in self.completed_checks:
            self.completed_checks.append(check)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["stage"] = self.stage.value
        payload["passed"] = self.passed
        return payload


def default_delivery_gates() -> List[DeliveryGate]:
    """Return the quality gates for this scientific AI project."""

    return [
        DeliveryGate(DeliveryStage.DISCOVER, ["problem_brief", "success_metrics", "risk_register"]),
        DeliveryGate(DeliveryStage.DESIGN, ["architecture", "data_contract", "threat_model"]),
        DeliveryGate(DeliveryStage.BUILD, ["reproducible_code", "unit_tests", "observability"]),
        DeliveryGate(DeliveryStage.VALIDATE, ["quality_evaluation", "evidence_review", "human_review"]),
        DeliveryGate(DeliveryStage.RELEASE, ["release_notes", "rollback_plan", "approval"]),
        DeliveryGate(DeliveryStage.OPERATE, ["drift_monitoring", "incident_path", "cost_tracking"]),
        DeliveryGate(DeliveryStage.EVOLVE, ["feedback_loop", "backlog_update", "next_experiment"]),
    ]


def next_ready_stage(gates: List[DeliveryGate]) -> DeliveryStage | None:
    """Return the first incomplete gate, or ``None`` when the loop is complete."""

    for gate in gates:
        if not gate.passed:
            return gate.stage
    return None
