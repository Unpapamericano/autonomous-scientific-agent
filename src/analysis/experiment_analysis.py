"""Polars-powered analysis helpers for scientific experiment results."""

from typing import Any, Dict, List

import polars as pl


def _as_frame(records: List[Dict[str, Any]], required: List[str]) -> pl.DataFrame:
    """Create a validated numeric experiment frame."""
    frame = pl.DataFrame(records)
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing experiment columns: {', '.join(missing)}")

    numeric = [column for column in required if column != "solution"]
    frame = frame.with_columns(
        [pl.col(column).cast(pl.Float64, strict=False) for column in numeric]
    ).drop_nulls(required)
    if frame.is_empty():
        raise ValueError("records must contain at least one complete numeric experiment")
    return frame


def summarize_experiments(
    records: List[Dict[str, Any]],
    solution_column: str = "solution",
    score_column: str = "score",
) -> List[Dict[str, Any]]:
    """Aggregate solution performance with mean, spread, and sample count."""
    frame = _as_frame(records, [solution_column, score_column])
    summary = (
        frame.group_by(solution_column)
        .agg(
            pl.col(score_column).mean().alias("mean_score"),
            pl.col(score_column).std(ddof=0).fill_null(0.0).alias("std_score"),
            pl.len().alias("observations"),
        )
        .sort("mean_score", descending=True)
    )
    return summary.to_dicts()


def rank_solutions(
    records: List[Dict[str, Any]],
    solution_column: str = "solution",
    quality_column: str = "quality",
    cost_column: str = "cost",
) -> List[Dict[str, Any]]:
    """Rank solutions by quality per unit cost using Polars expressions."""
    frame = _as_frame(records, [solution_column, quality_column, cost_column])
    if (frame[cost_column] <= 0).any():
        raise ValueError("cost values must be greater than zero")

    return (
        frame.with_columns(
            (pl.col(quality_column) / pl.col(cost_column)).alias("quality_per_cost")
        )
        .sort("quality_per_cost", descending=True)
        .to_dicts()
    )


def pareto_frontier(
    records: List[Dict[str, Any]],
    solution_column: str = "solution",
    quality_column: str = "quality",
    cost_column: str = "cost",
) -> List[Dict[str, Any]]:
    """Return non-dominated solutions minimizing cost and maximizing quality."""
    frame = _as_frame(records, [solution_column, quality_column, cost_column])
    rows = frame.to_dicts()
    frontier = [
        candidate
        for candidate in rows
        if not any(
            other[cost_column] <= candidate[cost_column]
            and other[quality_column] >= candidate[quality_column]
            and (
                other[cost_column] < candidate[cost_column]
                or other[quality_column] > candidate[quality_column]
            )
            for other in rows
        )
    ]
    return sorted(frontier, key=lambda row: row[cost_column])
