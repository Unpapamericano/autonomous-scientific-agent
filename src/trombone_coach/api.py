"""FastAPI surface for the Trombone Coach AI MVP."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .audio_engine import AudioEngine, WavAutocorrelationEngine
from .auth import AuthStore, Credentials, create_token, current_user
from .models import SessionRecord
from .repository import SessionRepository
from .knowledge import COACH_BODY


def create_app(
    engine: AudioEngine | None = None,
    repository: SessionRepository | None = None,
) -> FastAPI:
    app = FastAPI(title=COACH_BODY.name, version=COACH_BODY.version, description=COACH_BODY.mission)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("COACH_ALLOWED_ORIGINS", "http://localhost:5173").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    analyzer = engine or WavAutocorrelationEngine()
    sessions = repository or SessionRepository(os.getenv("COACH_DATABASE_PATH", "data/trombone_coach.db"))
    auth = AuthStore(os.getenv("COACH_DATABASE_PATH", "data/trombone_coach.db"))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "engine": analyzer.name, "coach_body": COACH_BODY.version}

    @app.get("/api/v1/coach/body")
    def coach_body() -> dict[str, object]:
        return {
            "name": COACH_BODY.name,
            "version": COACH_BODY.version,
            "mission": COACH_BODY.mission,
            "principles": COACH_BODY.principles,
        }

    @app.get("/api/v1/sessions", response_model=list[SessionRecord])
    def list_sessions(user: str | None = Depends(current_user)) -> list[SessionRecord]:
        return sessions.list()

    @app.post("/api/v1/auth/register", status_code=201)
    def register(credentials: Credentials) -> dict[str, str]:
        try:
            auth.register(credentials)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"message": "Account created."}

    @app.post("/api/v1/auth/login")
    def login(credentials: Credentials) -> dict[str, str]:
        if not auth.verify(credentials):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        return {"access_token": create_token(credentials.email), "token_type": "bearer"}

    @app.post("/api/v1/sessions/analyze", response_model=SessionRecord, status_code=201)
    async def analyze_session(
        audio: UploadFile = File(...),
        title: str = Form("Practice session"),
        focus: str = Form("fundamentals"),
        notes: str = Form(""),
        user: str | None = Depends(current_user),
    ) -> SessionRecord:
        if audio.content_type not in {"audio/wav", "audio/x-wav", "audio/wave", "audio/mpeg", "audio/mp3"}:
            raise HTTPException(status_code=415, detail="Upload a WAV or MP3 audio file.")
        payload = await audio.read()
        if not payload:
            raise HTTPException(status_code=400, detail="The uploaded audio file is empty.")
        if len(payload) > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Audio files must be 50 MB or smaller.")
        try:
            report = analyzer.analyze(payload, audio.filename or "practice.wav")
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        session = SessionRecord(
            id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc),
            filename=audio.filename or "practice.wav",
            title=title,
            focus=focus,
            notes=notes,
            report=report,
        )
        return sessions.save(session)

    return app


app = create_app()
