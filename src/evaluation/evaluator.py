"""
Phase 9: Evaluation Orchestrator

Orchestrates end-to-end evaluation runs for RQ1-RQ7.
Manages test execution, metrics collection, and reporting.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class EvaluationPhase(str, Enum):
    """Phase of evaluation."""
    SETUP = "setup"
    EXECUTION = "execution"
    METRICS = "metrics"
    REPORTING = "reporting"
    CLEANUP = "cleanup"


@dataclass
class EvaluationConfig:
    """Configuration for an evaluation run."""
    name: str  # e.g., "RQ1_Completion_Test"
    description: str
    test_set: str  # "research_questions", "contradictions", "adversarial"
    timeout_seconds: int = 300
    num_workers: int = 1
    collect_metrics: bool = True
    generate_report: bool = True


@dataclass
class EvaluationRun:
    """A single evaluation run."""
    run_id: str
    config: EvaluationConfig
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    status: str = "running"  # "running", "completed", "failed"
    phase: EvaluationPhase = EvaluationPhase.SETUP
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metrics_summary: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "config": {
                "name": self.config.name,
                "description": self.config.description,
                "test_set": self.config.test_set,
            },
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "phase": self.phase.value,
            "results_count": len(self.results),
            "errors_count": len(self.errors),
            "metrics_summary": self.metrics_summary,
        }


class EvaluationOrchestrator:
    """
    Orchestrates evaluation runs end-to-end.
    """

    def __init__(self):
        self.runs: List[EvaluationRun] = []
        self.current_run: Optional[EvaluationRun] = None

    def create_run(self, config: EvaluationConfig) -> EvaluationRun:
        """Create a new evaluation run."""
        run_id = f"{config.name}_{datetime.utcnow().timestamp()}"
        run = EvaluationRun(run_id=run_id, config=config)
        self.runs.append(run)
        self.current_run = run
        logger.info(f"Created evaluation run: {run_id}")
        return run

    def start_run(self, run: EvaluationRun) -> None:
        """Start an evaluation run (move to EXECUTION phase)."""
        self.current_run = run
        run.phase = EvaluationPhase.EXECUTION
        run.status = "running"
        logger.info(f"Starting evaluation run: {run.run_id}")

    def add_result(self, test_id: str, result: Any) -> None:
        """Add a test result to current run."""
        if self.current_run is None:
            raise RuntimeError("No active run")

        self.current_run.results[test_id] = result
        logger.debug(f"Added result for test {test_id}")

    def add_error(self, error_msg: str) -> None:
        """Add an error to current run."""
        if self.current_run is None:
            raise RuntimeError("No active run")

        self.current_run.errors.append(error_msg)
        logger.error(f"Evaluation error: {error_msg}")

    def complete_metrics_phase(self, metrics: Dict[str, float]) -> None:
        """Move to METRICS phase and store metrics."""
        if self.current_run is None:
            raise RuntimeError("No active run")

        self.current_run.phase = EvaluationPhase.METRICS
        self.current_run.metrics_summary = metrics
        logger.info(f"Metrics phase complete for {self.current_run.run_id}")

    def complete_run(self, status: str = "completed") -> None:
        """Complete the current evaluation run."""
        if self.current_run is None:
            raise RuntimeError("No active run")

        self.current_run.phase = EvaluationPhase.REPORTING
        self.current_run.status = status
        self.current_run.end_time = datetime.utcnow().isoformat()
        logger.info(f"Evaluation run completed: {self.current_run.run_id} (status={status})")

    def get_run(self, run_id: str) -> Optional[EvaluationRun]:
        """Get a run by ID."""
        for run in self.runs:
            if run.run_id == run_id:
                return run
        return None

    def get_all_runs(self) -> List[EvaluationRun]:
        """Get all runs."""
        return self.runs

    def get_runs_by_status(self, status: str) -> List[EvaluationRun]:
        """Get runs by status."""
        return [r for r in self.runs if r.status == status]

    def export_runs(self) -> Dict[str, Any]:
        """Export all runs as dict."""
        return {
            "total_runs": len(self.runs),
            "runs": [r.to_dict() for r in self.runs],
            "export_timestamp": datetime.utcnow().isoformat(),
        }


class TestRunner:
    """
    Runs individual tests and collects results.
    """

    def __init__(self, orchestrator: EvaluationOrchestrator):
        self.orchestrator = orchestrator

    def run_test(
        self,
        test_id: str,
        test_func,
        timeout_seconds: int = 300,
    ) -> Dict[str, Any]:
        """
        Run a single test with timeout.

        Args:
            test_id: Unique test identifier
            test_func: Callable that executes the test
            timeout_seconds: Timeout in seconds

        Returns:
            Test result dict
        """
        result = {
            "test_id": test_id,
            "status": "pending",
            "output": None,
            "error": None,
            "duration_seconds": 0.0,
        }

        try:
            start = datetime.utcnow()

            # In Phase 11+, replace with actual timeout execution
            output = test_func()

            end = datetime.utcnow()
            result["status"] = "success"
            result["output"] = output
            result["duration_seconds"] = (end - start).total_seconds()

            self.orchestrator.add_result(test_id, result)
            logger.info(f"Test {test_id} completed in {result['duration_seconds']:.2f}s")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.orchestrator.add_error(f"Test {test_id} failed: {str(e)}")
            logger.error(f"Test {test_id} failed: {str(e)}")

        return result

    def run_batch(
        self,
        tests: List[tuple],  # List of (test_id, test_func) tuples
        timeout_seconds: int = 300,
    ) -> List[Dict[str, Any]]:
        """
        Run a batch of tests sequentially.

        Args:
            tests: List of (test_id, test_func) tuples
            timeout_seconds: Timeout per test

        Returns:
            List of test results
        """
        results = []
        for test_id, test_func in tests:
            result = self.run_test(test_id, test_func, timeout_seconds)
            results.append(result)

        return results


def get_evaluator() -> EvaluationOrchestrator:
    """Get an evaluation orchestrator instance."""
    return EvaluationOrchestrator()


def get_test_runner(orchestrator: EvaluationOrchestrator) -> TestRunner:
    """Get a test runner instance."""
    return TestRunner(orchestrator)
