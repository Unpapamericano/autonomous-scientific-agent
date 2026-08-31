import pytest

from src.dashboard.metrics_view import MetricsView


def test_solution_comparison_aggregates_and_sorts_with_polars():
    chart = MetricsView.build_solution_comparison_chart(
        [
            {"solution": "A", "score": "0.8"},
            {"solution": "A", "score": 1.0},
            {"solution": "B", "score": 0.9},
        ]
    )

    assert chart.labels == ["A", "B"]
    assert chart.datasets[0]["data"] == [0.9, 0.9]


def test_solution_tradeoff_chart_returns_chartjs_points():
    chart = MetricsView.build_solution_tradeoff_chart(
        [
            {"solution": "fast", "cost": "1.5", "quality": 0.75},
            {"solution": "accurate", "cost": 3, "quality": 0.95},
        ]
    )

    assert chart.chart_type == "scatter"
    assert chart.labels == ["accurate", "fast"]
    assert chart.datasets[0]["data"] == [{"x": 3.0, "y": 0.95}, {"x": 1.5, "y": 0.75}]


def test_solution_visualization_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing solution columns"):
        MetricsView.build_solution_comparison_chart([{"solution": "A"}])
