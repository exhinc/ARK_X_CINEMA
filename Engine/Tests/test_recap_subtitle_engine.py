"""Tests for final recap SRT timing."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from recap_subtitle_engine import build_recap_srt  # noqa: E402


def test_build_recap_srt_accumulates_narration_durations():
    result = build_recap_srt([
        {"text": "First beat.", "duration_seconds": 1.25},
        {"text": "Second beat.", "duration_seconds": 2.5},
    ])
    assert "00:00:00,000 --> 00:00:01,250" in result
    assert "00:00:01,250 --> 00:00:03,750" in result
    assert "First beat." in result
    assert "Second beat." in result
