"""Tests for safe resumable stage execution."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import pytest
from resumable_orchestrator import execute_stage
from stage_state import StageStateError, load_state


def _complete_ingestion(root, movie_id="movie-001"):
    execute_stage(root, movie_id, "ingestion", lambda: None, artifact="workspace")


def test_success_is_recorded_and_work_runs_once(tmp_path):
    calls = []
    _complete_ingestion(tmp_path)
    first = execute_stage(root=tmp_path, movie_id="movie-001", stage="transcription", work=lambda: calls.append(1), artifact="ad.srt")
    second = execute_stage(root=tmp_path, movie_id="movie-001", stage="transcription", work=lambda: calls.append(2), artifact="ad.srt")
    assert first.status == "complete"
    assert second.status == "skipped"
    assert calls == [1]


def test_failure_is_persisted_and_stage_can_be_resumed(tmp_path):
    _complete_ingestion(tmp_path)
    calls = []
    failed = execute_stage(
        root=tmp_path,
        movie_id="movie-001",
        stage="transcription",
        work=lambda: (_ for _ in ()).throw(RuntimeError("whisper failed")),
    )
    assert failed.status == "failed"
    assert load_state(tmp_path, "movie-001").failed == "transcription"

    recovered = execute_stage(root=tmp_path, movie_id="movie-001", stage="transcription", work=lambda: calls.append("retry"), artifact="ad.srt")
    assert recovered.status == "complete"
    assert calls == ["retry"]
    assert load_state(tmp_path, "movie-001").failed is None


def test_later_stage_requires_prerequisite(tmp_path):
    with pytest.raises(StageStateError, match="prerequisite"):
        execute_stage(root=tmp_path, movie_id="movie-001", stage="intelligence", work=lambda: None)
