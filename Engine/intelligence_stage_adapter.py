"""Resumable adapter for the evidence-first Ollama intelligence stage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from movie_intelligence import build_scene_packets
from ollama_intelligence import OllamaResult, infer_scene
from orchestrator_stage_adapter import StageBinding, run_bound_stage
from resumable_orchestrator import StageResult


class IntelligenceStageError(RuntimeError):
    """Raised when the intelligence stage cannot produce a completed artifact."""


def run_intelligence_stage(
    root: Path,
    movie_id: str,
    timeline: dict[str, Any],
    model: str,
    *,
    base_url: str = "http://127.0.0.1:11434/api/generate",
    infer: Callable[..., OllamaResult] = infer_scene,
    max_chars_per_packet: int = 6000,
) -> list[dict[str, Any]]:
    """Run bounded evidence packets through Ollama and persist intelligence JSON."""
    packets = build_scene_packets(timeline, max_chars_per_packet=max_chars_per_packet)
    artifact = Path("intelligence") / "intelligence.json"
    destination = root / artifact

    def work() -> None:
        results: list[dict[str, Any]] = []
        for packet in packets:
            result = infer(packet, model=model, base_url=base_url)
            results.append({
                "packet_id": packet["packet_id"],
                "scene_id": packet["scene_id"],
                "start": packet["start"],
                "end": packet["end"],
                "model": result.model,
                "duration_ms": result.duration_ms,
                "intelligence": result.parsed,
            })
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    result: StageResult = run_bound_stage(
        root, movie_id, StageBinding("intelligence", artifact.as_posix(), work)
    )
    if result.status == "failed":
        raise IntelligenceStageError(result.error or "Intelligence stage failed")
    if not destination.is_file() or destination.stat().st_size == 0:
        raise IntelligenceStageError("Intelligence stage completed without a valid artifact")
    return json.loads(destination.read_text(encoding="utf-8"))
