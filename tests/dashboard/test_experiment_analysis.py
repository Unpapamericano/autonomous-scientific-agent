import pytest

from src.analysis.experiment_analysis import (
    pareto_frontier,
    rank_solutions,
    summarize_experiments,
)


def test_summarize_experiments_returns_polars_aggregates():
    summary = summarize_experiments(
        [
            {"solution": "A", "score": 0.8},
            {"solution": "A", "score": 1.0},
            {"solution": "B", "score": 0.7},
        ]
    )

    assert summary[0]["solution"] == "A"
    assert summary[0]["mean_score"] == 0.9
    assert summary[0]["observations"] == 2
    assert summary[0]["std_score"] == pytest.approx(0.1)


def test_rank_solutions_uses_quality_per_cost():
    ranked = rank_solutions(
        [
            {"solution": "accurate", "quality": 0.95, "cost": 3},
            {"solution": "efficient", "quality": 0.8, "cost": 1},
        ]
    )

    assert ranked[0]["solution"] == "efficient"
    assert ranked[0]["quality_per_cost"] == pytest.approx(0.8)


def test_pareto_frontier_removes_dominated_candidates():
    frontier = pareto_frontier(
        [
            {"solution": "cheap", "quality": 0.85, "cost": 1},
            {"solution": "best", "quality": 0.95, "cost": 3},
            {"solution": "dominated", "quality": 0.8, "cost": 2},
        ]
    )

    assert [row["solution"] for row in frontier] == ["cheap", "best"]


def test_rank_solutions_rejects_non_positive_cost():
    with pytest.raises(ValueError, match="greater than zero"):
        rank_solutions([{"solution": "A", "quality": 0.8, "cost": 0}])
