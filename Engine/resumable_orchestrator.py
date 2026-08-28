"""Safe, testable stage execution wrapper for ARK X Cinema.

This module does not replace the existing orchestrator. It provides a small
execution boundary that records stage state before/after work and supports
resume decisions without re-running completed stages.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any

from stage_state import STAGES, StageStateError, load_state, mark_complete, mark_failed, mark_running


@dataclass(frozen=True)
class StageResult:
    movie_id: str
    stage: str
    status: str
    artifact: str | None = None
    error: str | None = None


def execute_stage(
    root: Path,
    movie_id: str,
    stage: str,
    work: Callable[[], Any],
    artifact: str | None = None,
) -> StageResult:
    """Execute a stage once unless a valid completed checkpoint exists.

    A callable is never invoked when the requested stage is already complete.
    Exceptions raised by the stage work are persisted as a failed checkpoint
    and returned as a ``StageResult``; transition/configuration errors remain
    exceptions so callers cannot confuse an invalid pipeline state with a
    stage failure.
    """
    state = load_state(root, movie_id)
    if stage not in STAGES:
        raise StageStateError(f"Unknown stage: {stage}")
    if stage in state.completed:
        return StageResult(movie_id, stage, "skipped", artifact=artifact)

    mark_running(root, movie_id, stage)
    try:
        work()
    except Exception as exc:
        message = str(exc) or exc.__class__.__name__
        mark_failed(root, movie_id, stage, message)
        return StageResult(movie_id, stage, "failed", error=message)

    mark_complete(root, movie_id, stage, artifact=artifact)
    return StageResult(movie_id, stage, "complete", artifact=artifact)
