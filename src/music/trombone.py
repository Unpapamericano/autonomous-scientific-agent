"""Evidence-aware practice and repertoire workflows for trombonists."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class PracticeBlock:
    """A bounded block in a practice session."""

    focus: str
    minutes: int
    objective: str
    intensity: str = "moderate"

    def __post_init__(self) -> None:
        if not self.focus.strip() or not self.objective.strip():
            raise ValueError("Practice blocks require a focus and objective")
        if self.minutes < 1:
            raise ValueError("Practice block minutes must be positive")
        if self.intensity not in {"easy", "moderate", "high"}:
            raise ValueError("intensity must be easy, moderate, or high")


@dataclass(frozen=True)
class PracticePlan:
    """A session plan with deliberate warm-up and recovery boundaries."""

    instrument: str
    duration_minutes: int
    blocks: tuple[PracticeBlock, ...]
    generated_on: str

    def to_dict(self) -> dict[str, object]:
        return {
            "instrument": self.instrument,
            "duration_minutes": self.duration_minutes,
            "blocks": [asdict(block) for block in self.blocks],
            "generated_on": self.generated_on,
        }


@dataclass(frozen=True)
class RepertoireItem:
    """Metadata about a work; this project does not distribute sheet music."""

    title: str
    composer: str
    level: str
    styles: tuple[str, ...]
    skills: tuple[str, ...]
    source_url: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_practice_plan(
    duration_minutes: int,
    *,
    focus: str = "fundamentals",
    today: date | None = None,
) -> PracticePlan:
    """Create a balanced, bounded session for a trombone player."""

    if duration_minutes < 20:
        raise ValueError("Practice sessions must allow at least 20 minutes")
    warmup = max(5, round(duration_minutes * 0.2))
    technique = max(5, round(duration_minutes * 0.3))
    repertoire = max(5, round(duration_minutes * 0.35))
    reflection = duration_minutes - warmup - technique - repertoire
    if reflection < 5:
        repertoire -= 5 - reflection
        reflection = 5
    blocks = (
        PracticeBlock("breathing and long tones", warmup, "Warm the body and establish a relaxed sound", "easy"),
        PracticeBlock("slide technique and articulation", technique, f"Develop clean {focus} coordination", "moderate"),
        PracticeBlock("repertoire", repertoire, "Apply the skill to a musical passage", "moderate"),
        PracticeBlock("cool-down and notes", reflection, "Record one observation and finish comfortably", "easy"),
    )
    return PracticePlan(
        instrument="trombone",
        duration_minutes=sum(block.minutes for block in blocks),
        blocks=blocks,
        generated_on=(today or date.today()).isoformat(),
    )


def find_repertoire(
    catalog: Iterable[RepertoireItem],
    *,
    level: str | None = None,
    skill: str | None = None,
    style: str | None = None,
) -> list[RepertoireItem]:
    """Filter repertoire metadata without copying or distributing protected scores."""

    return [
        item
        for item in catalog
        if (level is None or item.level.casefold() == level.casefold())
        and (skill is None or skill.casefold() in {value.casefold() for value in item.skills})
        and (style is None or style.casefold() in {value.casefold() for value in item.styles})
    ]


def summarize_practice(sessions: Iterable[dict[str, object]]) -> dict[str, object]:
    """Summarize logged practice sessions with transparent arithmetic."""

    rows = list(sessions)
    if not rows:
        return {"sessions": 0, "minutes": 0, "average_minutes": 0.0, "focus_minutes": {}}
    minutes = 0
    focus_minutes: dict[str, int] = {}
    for row in rows:
        value = row.get("minutes")
        focus = row.get("focus")
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Each practice session needs positive numeric minutes")
        if not isinstance(focus, str) or not focus.strip():
            raise ValueError("Each practice session needs a focus")
        minutes += value
        focus_minutes[focus] = focus_minutes.get(focus, 0) + value
    return {
        "sessions": len(rows),
        "minutes": minutes,
        "average_minutes": minutes / len(rows),
        "focus_minutes": focus_minutes,
    }
