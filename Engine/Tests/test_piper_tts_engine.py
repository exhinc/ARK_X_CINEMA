"""Tests for the Piper narration engine without requiring Piper locally."""

from pathlib import Path
import json
import sys

import pytest

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import piper_tts_engine as pte  # noqa: E402


def test_missing_piper_dependencies_fail_closed(tmp_path):
    with pytest.raises(pte.PiperTTSError, match="Piper executable not found"):
        pte.synthesize_segments(
            [{"text": "Hello.", "timestamp": "00:00:01", "scene_id": "s1"}],
            tmp_path / "missing.exe",
            tmp_path / "missing.onnx",
            tmp_path / "audio" / "narration.wav",
            tmp_path / "audio" / "narration_segments.json",
        )


def test_synthesize_segments_records_durations_and_metadata(tmp_path, monkeypatch):
    piper = tmp_path / "piper.exe"
    model = tmp_path / "model.onnx"
    piper.write_bytes(b"x")
    model.write_bytes(b"x")

    calls = []

    class Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(command, **kwargs):
        calls.append(command)
        if command[0] == str(piper):
            Path(command[command.index("--output_file") + 1]).write_bytes(b"wav")
        elif command[0] == "ffmpeg":
            Path(command[-1]).write_bytes(b"final")
        return Result()

    monkeypatch.setattr(pte.subprocess, "run", fake_run)
    monkeypatch.setattr(pte, "_duration_seconds", lambda path, ffprobe="ffprobe": 1.5)

    output = tmp_path / "audio" / "narration.wav"
    metadata = tmp_path / "audio" / "narration_segments.json"
    result = pte.synthesize_segments(
        [{"text": "Hello.", "timestamp": "00:00:01", "scene_id": "s1"}],
        piper,
        model,
        output,
        metadata,
    )
    assert result == output
    assert output.read_bytes() == b"final"
    data = json.loads(metadata.read_text(encoding="utf-8"))
    assert data["segments"][0]["duration_seconds"] == 1.5
    assert data["segments"][0]["scene_id"] == "s1"
