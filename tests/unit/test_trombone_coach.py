import io
import math
import struct
import wave

from src.trombone_coach.auth import AuthStore, Credentials
from src.trombone_coach.audio_engine import WavAutocorrelationEngine


def _tone_wav(frequency=440, sample_rate=16000, seconds=0.5):
    frames = b"".join(
        struct.pack("<h", int(12000 * math.sin(2 * math.pi * frequency * i / sample_rate)))
        for i in range(int(sample_rate * seconds))
    )
    output = io.BytesIO()
    with wave.open(output, "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(sample_rate)
        stream.writeframes(frames)
    return output.getvalue()


def test_mvp_engine_reports_measurements_with_confidence():
    report = WavAutocorrelationEngine().analyze(_tone_wav(), "long-tone.wav")

    assert report.engine == "wav-autocorrelation-mvp"
    assert report.duration_seconds.value == 0.5
    assert report.detected_notes
    assert report.detected_notes[0].note == "A4"
    assert report.performance_score.value is not None
    assert report.tempo_bpm.status == "unavailable"


def test_mvp_engine_rejects_non_wav_until_optional_engine_is_selected():
    try:
        WavAutocorrelationEngine().analyze(b"not audio", "practice.mp3")
    except ValueError as error:
        assert "WAV" in str(error)
    else:
        raise AssertionError("MP3 should be rejected by the WAV MVP engine")


def test_auth_store_hashes_and_verifies_passwords(tmp_path):
    store = AuthStore(str(tmp_path / "coach.db"))
    credentials = Credentials(email="player@example.com", password="secure-pass")

    store.register(credentials)

    assert store.verify(credentials)
    assert not store.verify(Credentials(email=credentials.email, password="wrong-pass"))
