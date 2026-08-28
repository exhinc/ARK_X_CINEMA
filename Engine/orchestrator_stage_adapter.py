"""Integration boundary between the legacy orchestrator and resumable stages.

This adapter deliberately does not replace or mutate the existing orchestrator.
It supplies a small, explicit bridge so orchestration can adopt checkpointing one
stage at a time without changing existing stage implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from resumable_orchestrator import StageResult, execute_stage


@dataclass(frozen=True)
class StageBinding:
    """Description of one existing stage and the artifact it must produce."""

    name: str
    artifact: str
    work: Callable[[], Any]


def run_bound_stage(root: Path, movie_id: str, binding: StageBinding) -> StageResult:
    """Run an existing stage through the resumable execution boundary."""
    return execute_stage(
        root=root,
        movie_id=movie_id,
        stage=binding.name,
        work=binding.work,
        artifact=binding.artifact,
    )


def bind_ingestion(
    root: Path,
    movie_id: str,
    workspace: Path,
    identify: Callable[[], Any],
    ingest: Callable[[Any], Any],
) -> StageResult:
    """Adapt the existing identify→ingest flow without changing its functions."""
    artifact = str((workspace / "ingestion_manifest.json").relative_to(root))

    def work() -> Any:
        manifest = identify()
        return ingest(manifest)

    return run_bound_stage(root, movie_id, StageBinding("ingestion", artifact, work))
