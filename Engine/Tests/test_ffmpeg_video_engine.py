"""Tests for FFmpeg recap assembly without invoking a real encoder."""

from pathlib import Path
import json
import sys

import pytest

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import ffmpeg_video_engine as fve  # noqa: E402


def test_assemble_recap_requires_all_inputs(tmp_path):
    with pytest.raises(fve.FFmpegVideoError, match="source video"):
        fve.assemble_recap(
            tmp_path / "movie.mp4",
            tmp_path / "narration.wav",
            tmp_path / "edit.json",
            tmp_path / "recap.srt",
            tmp_path / "final.mp4",
        )


def test_assemble_recap_runs_cut_concat_and_mux_in_order(tmp_path, monkeypatch):
    source = tmp_path / "movie.mp4"; source.write_bytes(b"movie")
    narration = tmp_path / "narration.wav"; narration.write_bytes(b"audio")
    subtitle = tmp_path / "recap.srt"; subtitle.write_text("1\n00:00:00,000 --> 00:00:01,000\nHello.\n", encoding="utf-8")
    manifest = tmp_path / "edit.json"
    manifest.write_text(json.dumps({"edits": [{"edit_index": 1, "source_start_seconds": 0, "source_end_seconds": 2}]}), encoding="utf-8")
    destination = tmp_path / "final.mp4"
    calls = []

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command):
        calls.append(command)
        output = Path(command[-1])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"encoded")
        return Result()

    monkeypatch.setattr(fve, "_run", fake_run)
    result = fve.assemble_recap(source, narration, manifest, subtitle, destination)
    assert result == destination
    assert destination.read_bytes() == b"encoded"
    assert len(calls) == 3
