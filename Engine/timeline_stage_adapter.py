"""Resumable adapter for canonical movie timeline generation.

The deterministic timeline engine remains the execution primitive. This adapter
adds the stage boundary, artifact checkpointing, and resume behavior without
modifying the existing orchestrator or timeline implementation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from resumable_orchestrator import StageResult, execute_stage
from timeline_engine import build_timeline, write_timeline


def bind_timeline(
    root: Path,
    movie_id: str,
    subtitle_srt: Path | None,
    ad_srt: Path | None,
    output_json: Path,
    boundary_ms: int = 5000,
) -> StageResult:
    """Build and persist the canonical timeline through the resumable boundary."""
    root = Path(root).resolve()
    output_json = Path(output_json).resolve()
    try:
        artifact = str(output_json.relative_to(root))
    except ValueError as exc:
        raise ValueError("output_json must be inside the pipeline root") from exc

    subtitle_srt = Path(subtitle_srt).resolve() if subtitle_srt else None
    ad_srt = Path(ad_srt).resolve() if ad_srt else None

    def work() -> Any:
        data = build_timeline(
            movie_id=movie_id,
            subtitle_srt=subtitle_srt,
            ad_srt=ad_srt,
            boundary_ms=boundary_ms,
        )
        return write_timeline(data, output_json)

    return execute_stage(
        root=root,
        movie_id=movie_id,
        stage="timeline",
        work=work,
        artifact=artifact,
    )
