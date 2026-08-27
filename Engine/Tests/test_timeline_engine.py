"""Tests for deterministic scene/timeline generation."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from timeline_engine import build_timeline, parse_srt  # noqa: E402


def _srt(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_srt_returns_timed_cues(tmp_path):
    path = _srt(tmp_path / "movie.srt", "1\n00:00:01,000 --> 00:00:02,000\nHello\n")
    cues = parse_srt(path)
    assert len(cues) == 1
    assert cues[0]["start_ms"] == 1000
    assert cues[0]["text"] == "Hello"


def test_timeline_merges_close_cues_and_splits_large_gaps(tmp_path):
    subtitle = _srt(tmp_path / "movie.srt", "1\n00:00:01,000 --> 00:00:02,000\nOne\n\n2\n00:00:03,000 --> 00:00:04,000\nTwo\n\n3\n00:00:12,000 --> 00:00:13,000\nThree\n")
    data = build_timeline("movie", subtitle_srt=subtitle, boundary_ms=5000)
    assert data["scene_count"] == 2
    assert data["scenes"][0]["start"] == "00:00:01,000"
    assert data["scenes"][0]["end"] == "00:00:04,000"
    assert data["scenes"][1]["start"] == "00:00:12,000"


def test_ad_and_subtitle_sources_are_preserved(tmp_path):
    subtitle = _srt(tmp_path / "movie.srt", "1\n00:00:01,000 --> 00:00:02,000\nDialogue\n")
    ad = _srt(tmp_path / "ad.srt", "1\n00:00:01,200 --> 00:00:02,000\nA man enters.\n")
    data = build_timeline("movie", subtitle_srt=subtitle, ad_srt=ad)
    assert data["subtitle_cue_count"] == 1
    assert data["ad_cue_count"] == 1
    assert set(data["scenes"][0]["sources"]) == {"subtitle", "ad"}
