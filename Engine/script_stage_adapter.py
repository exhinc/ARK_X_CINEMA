"""Resumable, evidence-grounded recap script stage.

This stage converts validated scene intelligence into an original recap-script
input contract. It does not call an LLM itself; the generation callable is
injected so CI can test the stage without Ollama.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from orchestrator_stage_adapter import StageBinding, run_bound_stage


class ScriptStageError(ValueError):
    """Raised when intelligence is unsuitable for script generation."""


def _validate_intelligence(items: list[dict[str, Any]]) -> None:
    if not items:
        raise ScriptStageError("No intelligence records supplied")
    for item in items:
        intelligence = item.get("intelligence")
        if not isinstance(intelligence, dict):
            raise ScriptStageError("Each intelligence record must contain an object")
        if not isinstance(intelligence.get("unsupported_claims"), list):
            raise ScriptStageError("Intelligence must expose unsupported_claims")


def run_script_stage(
    root: Path,
    movie_id: str,
    intelligence: list[dict[str, Any]],
    generate: Callable[[list[dict[str, Any]]], str],
) -> str:
    """Generate and persist a recap script from validated intelligence."""
    _validate_intelligence(intelligence)
    artifact = Path("script") / "recap.txt"
    destination = root / artifact

    def work() -> None:
        script = generate(intelligence)
        if not isinstance(script, str) or not script.strip():
            raise ScriptStageError("Script generator returned empty output")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(script.strip() + "\n", encoding="utf-8")

    run_bound_stage(root, movie_id, StageBinding("script", artifact.as_posix(), work))
    return destination.read_text(encoding="utf-8")
