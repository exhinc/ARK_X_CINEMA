"""Evidence-to-Ollama integration for ARK X Cinema.

This module connects the bounded evidence packet stage to the optional local
Ollama adapter without making Ollama a dependency of the core engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from movie_intelligence import build_scene_packets, build_intelligence_schema
from ollama_intelligence import OllamaError, infer_scene


def analyze_timeline(
    timeline: dict[str, Any],
    model: str,
    base_url: str = "http://127.0.0.1:11434/api/generate",
    timeout_seconds: int = 120,
    max_chars_per_packet: int = 6000,
    infer: Callable[..., Any] = infer_scene,
) -> dict[str, Any]:
    """Analyze every bounded evidence packet and return a resumable artifact.

    A failed packet stops the stage with an explicit error; partial results are
    retained in memory and can be written by the caller if desired.
    """
    packets = build_scene_packets(timeline, max_chars_per_packet=max_chars_per_packet)
    results: list[dict[str, Any]] = []
    for packet in packets:
        try:
            result = infer(packet, model=model, base_url=base_url, timeout_seconds=timeout_seconds)
        except OllamaError as exc:
            return {
                "schema_version": 1,
                "status": "failed",
                "model": model,
                "processed_packets": len(results),
                "total_packets": len(packets),
                "error": str(exc),
                "results": results,
            }
        results.append({
            "packet_id": packet["packet_id"],
            "scene_id": packet["scene_id"],
            "start": packet["start"],
            "end": packet["end"],
            "intelligence": result.parsed,
            "duration_ms": result.duration_ms,
        })
    return {
        "schema_version": 1,
        "status": "complete",
        "model": model,
        "processed_packets": len(results),
        "total_packets": len(packets),
        "intelligence_schema": build_intelligence_schema(),
        "results": results,
    }


def write_intelligence_artifact(artifact: dict[str, Any], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    return destination
