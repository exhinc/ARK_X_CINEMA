"""Safe, testable stage execution wrapper for ARK X Cinema.

This module does not replace the existing orchestrator. It provides a small
execution boundary that records stage state before/after work and supports
resume decisions without re-running completed stages.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any

from stage_state import STAGES, StageState, StageStateError, load_state, mark_complete, mark_failed, mark_running


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
    """Execute one stage exactly once unless it has not completed.

    A callable is never invoked when the requested stage is already complete.
    Failures are persisted and re-raised so callers cannot mistake them for
    successful processing.
    """
    state = load_state(root, movie_id)
    if stage not in STAGES:
        raise StageStateError(f"Unknown stage: {stage}")
    if stage in state.completed:
        return StageResult(movie_id, stage, "skipped", artifact=artifact)

    mark_running(root, movie_id, stage)
    try:
        result = work()
    except Exception as exc:
        mark_failed(root, movie_id, stage, str(exc) or exc.__class__.__name__)
        return StageResult(movie_id, stage, "failed", error=str(exc) or exc.__class__.__name__)

    mark_complete(root, movie_id, stage, artifact=artifact)
    return StageResult(movie_id, stage, "complete", artifact=artifact)
