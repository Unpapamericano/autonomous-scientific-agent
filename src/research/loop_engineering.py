"""Closed-loop engineering primitives for measurable research workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List


LOOP_STAGES = ("define", "build", "measure", "review", "iterate")


@dataclass
class LoopIteration:
    """One auditable pass through the engineering loop."""

    iteration: int
    objective: str
    stage_results: Dict[str, Any] = field(default_factory=dict)
    decision: str = "continue"
    started_at: str = ""
    completed_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LoopEngineer:
    """Run bounded define-build-measure-review-iterate cycles.

    Callbacks are deliberately small and injectable so the loop can wrap
    local model inference, Polars analysis, tool execution, or human review.
    """

    def __init__(
        self,
        objective: str,
        *,
        define: Callable[[str, int], Any],
        build: Callable[[Any, int], Any],
        measure: Callable[[Any, int], Any],
        review: Callable[[Any, Any, int], Any],
        iterate: Callable[[Any, int], str],
    ) -> None:
        self.objective = objective
        self._callbacks = (define, build, measure, review, iterate)

    def run(self, max_iterations: int = 1) -> List[LoopIteration]:
        if max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")

        history: List[LoopIteration] = []
        objective = self.objective
        for iteration in range(1, max_iterations + 1):
            started = datetime.now(timezone.utc).isoformat()
            definition = self._callbacks[0](objective, iteration)
            artifact = self._callbacks[1](definition, iteration)
            metrics = self._callbacks[2](artifact, iteration)
            review = self._callbacks[3](metrics, artifact, iteration)
            decision = self._callbacks[4](review, iteration)
            if decision not in {"continue", "stop"}:
                raise ValueError("iterate callback must return 'continue' or 'stop'")
            record = LoopIteration(
                iteration=iteration,
                objective=objective,
                stage_results={
                    "define": definition,
                    "build": artifact,
                    "measure": metrics,
                    "review": review,
                },
                decision=decision,
                started_at=started,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            history.append(record)
            if decision == "stop":
                break
            objective = f"{objective} (iteration {iteration + 1})"
        return history
