"""Evidence-first movie intelligence preparation for the local LLM stage.

This module does not invent plot facts. It converts the canonical scene timeline
into bounded, timestamped evidence packets. Oversized cues are deterministically
chunked so the packet limit is a hard upper bound.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _item(source: Any, cue: dict[str, Any], text: str) -> dict[str, Any]:
    return {"source": source, "start": cue.get("start"), "end": cue.get("end"), "text": text}


def _serialized_size(item: dict[str, Any]) -> int:
    return len(json.dumps(item, ensure_ascii=False))


def build_scene_packets(timeline: dict[str, Any], max_chars_per_packet: int = 6000) -> list[dict[str, Any]]:
    """Create bounded evidence packets, preserving scene/time/source provenance."""
    if max_chars_per_packet < 500:
        raise ValueError("max_chars_per_packet must be at least 500")
    packets: list[dict[str, Any]] = []
    for scene in timeline.get("scenes", []):
        packet_evidence: list[list[dict[str, Any]]] = [[]]
        used = 0
        for cue in scene.get("cues", []):
            text = str(cue.get("text", "")).strip()
            if not text:
                continue
            # A single cue can exceed the limit. Split its text deterministically.
            remaining = text
            while remaining:
                prefix = _item(cue.get("source"), cue, "")
                available = max_chars_per_packet - used - _serialized_size(prefix)
                if available <= 0 and packet_evidence[-1]:
                    packet_evidence.append([])
                    used = 0
                    continue
                # Conservative binary search for the largest text that fits.
                lo, hi = 1, len(remaining)
                best = 0
                while lo <= hi:
                    mid = (lo + hi) // 2
                    candidate = _item(cue.get("source"), cue, remaining[:mid])
                    if _serialized_size(candidate) <= max_chars_per_packet - used:
                        best = mid
                        lo = mid + 1
                    else:
                        hi = mid - 1
                if best == 0:
                    if packet_evidence[-1]:
                        packet_evidence.append([])
                        used = 0
                        continue
                    # max_chars_per_packet >= 500, so metadata should always fit;
                    # fail explicitly rather than violating the hard limit.
                    raise ValueError("Evidence metadata exceeds packet size limit")
                chunk = _item(cue.get("source"), cue, remaining[:best])
                packet_evidence[-1].append(chunk)
                used += _serialized_size(chunk)
                remaining = remaining[best:]
                if remaining:
                    packet_evidence.append([])
                    used = 0

        for packet_index, evidence in enumerate(packet_evidence, start=1):
            if not evidence:
                continue
            packet_id = scene["scene_id"] if len(packet_evidence) == 1 else f"{scene['scene_id']}_part_{packet_index:02d}"
            size = sum(_serialized_size(item) for item in evidence)
            packets.append({
                "schema_version": 1,
                "scene_id": scene["scene_id"],
                "packet_id": packet_id,
                "start": scene["start"],
                "end": scene["end"],
                "duration_ms": scene["duration_ms"],
                "evidence": evidence,
                "evidence_characters": size,
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
