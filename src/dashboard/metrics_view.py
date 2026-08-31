"""
Phase 10: Metrics Visualization

Provides views and charts for evaluation metrics.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import polars as pl

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
    def build_solution_comparison_chart(
        solutions: List[Dict[str, Any]],
        solution_column: str = "solution",
        score_column: str = "score",
    ) -> ChartData:
        """Build a bar chart showing mean score for each scientific solution.

        Polars performs the numeric coercion, grouping, and ordering so callers
        can pass raw values extracted from papers or experiment results.
        """
        frame = MetricsView._solution_frame(solutions, solution_column, score_column)
        summary = (
            frame.group_by(solution_column)
            .agg(pl.col(score_column).mean().alias("mean_score"))
            .sort(["mean_score", solution_column], descending=[True, False])
        )

        return ChartData(
            title="Scientific Solution Comparison",
            chart_type="bar",
            labels=summary[solution_column].to_list(),
            datasets=[
                {
                    "label": "Mean Score",
                    "data": [round(value, 6) for value in summary["mean_score"].to_list()],
                    "backgroundColor": "#007bff",
                }
            ],
            options={"scales": {"y": {"beginAtZero": True}}},
        )

    @staticmethod
    def build_solution_tradeoff_chart(
        solutions: List[Dict[str, Any]],
        solution_column: str = "solution",
        cost_column: str = "cost",
        quality_column: str = "quality",
    ) -> ChartData:
        """Build a scatter chart exposing solution cost versus quality."""
        required = [solution_column, cost_column, quality_column]
        frame = pl.DataFrame(solutions)
        missing = [column for column in required if column not in frame.columns]
        if missing:
            raise ValueError(f"Missing solution columns: {', '.join(missing)}")

        frame = (
            frame.with_columns(
                pl.col(cost_column).cast(pl.Float64, strict=False),
                pl.col(quality_column).cast(pl.Float64, strict=False),
            )
            .drop_nulls(required)
            .sort(quality_column, descending=True)
        )
        if frame.is_empty():
            raise ValueError("solutions must contain at least one numeric cost and quality value")

        return ChartData(
            title="Scientific Solution Cost-Quality Tradeoff",
            chart_type="scatter",
            labels=frame[solution_column].cast(pl.String).to_list(),
            datasets=[
                {
                    "label": "Solution",
                    "data": [
                        {"x": cost, "y": quality}
                        for cost, quality in zip(
                            frame[cost_column].to_list(),
                            frame[quality_column].to_list(),
                        )
                    ],
                    "backgroundColor": "#28a745",
                }
            ],
            options={
                "scales": {
                    "x": {"title": {"display": True, "text": "Cost"}},
                    "y": {"title": {"display": True, "text": "Quality"}},
                }
            },
        )

    @staticmethod
    def _solution_frame(
        solutions: List[Dict[str, Any]],
        solution_column: str,
        score_column: str,
    ) -> pl.DataFrame:
        """Normalize solution records with Polars for chart construction."""
        frame = pl.DataFrame(solutions)
        required = [solution_column, score_column]
        missing = [column for column in required if column not in frame.columns]
        if missing:
            raise ValueError(f"Missing solution columns: {', '.join(missing)}")

        frame = (
            frame.with_columns(
                pl.col(solution_column).cast(pl.String),
                pl.col(score_column).cast(pl.Float64, strict=False),
            )
            .drop_nulls(required)
        )
        if frame.is_empty():
            raise ValueError("solutions must contain at least one numeric score")
        return frame

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
