"""Resumable TTS stage boundary for ARK X Cinema."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from orchestrator_stage_adapter import StageBinding, run_bound_stage
from resumable_orchestrator import StageResult


class TTSStageError(ValueError):
    """Raised when TTS input or output is invalid."""


def run_tts_stage(root: Path, movie_id: str, script: str, synthesize: Callable[[str, Path], None]) -> Path:
    """Synthesize narration into a single audio artifact and checkpoint it."""
    if not isinstance(script, str) or not script.strip():
        raise TTSStageError("Script must contain non-empty text")

    artifact = Path("audio") / "narration.wav"
    destination = root / artifact

    def work() -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        synthesize(script.strip(), destination)
        if not destination.is_file() or destination.stat().st_size == 0:
            raise TTSStageError("TTS engine produced no audio artifact")

    result: StageResult = run_bound_stage(
        root, movie_id, StageBinding("tts", artifact.as_posix(), work)
    )
    if result.status == "failed":
        raise TTSStageError(result.error or "TTS stage failed")
    if not destination.is_file() or destination.stat().st_size == 0:
        raise TTSStageError("TTS stage completed without a valid artifact")
    return destination
