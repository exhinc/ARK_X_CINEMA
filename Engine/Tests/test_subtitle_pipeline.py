"""Tests for canonical subtitle/AD ingestion."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from subtitle_pipeline import classify_external_subtitles, find_ad_audio, validate_srt  # noqa: E402


def test_valid_srt(tmp_path):
    srt = tmp_path / "ok.srt"
    srt.write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nHello.\n\n"
        "2\n00:00:03,000 --> 00:00:04,000\nWorld.\n",
        encoding="utf-8",
    )
    assert validate_srt(srt) == []


def test_invalid_overlap_and_empty_text(tmp_path):
    srt = tmp_path / "bad.srt"
    srt.write_text(
        "1\n00:00:01,000 --> 00:00:03,000\nHello.\n\n"
        "2\n00:00:02,000 --> 00:00:04,000\n\n",
        encoding="utf-8",
    )
    errors = validate_srt(srt)
    assert any("overlaps" in e for e in errors)
    assert any("empty cue text" in e for e in errors)


def test_subtitle_candidates_are_deterministic(tmp_path):
    files = [tmp_path / "movie.eng.srt", tmp_path / "other.srt", tmp_path / "movie.srt"]
    result = classify_external_subtitles(files, "movie")
    assert result[0].name == "movie.srt"


def test_ad_audio_detection_excludes_srt(tmp_path):
    ad = tmp_path / "movie_AD.mp3"
    subtitle = tmp_path / "movie_AD.srt"
    other = tmp_path / "movie.mp3"
    assert find_ad_audio([ad, subtitle, other]) == [ad]
