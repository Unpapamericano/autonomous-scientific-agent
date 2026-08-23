"""
Phase 9: Evaluation Metrics

Implements metrics for RQ1–RQ7 research questions:
- RQ1: Task completion rate, coverage, latency
- RQ2: Citation precision, recall, hallucination rate
- RQ3: Tool effectiveness (completion vs. no tools)
- RQ4: Contradiction detection F1
- RQ5: Security attack resistance
- RQ6: Model comparison (latency, accuracy, cost)
- RQ7: Quality-cost Pareto frontier
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of evaluation metrics."""
    COMPLETION_RATE = "completion_rate"
    COVERAGE = "coverage"
    LATENCY = "latency"
    CITATION_PRECISION = "citation_precision"
    CITATION_RECALL = "citation_recall"
    HALLUCINATION_RATE = "hallucination_rate"
    GROUNDING_CONFIDENCE = "grounding_confidence"
    CONTRADICTION_F1 = "contradiction_f1"
    CONTRADICTION_PRECISION = "contradiction_precision"
    CONTRADICTION_RECALL = "contradiction_recall"
    TOOL_COMPLETION_RATE = "tool_completion_rate"
    ERROR_RECOVERY_RATE = "error_recovery_rate"
    ATTACK_SUCCESS_RATE = "attack_success_rate"
    FALSE_POSITIVE_RATE = "false_positive_rate"
    INFERENCE_TIME = "inference_time"
    VRAM_USAGE = "vram_usage"
    COST_PER_QUERY = "cost_per_query"


@dataclass
class EvaluationMetric:
    """Single evaluation metric result."""
    metric_type: MetricType
    value: float  # 0.0-1.0 for rates/scores
    unit: str  # "rate", "seconds", "GB", "$", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class RQ1Result:
    """RQ1: Task Completion, Coverage, Latency"""
    task_completion_rate: float  # % of questions answered end-to-end
    answer_coverage: int  # # unique papers cited
    latency_seconds: float  # seconds from question to report
    workflow_errors: int  # # of crashes/failures
    traceable_citations: int  # # of claims with sources

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_completion_rate": self.task_completion_rate,
            "answer_coverage": self.answer_coverage,
            "latency_seconds": self.latency_seconds,
            "workflow_errors": self.workflow_errors,
            "traceable_citations": self.traceable_citations,
        }


@dataclass
class RQ2Result:
    """RQ2: Evidence-Grounded RAG reduces hallucination"""
    grounded_precision: float  # % of claims citing relevant docs
    grounded_recall: float  # % of extractable facts cited
    hallucination_rate: float  # % of unsupported claims
    avg_grounding_confidence: float  # 0.0-1.0
    treatment: str  # "rag_grounded" or "no_rag"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grounded_precision": self.grounded_precision,
            "grounded_recall": self.grounded_recall,
            "hallucination_rate": self.hallucination_rate,
            "avg_grounding_confidence": self.avg_grounding_confidence,
            "treatment": self.treatment,
        }


@dataclass
class RQ3Result:
    """RQ3: Tool use effect on research quality"""
    task_completion_rate: float
    evidence_extraction_f1: float
    analysis_depth: int  # # unique claims
    error_recovery_rate: float
    tool_set: str  # "full", "search_only", "none"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_completion_rate": self.task_completion_rate,
            "evidence_extraction_f1": self.evidence_extraction_f1,
            "analysis_depth": self.analysis_depth,
            "error_recovery_rate": self.error_recovery_rate,
            "tool_set": self.tool_set,
        }


@dataclass
class RQ4Result:
    """RQ4: Contradiction detection reliability"""
    precision: float  # % detected contradictions are real
    recall: float  # % of actual contradictions detected
    f1_score: float  # harmonic mean
    false_positive_rate: float  # disagreement misidentified

    def to_dict(self) -> Dict[str, Any]:
        return {
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "false_positive_rate": self.false_positive_rate,
        }


@dataclass
class RQ5Result:
    """RQ5: Prompt injection attack resistance"""
    attack_success_rate: float  # % of injections that modified behavior
    false_positive_rate: float  # % of benign inputs flagged
    latency_overhead_ms: float  # milliseconds added for security
    attacks_blocked: int  # # successful blocks
    attacks_passed: int  # # successful injections

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attack_success_rate": self.attack_success_rate,
            "false_positive_rate": self.false_positive_rate,
            "latency_overhead_ms": self.latency_overhead_ms,
            "attacks_blocked": self.attacks_blocked,
            "attacks_passed": self.attacks_passed,
        }


@dataclass
class RQ6Result:
    """RQ6: Model comparison (Muse vs. Gemma/Qwen/Nemotron)"""
    model_name: str
    task_completion_rate: float
    evidence_accuracy_f1: float
    contradiction_detection_f1: float
    inference_time_seconds: float
    vram_usage_gb: float
    cost_per_query_dollars: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "task_completion_rate": self.task_completion_rate,
            "evidence_accuracy_f1": self.evidence_accuracy_f1,
            "contradiction_detection_f1": self.contradiction_detection_f1,
            "inference_time_seconds": self.inference_time_seconds,
            "vram_usage_gb": self.vram_usage_gb,
            "cost_per_query_dollars": self.cost_per_query_dollars,
        }


@dataclass
class RQ7Result:
    """RQ7: Quality-cost Pareto frontier"""
    quantization: str  # "2-bit", "4-bit", "8-bit", "bf16"
    hardware: str  # "cpu", "rtx4090", "a100"
    quality_score: float  # composite 0.0-1.0
    latency_seconds: float
    cost_per_query: float
    quality_components: Dict[str, float] = field(default_factory=dict)  # RQ1-4 weights

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quantization": self.quantization,
            "hardware": self.hardware,
            "quality_score": self.quality_score,
            "latency_seconds": self.latency_seconds,
            "cost_per_query": self.cost_per_query,
            "quality_components": self.quality_components,
        }


class MetricsCalculator:
    """
    Calculates evaluation metrics from evaluation results.
    """

    @staticmethod
    def calculate_rq1(
        num_tasks_total: int,
        num_tasks_completed: int,
        num_papers_cited: int,
        total_latency_seconds: float,
        workflow_errors: int,
        traceable_citations: int,
    ) -> RQ1Result:
        """Calculate RQ1 metrics."""
        completion_rate = (
            num_tasks_completed / num_tasks_total if num_tasks_total > 0 else 0.0
        )
        avg_latency = total_latency_seconds / num_tasks_completed if num_tasks_completed > 0 else 0.0

        return RQ1Result(
            task_completion_rate=completion_rate,
            answer_coverage=num_papers_cited,
            latency_seconds=avg_latency,
            workflow_errors=workflow_errors,
            traceable_citations=traceable_citations,
        )

    @staticmethod
    def calculate_rq2(
        num_claims_total: int,
        num_claims_with_citations: int,
        num_extractable_facts: int,
        num_facts_cited: int,
        confidence_scores: List[float],
        treatment: str = "rag_grounded",
    ) -> RQ2Result:
        """Calculate RQ2 metrics."""
        precision = (
            num_claims_with_citations / num_claims_total if num_claims_total > 0 else 0.0
        )
        recall = num_facts_cited / num_extractable_facts if num_extractable_facts > 0 else 0.0
        hallucination_rate = 1.0 - precision
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return RQ2Result(
            grounded_precision=precision,
            grounded_recall=recall,
            hallucination_rate=hallucination_rate,
            avg_grounding_confidence=avg_confidence,
            treatment=treatment,
        )

    @staticmethod
    def calculate_rq3(
        completion_rate: float,
        extraction_tp: int,  # True positives
        extraction_fp: int,  # False positives
        extraction_fn: int,  # False negatives
        num_claims: int,
        tool_errors_recovered: int,
        tool_errors_total: int,
        tool_set: str = "full",
    ) -> RQ3Result:
        """Calculate RQ3 metrics."""
        # F1 on evidence extraction
        precision = extraction_tp / (extraction_tp + extraction_fp) if (extraction_tp + extraction_fp) > 0 else 0.0
        recall = extraction_tp / (extraction_tp + extraction_fn) if (extraction_tp + extraction_fn) > 0 else 0.0
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        error_recovery_rate = (
            tool_errors_recovered / tool_errors_total if tool_errors_total > 0 else 1.0
        )

        return RQ3Result(
            task_completion_rate=completion_rate,
            evidence_extraction_f1=f1,
            analysis_depth=num_claims,
            error_recovery_rate=error_recovery_rate,
            tool_set=tool_set,
        )

    @staticmethod
    def calculate_rq4(
        tp: int,  # True positives (real contradictions detected)
        fp: int,  # False positives (non-contradictions flagged)
        fn: int,  # False negatives (contradictions missed)
    ) -> RQ4Result:
        """Calculate RQ4 metrics."""
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        false_positive_rate = fp / (fp + (30 - fp - fn)) if (fp + (30 - fp - fn)) > 0 else 0.0

        return RQ4Result(
            precision=precision,
            recall=recall,
            f1_score=f1,
            false_positive_rate=false_positive_rate,
        )

    @staticmethod
    def calculate_rq5(
        attacks_blocked: int,
        attacks_passed: int,
        false_positives: int,
        benign_inputs: int,
        security_latency_overhead_ms: float,
    ) -> RQ5Result:
        """Calculate RQ5 metrics."""
        total_attacks = attacks_blocked + attacks_passed
        attack_success_rate = attacks_passed / total_attacks if total_attacks > 0 else 0.0
        false_positive_rate = (
            false_positives / benign_inputs if benign_inputs > 0 else 0.0
        )

        return RQ5Result(
            attack_success_rate=attack_success_rate,
            false_positive_rate=false_positive_rate,
            latency_overhead_ms=security_latency_overhead_ms,
            attacks_blocked=attacks_blocked,
            attacks_passed=attacks_passed,
        )

    @staticmethod
    def calculate_rq6_models(results: List[RQ6Result]) -> Dict[str, RQ6Result]:
        """Organize RQ6 results by model."""
        return {r.model_name: r for r in results}

    @staticmethod
    def calculate_rq7_quality_score(
        rq1_completion: float,  # 40% weight
        rq2_precision: float,  # 35% weight
        rq4_f1: float,  # 15% weight
        rq5_security: float,  # 10% weight
    ) -> float:
        """Calculate composite quality score for RQ7."""
        weights = {
            "rq1": 0.40,
            "rq2": 0.35,
            "rq4": 0.15,
            "rq5": 0.10,
        }

        # Normalize security to 0-1 (1 - attack_success_rate)
        security_score = rq5_security

        score = (
            weights["rq1"] * rq1_completion
            + weights["rq2"] * rq2_precision
            + weights["rq4"] * rq4_f1
            + weights["rq5"] * security_score
        )

        return score


def get_metrics_calculator() -> MetricsCalculator:
    """Get a metrics calculator instance."""
    return MetricsCalculator()
