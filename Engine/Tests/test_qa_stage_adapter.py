"""Tests for the deterministic QA stage boundary."""

from pathlib import Path
import sys

import pytest

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from orchestrator_stage_adapter import StageBinding, run_bound_stage
from qa_stage_adapter import QAStageError, run_qa_stage


def _complete_prerequisites(tmp_path):
    for stage, artifact in (("ingestion", "ingestion.txt"), ("transcription", "ad.srt"), ("timeline", "timeline.json"), ("intelligence", "intelligence/intelligence.json"), ("script", "script/recap.txt"), ("tts", "audio/narration.wav"), ("video", "video/final.mp4")):
        path = tmp_path / artifact
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(stage.encode())
        run_bound_stage(tmp_path, "movie-001", StageBinding(stage, artifact, lambda: None))


def _inputs(tmp_path):
    paths = {"final_video": tmp_path / "video" / "final.mp4", "narration": tmp_path / "audio" / "narration.wav", "script": tmp_path / "script" / "recap.txt", "timeline": tmp_path / "timeline.json", "intelligence": tmp_path / "intelligence" / "intelligence.json"}
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"artifact")
    return paths


def test_qa_inspects_final_video_and_is_resumable(tmp_path):
    _complete_prerequisites(tmp_path)
    paths = _inputs(tmp_path)
    calls = []

    def inspect(video):
        calls.append(video)
        assert video == paths["final_video"]
        return {"valid": True, "duration_seconds": 600}

    first = run_qa_stage(tmp_path, "movie-001", **paths, inspect_video=inspect)
    second = run_qa_stage(tmp_path, "movie-001", **paths, inspect_video=inspect)
    assert first == second
    assert first["passed"] is True
    assert len(calls) == 1
    assert (tmp_path / "qa" / "report.json").is_file()


def test_missing_required_artifact_is_rejected(tmp_path):
    _complete_prerequisites(tmp_path)
    paths = _inputs(tmp_path)
    paths["script"].unlink()
    with pytest.raises(QAStageError):
        run_qa_stage(tmp_path, "movie-001", **paths, inspect_video=lambda _: {"valid": True})


def test_failed_video_inspection_is_rejected(tmp_path):
    _complete_prerequisites(tmp_path)
    paths = _inputs(tmp_path)
    with pytest.raises(QAStageError):
        run_qa_stage(tmp_path, "movie-001", **paths, inspect_video=lambda _: {"valid": False})
