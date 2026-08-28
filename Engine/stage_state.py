"""Stage-state policy for resumable ARK X Cinema movie runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from checkpoint import Checkpoint, CheckpointError, load_checkpoint, save_checkpoint


STAGES = (
    "ingestion",
    "transcription",
    "timeline",
    "intelligence",
    "script",
    "tts",
    "video",
    "qa",
)


class StageStateError(ValueError):
    """Raised when a stage transition is unsafe."""


@dataclass(frozen=True)
class StageState:
    movie_id: str
    completed: tuple[str, ...]
    failed: str | None = None


def _validate_stage(stage: str) -> None:
    if stage not in STAGES:
        raise StageStateError(f"Unknown stage: {stage}")


def checkpoint_path(root: Path, movie_id: str) -> Path:
    if not movie_id.strip():
        raise StageStateError("movie_id must not be empty")
    return root / "state" / movie_id / "checkpoint.json"


def load_state(root: Path, movie_id: str) -> StageState:
    checkpoint = load_checkpoint(checkpoint_path(root, movie_id))
    if checkpoint is None:
        return StageState(movie_id=movie_id, completed=())
    if checkpoint.movie_id != movie_id:
        raise StageStateError("Checkpoint movie_id does not match requested movie")
    if checkpoint.status == "complete":
        completed = tuple(STAGES[: STAGES.index(checkpoint.stage) + 1])
        return StageState(movie_id, completed)
    return StageState(movie_id, tuple(STAGES[: STAGES.index(checkpoint.stage)]), checkpoint.stage if checkpoint.status == "failed" else None)


def mark_running(root: Path, movie_id: str, stage: str) -> StageState:
    _validate_stage(stage)
    state = load_state(root, movie_id)
    if stage in state.completed:
        raise StageStateError(f"Stage already complete: {stage}")
    index = STAGES.index(stage)
    if index and STAGES[index - 1] not in state.completed:
        raise StageStateError(f"Cannot start {stage}; prerequisite {STAGES[index - 1]} is incomplete")
    save_checkpoint(checkpoint_path(root, movie_id), Checkpoint(movie_id, stage, "running"))
    return state


def mark_complete(root: Path, movie_id: str, stage: str, artifact: str | None = None) -> StageState:
    _validate_stage(stage)
    state = load_state(root, movie_id)
    index = STAGES.index(stage)
    if index and STAGES[index - 1] not in state.completed:
        raise StageStateError(f"Cannot complete {stage}; prerequisite {STAGES[index - 1]} is incomplete")
    save_checkpoint(checkpoint_path(root, movie_id), Checkpoint(movie_id, stage, "complete", artifact=artifact))
    return load_state(root, movie_id)


def mark_failed(root: Path, movie_id: str, stage: str, error: str) -> StageState:
    _validate_stage(stage)
    if not error.strip():
        raise StageStateError("Failure reason must not be empty")
    save_checkpoint(checkpoint_path(root, movie_id), Checkpoint(movie_id, stage, "failed", error=error))
    return load_state(root, movie_id)
