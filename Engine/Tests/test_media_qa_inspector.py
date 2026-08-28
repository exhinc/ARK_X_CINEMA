"""Tests for deterministic final-media inspection."""

from pathlib import Path
import json
import sys

import pytest

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from media_qa_inspector import inspect_video  # noqa: E402


def test_missing_video_fails_closed(tmp_path):
    report = inspect_video(tmp_path / "missing.mp4")
    assert report["valid"] is False


def test_inspector_parses_video_audio_and_subtitle_streams(tmp_path, monkeypatch):
    video = tmp_path / "final.mp4"
    video.write_bytes(b"video")

    class Result:
        returncode = 0
        stdout = json.dumps({
            "streams": [
                {"codec_type": "video"},
                {"codec_type": "audio"},
                {"codec_type": "subtitle"},
            ],
            "format": {"duration": "12.5"},
        })
        stderr = ""

    monkeypatch.setattr("media_qa_inspector.subprocess.run", lambda *args, **kwargs: Result())
    report = inspect_video(video)
    assert report["valid"] is True
    assert report["duration_seconds"] == 12.5
    assert report["has_subtitles"] is True


def test_inspector_rejects_media_without_subtitles(tmp_path, monkeypatch):
    video = tmp_path / "final.mp4"
    video.write_bytes(b"video")

    class Result:
        returncode = 0
        stdout = json.dumps({
            "streams": [
                {"codec_type": "video"},
                {"codec_type": "audio"},
            ],
            "format": {"duration": "12.5"},
        })
        stderr = ""

    monkeypatch.setattr("media_qa_inspector.subprocess.run", lambda *args, **kwargs: Result())
    report = inspect_video(video)
    assert report["valid"] is False
    assert report["has_subtitles"] is False
