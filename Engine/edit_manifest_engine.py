"""Deterministic mapping from recap segments to source-video clip ranges."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EditManifestError(ValueError):
    """Raised when recap timing cannot be mapped safely to source scenes."""


def _seconds(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    parts = text.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return float(h) * 3600 + float(m) * 60 + float(s)
    if len(parts) == 2:
        m, s = parts
        return float(m) * 60 + float(s)
    raise EditManifestError(f"Invalid timestamp: {value}")


def _scene_index(timeline: dict[str, Any]) -> dict[str, tuple[float, float]]:
    result: dict[str, tuple[float, float]] = {}
    for scene in timeline.get("scenes", []):
        scene_id = str(scene.get("scene_id", "")).strip()
        if not scene_id:
            continue
        try:
            start = _seconds(scene["start"])
            end = _seconds(scene["end"])
        except (KeyError, TypeError, ValueError) as exc:
            raise EditManifestError(f"Timeline scene has invalid timing: {scene_id}") from exc
        if end < start:
            raise EditManifestError(f"Timeline scene is reversed: {scene_id}")
        result[scene_id] = (start, end)
    return result


def build_edit_manifest(
    segments: list[dict[str, Any]],
    timeline: dict[str, Any],
    movie_duration_seconds: float,
    *,
    max_clip_seconds: float = 20.0,
    padding_before_seconds: float = 1.0,
    padding_after_seconds: float = 1.0,
) -> dict[str, Any]:
    """Map every narrated segment to a bounded source clip range."""
    if movie_duration_seconds <= 0:
        raise EditManifestError("Movie duration must be positive")
    if max_clip_seconds <= 0 or padding_before_seconds < 0 or padding_after_seconds < 0:
        raise EditManifestError("Clip limits and padding must be non-negative and usable")

    scenes = _scene_index(timeline)
    if not scenes:
        raise EditManifestError("Timeline contains no scenes")
    if not segments:
        raise EditManifestError("No recap segments supplied")

    edits: list[dict[str, Any]] = []
    for index, segment in enumerate(segments, start=1):
        scene_id = str(segment.get("scene_id", "")).strip()
        timestamp = str(segment.get("timestamp", "")).strip()
        text = str(segment.get("text", "")).strip()
        if not scene_id or not timestamp or not text:
            raise EditManifestError(f"Recap segment {index} is incomplete")
        if scene_id not in scenes:
            raise EditManifestError(f"Recap segment {index} references unknown scene: {scene_id}")
        point = _seconds(timestamp)
        scene_start, scene_end = scenes[scene_id]
        if point < scene_start or point > scene_end:
            raise EditManifestError(f"Recap segment {index} timestamp is outside scene: {scene_id}")

        start = max(scene_start, point - padding_before_seconds)
        end = min(scene_end, point + padding_after_seconds)
        if end <= start:
            start = max(0.0, min(point, movie_duration_seconds - 0.01))
            end = min(movie_duration_seconds, start + 0.01)
        if end - start > max_clip_seconds:
            center = point
            start = max(scene_start, center - max_clip_seconds / 2)
            end = min(scene_end, start + max_clip_seconds)
            start = max(scene_start, end - max_clip_seconds)
        edits.append({
            "edit_index": index,
            "scene_id": scene_id,
            "timestamp": timestamp,
            "text": text,
            "source_start_seconds": round(start, 3),
            "source_end_seconds": round(end, 3),
        })

    return {
        "schema_version": 1,
        "movie_duration_seconds": movie_duration_seconds,
        "edits": edits,
    }


def write_edit_manifest(manifest: dict[str, Any], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination
