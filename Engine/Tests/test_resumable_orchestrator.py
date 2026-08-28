"""Tests for safe resumable stage execution."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import pytest
from resumable_orchestrator import execute_stage
from stage_state import StageStateError, load_state


def _artifact(root, relative):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("valid artifact", encoding="utf-8")
    return relative


def _complete_ingestion(root, movie_id="movie-001"):
    artifact = _artifact(root, "Workspace/movie-001/workspace.txt")
    return execute_stage(root, movie_id, "ingestion", lambda: None, artifact=artifact)


def test_success_is_recorded_and_work_runs_once(tmp_path):
    calls = []
    _complete_ingestion(tmp_path)
    artifact = _artifact(tmp_path, "Workspace/movie-001/ad.srt")
    first = execute_stage(tmp_path, "movie-001", "transcription", lambda: calls.append(1), artifact=artifact)
    second = execute_stage(tmp_path, "movie-001", "transcription", lambda: calls.append(2), artifact=artifact)
    assert first.status == "complete"
    assert second.status == "skipped"
    assert calls == [1]


def test_failure_is_persisted_and_stage_can_be_resumed(tmp_path):
    _complete_ingestion(tmp_path)
    calls = []
    failed = execute_stage(
        tmp_path, "movie-001", "transcription",
        lambda: (_ for _ in ()).throw(RuntimeError("whisper failed")),
    )
    assert failed.status == "failed"
    state = load_state(tmp_path, "movie-001")
    assert state.failed == "transcription"
    assert state.completed == ("ingestion",)

    artifact = _artifact(tmp_path, "Workspace/movie-001/ad.srt")
    recovered = execute_stage(tmp_path, "movie-001", "transcription", lambda: calls.append("retry"), artifact=artifact)
    assert recovered.status == "complete"
    assert calls == ["retry"]
    assert load_state(tmp_path, "movie-001").completed == ("ingestion", "transcription")


def test_later_stage_requires_prerequisite(tmp_path):
    with pytest.raises(StageStateError, match="prerequisite"):
        execute_stage(tmp_path, "movie-001", "intelligence", lambda: None)


def test_completed_stage_with_deleted_artifact_cannot_be_skipped(tmp_path):
    _complete_ingestion(tmp_path)
    artifact = _artifact(tmp_path, "Workspace/movie-001/ad.srt")
    execute_stage(tmp_path, "movie-001", "transcription", lambda: None, artifact=artifact)
    (tmp_path / artifact).unlink()
    with pytest.raises(StageStateError, match="missing or invalid"):
        execute_stage(tmp_path, "movie-001", "transcription", lambda: None, artifact=artifact)
