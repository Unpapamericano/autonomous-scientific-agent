"""Typed contracts for measured audio data and coach interpretation."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Measurement(BaseModel):
    value: float | None
    unit: str
    confidence: float = Field(ge=0, le=1)
    status: Literal["measured", "unavailable", "low_confidence"] = "measured"


class PitchEvent(BaseModel):
    note: str
    midi: int
    cents_deviation: float | None
    start_seconds: float
    duration_seconds: float
    confidence: float = Field(ge=0, le=1)


class EvidenceItem(BaseModel):
    """A traceable statement in the measured -> interpreted -> action chain."""

    id: str
    kind: Literal["measured", "interpreted", "recommended"]
    text: str
    source: str
    confidence: float = Field(ge=0, le=1)


class AnalysisReport(BaseModel):
    schema_version: str = "1.0"
    engine: str
    analyzed_at: datetime
    duration_seconds: Measurement
    detected_notes: list[PitchEvent]
    intonation_cents_mean_abs: Measurement
    pitch_stability: Measurement
    tempo_bpm: Measurement
    performance_score: Measurement
    range_low: str | None
    range_high: str | None
    tessitura: str | None
    measured_limitations: list[str] = Field(default_factory=list)
    interpretation: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)


class SessionCreate(BaseModel):
    title: str = Field(default="Practice session", min_length=1, max_length=120)
    focus: str = Field(default="fundamentals", min_length=1, max_length=80)
    notes: str = Field(default="", max_length=4000)


class SessionRecord(SessionCreate):
    id: str
    created_at: datetime
    filename: str
    report: AnalysisReport
