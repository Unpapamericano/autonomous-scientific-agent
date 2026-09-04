"""Small, searchable notes that preserve research context across sessions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import re


@dataclass(frozen=True)
class ContextNote:
    """A durable observation, decision, or unresolved question."""

    note_id: str
    text: str
    category: str = "observation"
    created_at: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


class ContextNoteStore:
    """JSONL-backed note store with deterministic case-insensitive search."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def add(self, note: ContextNote) -> None:
        if not note.note_id.strip() or not note.text.strip():
            raise ValueError("Context notes require a non-empty ID and text")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = note
        if not note.created_at:
            payload = ContextNote(
                note.note_id,
                note.text,
                note.category,
                datetime.now(timezone.utc).isoformat(),
            )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload.to_dict(), ensure_ascii=True) + "\n")

    def search(self, query: str, *, limit: int = 20) -> list[ContextNote]:
        if limit < 1:
            raise ValueError("Search limit must be positive")
        terms = re.findall(r"\w+", query.casefold())
        if not terms or not self.path.exists():
            return []
        matches: list[ContextNote] = []
        with self.path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                note = ContextNote(**json.loads(line))
                haystack = f"{note.text} {note.category}".casefold()
                if all(term in haystack for term in terms):
                    matches.append(note)
        return matches[-limit:][::-1]
