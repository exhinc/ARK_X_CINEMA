"""Tests for safe resumable stage execution."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from resumable_orchestrator import execute_stage


def _complete_ingestion(root, movie_id="movie-001"):
    execute_stage(root, movie_id, "ingestion", lambda: None, artifact="workspace")


def test_success_is_recorded_and_work_runs_once(tmp_path):
    calls = []
    _complete_ingestion(tmp_path)
    first = execute_stage(tmp_path, "movie-001", "transcription", lambda: calls.append(1), artifact="ad.srt")
    second = execute_stage(tmp_path, "movie-001", "transcription", lambda: calls.append(2), artifact="ad.srt")
    assert first.status == "complete"
    assert second.status == "skipped"
    assert calls == [1]


def test_failure_is_persisted_and_exception_is_not_hidden(tmp_path):
    _complete_ingestion(tmp_path)
    result = execute_stage(tmp_path, "movie-001", "transcription", lambda: (_ for _ in ()).throw(RuntimeError("whisper failed")))
    assert result.status == "failed"
    assert "whisper failed" in result.error


def test_later_stage_requires_prerequisite(tmp_path):
    result = execute_stage(tmp_path, "movie-001", "intelligence", lambda: None)
    assert result.status == "failed"
    assert "prerequisite" in result.error.lower()
