"""Evidence-first movie intelligence preparation for the local LLM stage.

This module deliberately does not invent plot facts. It converts the canonical
scene timeline into bounded, timestamped evidence packets. The LLM can later
summarize/classify these packets, while the source evidence remains auditable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_scene_packets(timeline: dict[str, Any], max_chars_per_packet: int = 6000) -> list[dict[str, Any]]:
    """Create bounded evidence packets, preserving scene/time/source provenance."""
    if max_chars_per_packet < 500:
        raise ValueError("max_chars_per_packet must be at least 500")
    packets: list[dict[str, Any]] = []
    for scene in timeline.get("scenes", []):
        evidence: list[dict[str, Any]] = []
        used = 0
        for cue in scene.get("cues", []):
            text = str(cue.get("text", "")).strip()
            if not text:
                continue
            item = {
                "source": cue.get("source"),
                "start": cue.get("start"),
                "end": cue.get("end"),
                "text": text,
            }
            cost = len(json.dumps(item, ensure_ascii=False))
            if evidence and used + cost > max_chars_per_packet:
                break
            evidence.append(item)
            used += cost
        packets.append({
            "schema_version": 1,
            "scene_id": scene["scene_id"],
            "start": scene["start"],
            "end": scene["end"],
            "duration_ms": scene["duration_ms"],
            "evidence": evidence,
            "evidence_characters": used,
            "sources": scene.get("sources", []),
            "llm_instruction": (
                "Use only the supplied evidence. If a fact is not supported, mark it unknown. "
                "Separate dialogue from visual/action descriptions when describing the scene."
            ),
        })
    return packets


def build_intelligence_schema() -> dict[str, Any]:
    """Return the required structured output contract for later LLM inference."""
    return {
        "schema_version": 1,
        "scene_fields": {
            "summary": "string",
            "characters": "array[string]",
            "location": "string|null",
            "actions": "array[string]",
            "dialogue_points": "array[string]",
            "visual_description_points": "array[string]",
            "cause_effect": "array[string]",
            "importance": "string",
            "confidence": "number 0..1",
            "unsupported_claims": "array[string]",
        },
        "rule": "Every claim must be traceable to the packet evidence; unsupported facts must not be presented as facts.",
    }


def write_packets(packets: list[dict[str, Any]], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(packets, indent=2, ensure_ascii=False), encoding="utf-8")
    return destination


def write_schema(destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(build_intelligence_schema(), indent=2, ensure_ascii=False), encoding="utf-8")
    return destination
