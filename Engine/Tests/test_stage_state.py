"""Tests for resumable stage-state policy."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import pytest
from stage_state import StageStateError, load_state, mark_complete, mark_failed, mark_running


def test_new_movie_has_no_completed_stages(tmp_path):
    assert load_state(tmp_path, "movie-001").completed == ()


def test_stages_must_follow_pipeline_order(tmp_path):
    with pytest.raises(StageStateError):
        mark_running(tmp_path, "movie-001", "intelligence")

    mark_running(tmp_path, "movie-001", "ingestion")
    mark_complete(tmp_path, "movie-001", "ingestion", "Workspace/movie-001")
    mark_running(tmp_path, "movie-001", "transcription")


def test_failure_is_recorded_for_resume(tmp_path):
    mark_running(tmp_path, "movie-001", "ingestion")
    mark_failed(tmp_path, "movie-001", "ingestion", "input missing")
    state = load_state(tmp_path, "movie-001")
    assert state.failed == "ingestion"
    assert state.completed == ()
