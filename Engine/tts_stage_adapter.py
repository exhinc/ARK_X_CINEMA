"""Resumable TTS stage boundary for ARK X Cinema.

The actual TTS engine is injected so the orchestration contract can be tested
without installing a voice model in CI. Production can supply Piper, Kokoro,
or another approved local engine without changing checkpoint behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from orchestrator_stage_adapter import run_existing_stage


class TTSStageError(ValueError):
    """Raised when TTS input or output is invalid."""


def run_tts_stage(
    root: Path,
    movie_id: str,
    script: str,
    synthesize: Callable[[str, Path], None],
) -> Path:
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

    run_existing_stage(root, movie_id, "tts", work, artifact=artifact.as_posix())
    return destination
