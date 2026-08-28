"""Resumable, evidence-grounded recap script stage."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Callable

from orchestrator_stage_adapter import StageBinding, run_bound_stage
from resumable_orchestrator import StageResult


class ScriptStageError(ValueError):
    """Raised when intelligence or generated script is invalid."""


def _validate_intelligence(items: list[dict[str, Any]]) -> None:
    if not items:
        raise ScriptStageError("No intelligence records supplied")
    for item in items:
        intelligence = item.get("intelligence")
        if not isinstance(intelligence, dict):
            raise ScriptStageError("Each intelligence record must contain an object")
        if not isinstance(intelligence.get("unsupported_claims"), list):
            raise ScriptStageError("Intelligence must expose unsupported_claims")


def _generated_text_and_metadata(generated: Any) -> tuple[str, Any | None]:
    if isinstance(generated, str):
        return generated, None
    text = getattr(generated, "text", None)
    segments = getattr(generated, "segments", None)
    if isinstance(text, str) and text.strip() and isinstance(segments, list):
        return text, segments
    raise ScriptStageError("Script generator returned an unsupported result")


def _serialize_segments(segments: list[Any]) -> list[Any]:
    serialized: list[Any] = []
    for segment in segments:
        if is_dataclass(segment):
            serialized.append(asdict(segment))
        elif isinstance(segment, dict):
            serialized.append(segment)
        else:
            try:
                serialized.append(vars(segment))
            except TypeError as exc:
                raise ScriptStageError("Recap segment metadata is not serializable") from exc
    return serialized


def run_script_stage(
    root: Path,
    movie_id: str,
    intelligence: list[dict[str, Any]],
    generate: Callable[[list[dict[str, Any]]], Any],
) -> str:
    """Generate and persist a recap script from validated intelligence.

    String-returning generators remain fully compatible. Generators that return
    an object with ``text`` and ``segments`` additionally persist
    ``script/recap_segments.json`` for downstream scene synchronization.
    """
    _validate_intelligence(intelligence)
    artifact = Path("script") / "recap.txt"
    destination = root / artifact
    segments_destination = root / "script" / "recap_segments.json"

    def work() -> None:
        generated = generate(intelligence)
        script, segments = _generated_text_and_metadata(generated)
        if not script.strip():
            raise ScriptStageError("Script generator returned empty output")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(script.strip() + "\n", encoding="utf-8")
        if segments is not None:
            segments_destination.write_text(
                json.dumps(_serialize_segments(segments), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    result: StageResult = run_bound_stage(
        root, movie_id, StageBinding("script", artifact.as_posix(), work)
    )
    if result.status == "failed":
        raise ScriptStageError(result.error or "Script stage failed")
    if not destination.is_file() or destination.stat().st_size == 0:
        raise ScriptStageError("Script stage completed without a valid artifact")
    return destination.read_text(encoding="utf-8")
