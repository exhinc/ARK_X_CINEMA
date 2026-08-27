"""Canonical movie timeline/scene segmentation.

This stage does not attempt semantic scene understanding. It creates a stable
cue-based timeline from the movie subtitle track and/or AD SRT so downstream
analysis can address exact source intervals without rereading the movie.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

TIMESTAMP = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})")


def timestamp_ms(value: str) -> int:
    h, m, rest = value.split(":")
    s, ms = rest.split(",")
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)


def parse_srt(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    cues: list[dict[str, Any]] = []
    for block in re.split(r"\n\s*\n", text):
        lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
        if len(lines) < 3 or not lines[0].isdigit():
            continue
        match = TIMESTAMP.match(lines[1])
        if not match:
            continue
        start, end = match.groups()
        cues.append({"index": int(lines[0]), "start": start, "end": end, "start_ms": timestamp_ms(start), "end_ms": timestamp_ms(end), "text": " ".join(lines[2:])})
    return cues


def _gap_is_boundary(previous_end: int, next_start: int, boundary_ms: int) -> bool:
    return next_start - previous_end >= boundary_ms


def build_timeline(movie_id: str, subtitle_srt: Path | None = None, ad_srt: Path | None = None, boundary_ms: int = 5000) -> dict[str, Any]:
    """Create deterministic timeline intervals from available timed text."""
    if not subtitle_srt and not ad_srt:
        raise ValueError("At least one timed source is required")
    subtitle_cues = parse_srt(subtitle_srt) if subtitle_srt else []
    ad_cues = parse_srt(ad_srt) if ad_srt else []
    all_cues = [("subtitle", cue) for cue in subtitle_cues] + [("ad", cue) for cue in ad_cues]
    all_cues.sort(key=lambda item: (item[1]["start_ms"], item[1]["end_ms"], item[0], item[1]["index"]))
    scenes: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for source, cue in all_cues:
        if current is None or _gap_is_boundary(current["end_ms"], cue["start_ms"], boundary_ms):
            current = {
                "scene_id": f"{movie_id}_scene_{len(scenes) + 1:04d}",
                "start_ms": cue["start_ms"],
                "end_ms": cue["end_ms"],
                "sources": [],
                "cues": [],
            }
            scenes.append(current)
        current["end_ms"] = max(current["end_ms"], cue["end_ms"])
        current["sources"].append(source)
        current["cues"].append({"source": source, **cue})

    for scene in scenes:
        scene["start"] = _format_ms(scene["start_ms"])
        scene["end"] = _format_ms(scene["end_ms"])
        scene["duration_ms"] = scene["end_ms"] - scene["start_ms"]
        scene["sources"] = sorted(set(scene["sources"]))

    return {"schema_version": 1, "movie_id": movie_id, "boundary_ms": boundary_ms, "subtitle_cue_count": len(subtitle_cues), "ad_cue_count": len(ad_cues), "scene_count": len(scenes), "scenes": scenes}


def _format_ms(value: int) -> str:
    ms = value % 1000
    total = value // 1000
    s = total % 60
    total //= 60
    m = total % 60
    h = total // 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_timeline(data: dict[str, Any], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return destination
