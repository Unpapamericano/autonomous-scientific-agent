"""
Phase 10: Metrics Visualization

Provides views and charts for evaluation metrics.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChartData:
    """Data for a single chart."""
    title: str
    chart_type: str  # "bar", "line", "pie", "scatter"
    labels: List[str]
    datasets: List[Dict[str, Any]]  # {label, data, backgroundColor, etc.}
    options: Dict[str, Any] = None


class MetricsView:
    """
    Provides metrics visualization and charting.
    """

    @staticmethod
    def build_rq1_chart(completion_rate: float, latency: float, coverage: int) -> ChartData:
        """Build RQ1 completion metrics chart."""
        return ChartData(
            title="RQ1: Task Completion & Latency",
            chart_type="bar",
            labels=["Completion Rate", "Latency (s)", "Papers Cited"],
            datasets=[
                {
                    "label": "RQ1 Metrics",
                    "data": [completion_rate * 100, latency, coverage],
                    "backgroundColor": ["#007bff", "#28a745", "#ffc107"],
                }
            ],
            options={
                "indexAxis": "y",
                "scales": {
                    "x": {"beginAtZero": True},
                },
            },
        )

    @staticmethod
    def build_rq2_chart(precision: float, recall: float, hallucination: float) -> ChartData:
        """Build RQ2 RAG grounding chart."""
        return ChartData(
            title="RQ2: RAG Grounding Quality",
            chart_type="bar",
            labels=["Citation Precision", "Citation Recall", "Hallucination Rate"],
            datasets=[
                {
                    "label": "RQ2 Metrics",
                    "data": [precision * 100, recall * 100, (1 - hallucination) * 100],
                    "backgroundColor": ["#28a745", "#007bff", "#ffc107"],
                }
            ],
        )

    @staticmethod
    def build_rq4_chart(precision: float, recall: float, f1: float) -> ChartData:
        """Build RQ4 contradiction detection chart."""
        return ChartData(
            title="RQ4: Contradiction Detection",
            chart_type="bar",
            labels=["Precision", "Recall", "F1 Score"],
            datasets=[
                {
                    "label": "RQ4 Metrics",
                    "data": [precision * 100, recall * 100, f1 * 100],
                    "backgroundColor": ["#007bff", "#28a745", "#dc3545"],
                }
            ],
        )

    @staticmethod
    def build_rq5_chart(attack_success: float, false_positive: float) -> ChartData:
        """Build RQ5 security chart."""
        return ChartData(
            title="RQ5: Security Robustness",
            chart_type="pie",
            labels=["Attacks Blocked", "Attacks Passed", "False Positives"],
            datasets=[
                {
                    "label": "Security Events",
                    "data": [
                        (1 - attack_success) * 100,
                        attack_success * 100,
                        false_positive * 100,
                    ],
                    "backgroundColor": ["#28a745", "#dc3545", "#ffc107"],
                }
            ],
        )

    @staticmethod
    def build_rq7_pareto_chart(
        configurations: List[Dict[str, Any]],
    ) -> ChartData:
        """Build RQ7 quality-cost Pareto frontier chart."""
        labels = [f"{c['quantization']}/{c['hardware']}" for c in configurations]
        quality = [c["quality_score"] * 100 for c in configurations]
        cost = [c["cost_per_query"] for c in configurations]

        return ChartData(
            title="RQ7: Quality-Cost Pareto Frontier",
            chart_type="scatter",
            labels=labels,
            datasets=[
                {
                    "label": "Configuration",
                    "data": [
                        {"x": cost[i], "y": quality[i]} for i in range(len(configurations))
                    ],
                    "backgroundColor": "#007bff",
                }
            ],
            options={
                "scales": {
                    "x": {"title": {"display": True, "text": "Cost ($)"}},
                    "y": {"title": {"display": True, "text": "Quality Score (%)"}},
                },
            },
        )

    @staticmethod
    def build_model_comparison_chart(
        models: List[Dict[str, Any]],
    ) -> ChartData:
        """Build RQ6 model comparison chart."""
        return ChartData(
            title="RQ6: Model Performance Comparison",
            chart_type="bar",
            labels=[m["model_name"] for m in models],
            datasets=[
                {
                    "label": "Completion Rate",
                    "data": [m["task_completion_rate"] * 100 for m in models],
                    "backgroundColor": "#007bff",
                },
                {
                    "label": "Evidence Accuracy",
                    "data": [m["evidence_accuracy_f1"] * 100 for m in models],
                    "backgroundColor": "#28a745",
                },
                {
                    "label": "Contradiction F1",
                    "data": [m["contradiction_detection_f1"] * 100 for m in models],
                    "backgroundColor": "#dc3545",
                },
            ],
        )

    @staticmethod
    def build_time_series_chart(
        runs: List[Dict[str, Any]],
        metric_name: str,
    ) -> ChartData:
        """Build time series chart for metric across multiple runs."""
        labels = [r.get("run_id", "Run") for r in runs]
        data = [r.get("metrics_summary", {}).get(metric_name, 0) for r in runs]

        return ChartData(
            title=f"{metric_name} Over Time",
            chart_type="line",
            labels=labels,
            datasets=[
                {
                    "label": metric_name,
                    "data": data,
                    "borderColor": "#007bff",
                    "backgroundColor": "rgba(0, 123, 255, 0.1)",
                }
            ],
        )

    @staticmethod
    def chart_to_json(chart: ChartData) -> Dict[str, Any]:
        """Convert chart to JSON for front-end rendering (Chart.js format)."""
        return {
            "type": chart.chart_type,
            "data": {
                "labels": chart.labels,
                "datasets": chart.datasets,
            },
            "options": chart.options or {},
        }


class MetricsTable:
    """
    Provides tabular metrics display.
    """

    @staticmethod
    def build_rq_summary_table(rq_results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build table of RQ results."""
        rows = []
        for rq, results in rq_results.items():
            rows.append({
                "RQ": rq,
                "Status": results.get("status", "N/A"),
                "Target": results.get("target", "N/A"),
                "Actual": results.get("actual", "N/A"),
                "Pass": results.get("status") == "PASS",
            })
        return rows

    @staticmethod
    def build_runs_table(runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build table of evaluation runs."""
        rows = []
        for run in runs:
            rows.append({
                "Run ID": run.get("run_id", "N/A"),
                "Test Set": run.get("config", {}).get("test_set", "N/A"),
                "Status": run.get("status", "N/A"),
                "Results": run.get("results_count", 0),
                "Errors": run.get("errors_count", 0),
                "Timestamp": run.get("start_time", "N/A")[:10],  # Date only
            })
        return rows


def get_metrics_view() -> MetricsView:
    """Get a metrics view instance."""
    return MetricsView()


def get_metrics_table() -> MetricsTable:
    """Get a metrics table instance."""
    return MetricsTable()
