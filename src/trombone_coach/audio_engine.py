"""Replaceable audio-analysis engines.

The MVP engine is intentionally conservative: it analyzes PCM WAV files with
an autocorrelation estimator and reports confidence/limitations instead of
inventing precision. A librosa/pYIN engine can implement the same protocol
without changing the API or persistence layer.
"""

from __future__ import annotations

import io
import math
import struct
import wave
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from .models import AnalysisReport, Measurement, PitchEvent

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


class AudioEngine(ABC):
    """Contract for synchronous/offline performance analyzers."""

    name = "abstract"

    @abstractmethod
    def analyze(self, payload: bytes, filename: str) -> AnalysisReport:
        raise NotImplementedError


def _midi_to_note(midi: int) -> str:
    octave = midi // 12 - 1
    return f"{NOTE_NAMES[midi % 12]}{octave}"


def _frequency_to_midi(frequency: float) -> float:
    return 69 + 12 * math.log2(frequency / 440)


class WavAutocorrelationEngine(AudioEngine):
    """Dependency-light baseline for mono/stereo PCM WAV recordings."""

    name = "wav-autocorrelation-mvp"

    def analyze(self, payload: bytes, filename: str) -> AnalysisReport:
        if not filename.lower().endswith(".wav"):
            raise ValueError("The MVP analyzer accepts WAV audio. MP3 support requires the optional librosa engine.")
        try:
            with wave.open(io.BytesIO(payload), "rb") as source:
                channels = source.getnchannels()
                sample_width = source.getsampwidth()
                sample_rate = source.getframerate()
                frame_count = source.getnframes()
                raw = source.readframes(frame_count)
        except (wave.Error, EOFError) as exc:
            raise ValueError("The uploaded file is not a readable PCM WAV recording.") from exc
        if sample_width != 2 or sample_rate < 8000 or frame_count == 0:
            raise ValueError("Use a non-empty 16-bit PCM WAV recording at 8 kHz or higher.")

        samples = self._mono_samples(raw, channels)
        duration = len(samples) / sample_rate
        window_size = min(len(samples), max(2048, sample_rate // 2))
        window = samples[:window_size]
        frequency, confidence = self._estimate_frequency(window, sample_rate)
        limitations: list[str] = []
        if confidence < 0.75:
            limitations.append("The recording did not provide enough harmonic confidence for precise pitch cents.")
        if channels > 1:
            limitations.append("Stereo input was downmixed to mono for the MVP estimate.")
        if not frequency:
            limitations.append("No stable fundamental was detected in the analyzed window.")

        if frequency:
            midi_float = _frequency_to_midi(frequency)
            midi = round(midi_float)
            cents = (midi_float - midi) * 100
            event = PitchEvent(
                note=_midi_to_note(midi),
                midi=midi,
                cents_deviation=round(cents, 1) if confidence >= 0.75 else None,
                start_seconds=0,
                duration_seconds=round(duration, 3),
                confidence=round(confidence, 3),
            )
            range_low = range_high = event.note
            intonation = Measurement(
                value=round(abs(cents), 1) if confidence >= 0.75 else None,
                unit="cents absolute deviation",
                confidence=confidence,
                status="measured" if confidence >= 0.75 else "low_confidence",
            )
            stability = Measurement(
                value=round(max(0.0, min(100.0, confidence * 100)), 1),
                unit="percent",
                confidence=confidence,
                status="measured" if confidence >= 0.75 else "low_confidence",
            )
            interpretation = [
                f"{event.note}: {event.cents_deviation:+.1f} cents from equal temperament."
                if event.cents_deviation is not None
                else f"{event.note}: pitch detected, but cents are withheld because confidence is low."
            ]
            recommendations = [f"Practice {event.note} long tones for 5 minutes at a comfortable tempo."]
        else:
            event = None
            range_low = range_high = None
            intonation = Measurement(value=None, unit="cents absolute deviation", confidence=confidence, status="unavailable")
            stability = Measurement(value=None, unit="percent", confidence=confidence, status="unavailable")
            interpretation = ["The coach cannot interpret pitch from this recording yet."]
            recommendations = ["Record a closer, sustained note with less background noise."]

        score_value = round(max(0.0, min(100.0, confidence * 100)), 1) if frequency else None
        score = Measurement(
            value=score_value,
            unit="score out of 100",
            confidence=confidence,
            status="measured" if score_value is not None and confidence >= 0.75 else "low_confidence",
        )
        return AnalysisReport(
            engine=self.name,
            analyzed_at=datetime.now(timezone.utc),
            duration_seconds=Measurement(value=round(duration, 3), unit="seconds", confidence=1),
            detected_notes=[event] if event else [],
            intonation_cents_mean_abs=intonation,
            pitch_stability=stability,
            tempo_bpm=Measurement(value=None, unit="beats per minute", confidence=0, status="unavailable"),
            performance_score=score,
            range_low=range_low,
            range_high=range_high,
            tessitura=range_low,
            measured_limitations=limitations + [
                "MVP engine currently measures a representative sustained window; rhythm, dynamics, articulation, vibrato, MIDI comparison, and full tessitura require the advanced engine."
            ],
            interpretation=interpretation,
            recommendations=recommendations,
        )

    @staticmethod
    def _mono_samples(raw: bytes, channels: int) -> list[float]:
        values = struct.unpack("<" + "h" * (len(raw) // 2), raw)
        if channels == 1:
            return [value / 32768 for value in values]
        return [
            sum(values[index : index + channels]) / channels / 32768
            for index in range(0, len(values), channels)
        ]

    @staticmethod
    def _estimate_frequency(samples: list[float], sample_rate: int) -> tuple[float | None, float]:
        if not samples:
            return None, 0
        rms = math.sqrt(sum(value * value for value in samples) / len(samples))
        if rms < 0.005:
            return None, 0
        min_lag = max(2, int(sample_rate / 1000))
        max_lag = min(len(samples) // 2, int(sample_rate / 50))
        correlations = [
            sum(samples[index] * samples[index + lag] for index in range(len(samples) - lag))
            for lag in range(min_lag, max_lag)
        ]
        if not correlations:
            return None, 0
        peak_index = max(range(len(correlations)), key=correlations.__getitem__)
        lag = peak_index + min_lag
        peak = correlations[peak_index]
        energy = sum(value * value for value in samples)
        confidence = max(0.0, min(1.0, peak / energy if energy else 0))
        return (sample_rate / lag if confidence > 0.15 else None), confidence
