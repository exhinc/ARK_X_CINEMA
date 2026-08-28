"""Resumable adapter for the external Audio Description transcription stage.

The existing subtitle_pipeline implementation remains the execution primitive.
This adapter only supplies the stage contract and checkpoint boundary.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from resumable_orchestrator import StageResult, execute_stage
from subtitle_pipeline import transcribe_ad_to_srt


def bind_ad_transcription(
    root: Path,
    movie_id: str,
    ad_audio: Path,
    output_srt: Path,
    whisper_executable: Path,
    whisper_model: Path,
    ffmpeg_executable: str = "ffmpeg",
) -> StageResult:
    """Run AD audio -> timestamped SRT through the resumable stage boundary."""
    root = Path(root).resolve()
    output_srt = Path(output_srt).resolve()
    try:
        artifact = str(output_srt.relative_to(root))
    except ValueError as exc:
        raise ValueError("output_srt must be inside the pipeline root") from exc

    def work() -> Any:
        return transcribe_ad_to_srt(
            ad_audio=Path(ad_audio),
            output_srt=output_srt,
            whisper_executable=Path(whisper_executable),
            whisper_model=Path(whisper_model),
            ffmpeg_executable=ffmpeg_executable,
        )

    return execute_stage(
        root=root,
        movie_id=movie_id,
        stage="transcription",
        work=work,
        artifact=artifact,
    )
