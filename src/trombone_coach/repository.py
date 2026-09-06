"""Persistence boundary for session history.

SQLite is the zero-configuration development default. Production deployments
can provide a PostgreSQL-backed implementation behind this same interface.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import SessionRecord


class SessionRepository:
    def __init__(self, database_path: str = "data/trombone_coach.db") -> None:
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(database_path) as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS sessions "
                "(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, filename TEXT NOT NULL, "
                "title TEXT NOT NULL, focus TEXT NOT NULL, notes TEXT NOT NULL, report_json TEXT NOT NULL)"
            )

    def save(self, session: SessionRecord) -> SessionRecord:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    session.id,
                    session.created_at.isoformat(),
                    session.filename,
                    session.title,
                    session.focus,
                    session.notes,
                    session.report.model_dump_json(),
                ),
            )
        return session

    def list(self, limit: int = 50) -> list[SessionRecord]:
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                "SELECT id, created_at, filename, title, focus, notes, report_json "
                "FROM sessions ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            SessionRecord(
                id=row[0],
                created_at=row[1],
                filename=row[2],
                title=row[3],
                focus=row[4],
                notes=row[5],
                report=json.loads(row[6]),
            )
            for row in rows
        ]
