"""Tests for resumable stage-state policy."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import pytest
from checkpoint import Checkpoint, save_checkpoint
from stage_state import StageStateError, load_state, mark_complete, mark_failed, mark_running


def _artifact(root, relative="Workspace/movie-001/output.txt"):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("valid artifact", encoding="utf-8")
    return relative


def test_new_movie_has_no_completed_stages(tmp_path):
    assert load_state(tmp_path, "movie-001").completed == ()


def test_stages_must_follow_pipeline_order(tmp_path):
    with pytest.raises(StageStateError):
        mark_running(tmp_path, "movie-001", "intelligence")
    mark_running(tmp_path, "movie-001", "ingestion")
    artifact = _artifact(tmp_path)
    mark_complete(tmp_path, "movie-001", "ingestion", artifact)
    mark_running(tmp_path, "movie-001", "transcription")


def test_completed_stage_requires_a_real_artifact(tmp_path):
    mark_running(tmp_path, "movie-001", "ingestion")
    with pytest.raises(StageStateError):
        mark_complete(tmp_path, "movie-001", "ingestion", "missing.txt")


def test_completed_artifact_tampering_invalidates_resume(tmp_path):
    mark_running(tmp_path, "movie-001", "ingestion")
    artifact = _artifact(tmp_path)
    mark_complete(tmp_path, "movie-001", "ingestion", artifact)
    (tmp_path / artifact).write_text("tampered", encoding="utf-8")
    with pytest.raises(StageStateError, match="missing or invalid"):
        load_state(tmp_path, "movie-001")


def test_failure_is_recorded_for_resume(tmp_path):
    mark_running(tmp_path, "movie-001", "ingestion")
    mark_failed(tmp_path, "movie-001", "ingestion", "input missing")
    state = load_state(tmp_path, "movie-001")
    assert state.failed == "ingestion"
    assert state.completed == ()
