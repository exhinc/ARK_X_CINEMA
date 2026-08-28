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
    segment_durations: list[float] | None = None,
    max_clip_seconds: float = 120.0,
    padding_before_seconds: float = 1.0,
    padding_after_seconds: float = 1.0,
) -> dict[str, Any]:
    """Map every narrated segment to a bounded source clip range.

    When narration durations are supplied, each source clip is sized to cover
    the corresponding narration beat plus optional padding. Clip anchors are
    the evidence timestamps; clips may cross a scene boundary when necessary.
    """
    if movie_duration_seconds <= 0:
        raise EditManifestError("Movie duration must be positive")
    if max_clip_seconds <= 0 or padding_before_seconds < 0 or padding_after_seconds < 0:
        raise EditManifestError("Clip limits and padding must be non-negative and usable")
    if segment_durations is not None and len(segment_durations) != len(segments):
        raise EditManifestError("segment_durations must match segments length")

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

        narration_duration = None
        if segment_durations is not None:
            narration_duration = float(segment_durations[index - 1])
            if narration_duration <= 0:
                raise EditManifestError(f"Narration duration must be positive for segment {index}")

        if narration_duration is not None:
            desired = narration_duration + padding_before_seconds + padding_after_seconds
            desired = min(desired, max_clip_seconds) if desired < max_clip_seconds else desired
            start = max(0.0, point - padding_before_seconds)
            end = min(movie_duration_seconds, start + desired)
            if end - start < narration_duration:
                start = max(0.0, end - narration_duration)
        else:
            start = max(scene_start, point - padding_before_seconds)
            end = min(scene_end, point + padding_after_seconds)

        if end <= start:
            raise EditManifestError(f"Unable to create a positive clip range for segment {index}")
        edits.append({
            "edit_index": index,
            "scene_id": scene_id,
            "timestamp": timestamp,
            "text": text,
            "narration_duration_seconds": narration_duration,
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
