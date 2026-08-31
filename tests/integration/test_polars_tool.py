import pytest

from src.core.tools import ToolRegistry
from src.core.tools_impl import analyze_experiments, register_core_tools


@pytest.mark.asyncio
async def test_analyze_experiments_summary():
    result = await analyze_experiments(
        [
            {"solution": "A", "score": 0.8},
            {"solution": "A", "score": 1.0},
        ]
    )

    assert result["analysis"] == "summary"
    assert result["rows"][0]["mean_score"] == 0.9


@pytest.mark.asyncio
async def test_analyze_experiments_is_registered_and_validated():
    registry = ToolRegistry()
    register_core_tools(registry)

    result = await registry.execute(
        "analyze_experiments",
        {
            "analysis": "pareto",
            "records": [
                {"solution": "cheap", "quality": 0.8, "cost": 1},
                {"solution": "best", "quality": 0.95, "cost": 3},
            ],
        },
    )

    assert result["analysis"] == "pareto"
    assert [row["solution"] for row in result["rows"]] == ["cheap", "best"]


@pytest.mark.asyncio
async def test_analyze_experiments_rejects_unknown_analysis():
    with pytest.raises(ValueError, match="summary, rank, pareto"):
        await analyze_experiments([], analysis="unknown")
