import pytest

from src.music.trombone import (
    RepertoireItem,
    build_practice_plan,
    find_repertoire,
    summarize_practice,
)


def test_build_practice_plan_is_balanced_and_bounded():
    plan = build_practice_plan(60, focus="high register")
    assert plan.instrument == "trombone"
    assert sum(block.minutes for block in plan.blocks) == 60
    assert plan.blocks[0].intensity == "easy"
    assert plan.blocks[-1].focus == "cool-down and notes"


def test_repertoire_can_filter_by_skill_and_level():
    catalog = [
        RepertoireItem("A", "Composer", "intermediate", ("classical",), ("intonation",), "https://example.com"),
        RepertoireItem("B", "Composer", "advanced", ("jazz",), ("improvisation",), "https://example.com"),
    ]
    assert [item.title for item in find_repertoire(catalog, skill="intonation")] == ["A"]


def test_practice_summary_aggregates_focus():
    summary = summarize_practice(
        [
            {"minutes": 30, "focus": "tone"},
            {"minutes": 20, "focus": "tone"},
            {"minutes": 10, "focus": "repertoire"},
        ]
    )
    assert summary["minutes"] == 60
    assert summary["focus_minutes"] == {"tone": 50, "repertoire": 10}


def test_short_practice_plan_is_rejected():
    with pytest.raises(ValueError, match="at least 20"):
        build_practice_plan(15)
