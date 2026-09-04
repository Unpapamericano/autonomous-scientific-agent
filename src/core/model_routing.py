"""Policy-driven model routing for cost, latency, and safety trade-offs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class TaskKind(str, Enum):
    """Research task classes used by the routing policy."""

    BULK_EXTRACTION = "bulk_extraction"
    SYNTHESIS = "synthesis"
    COMPUTER_USE = "computer_use"
    CYBERSECURITY = "cybersecurity"


@dataclass(frozen=True)
class ModelProfile:
    """Operational characteristics supplied by a local or hosted backend."""

    name: str
    quality: float
    cost_per_million_output: float
    latency_score: float
    supports_tools: bool = False


@dataclass(frozen=True)
class RoutingDecision:
    """Auditable result of selecting a model for a task."""

    model: str
    reason: str
    requires_confirmation: bool = False

    def to_dict(self) -> Dict[str, object]:
        return {
            "model": self.model,
            "reason": self.reason,
            "requires_confirmation": self.requires_confirmation,
        }


def choose_model(
    task: TaskKind | str,
    profiles: list[ModelProfile],
    *,
    budget_per_million_output: float | None = None,
    confirmed_high_risk: bool = False,
) -> RoutingDecision:
    """Choose the best eligible profile using explicit task constraints.

    Cybersecurity tasks are limited to defensive-capable tool models and
    always require an affirmative confirmation before execution.
    """

    if not profiles:
        raise ValueError("At least one model profile is required")
    kind = TaskKind(task)
    eligible = profiles
    if budget_per_million_output is not None:
        eligible = [
            profile
            for profile in profiles
            if profile.cost_per_million_output <= budget_per_million_output
        ]
        if not eligible:
            raise ValueError("No model profile fits the configured output budget")
    if kind == TaskKind.COMPUTER_USE:
        eligible = [profile for profile in eligible if profile.supports_tools]
        if not eligible:
            raise ValueError("Computer-use tasks require a tool-capable model")
    if kind == TaskKind.CYBERSECURITY:
        eligible = [profile for profile in eligible if profile.supports_tools]
        if not eligible:
            raise ValueError("Defensive cybersecurity tasks require a tool-capable model")
    if kind == TaskKind.BULK_EXTRACTION:
        selected = min(eligible, key=lambda profile: (profile.cost_per_million_output, -profile.latency_score))
        reason = "Selected the lowest-cost eligible profile for bulk extraction."
    else:
        selected = max(eligible, key=lambda profile: (profile.quality, profile.latency_score))
        reason = "Selected the highest-quality eligible profile for complex reasoning."
    requires_confirmation = kind == TaskKind.CYBERSECURITY
    if requires_confirmation and confirmed_high_risk:
        reason += " High-risk confirmation was recorded by the caller."
    return RoutingDecision(selected.name, reason, requires_confirmation)
