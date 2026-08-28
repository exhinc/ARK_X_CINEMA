"""Resumable video assembly boundary for ARK X Cinema.

The actual FFmpeg invocation is injected. This keeps orchestration and
checkpoint behavior testable in CI without requiring a movie or FFmpeg.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence

from orchestrator_stage_adapter import run_existing_stage


class VideoStageError(ValueError):
    """Raised when video-stage inputs or output are invalid."""


def run_video_stage(
    root: Path,
    movie_id: str,
    source_video: Path,
    narration: Path,
    assemble: Callable[[Path, Path, Path], None],
    *,
    subtitle: Path | None = None,
) -> Path:
    """Assemble the final video and checkpoint its output."""
    source_video = Path(source_video)
    narration = Path(narration)
    if not source_video.is_file():
        raise VideoStageError(f"Source video does not exist: {source_video}")
    if not narration.is_file() or narration.stat().st_size == 0:
        raise VideoStageError(f"Narration artifact is missing or empty: {narration}")
    if subtitle is not None and not Path(subtitle).is_file():
        raise VideoStageError(f"Subtitle artifact does not exist: {subtitle}")

    artifact = Path("video") / "final.mp4"
    destination = root / artifact

    def work() -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        assemble(source_video, narration, destination)
        if not destination.is_file() or destination.stat().st_size == 0:
            raise VideoStageError("Video assembler produced no output")

    run_existing_stage(root, movie_id, "video", work, artifact=artifact.as_posix())
    return destination
