"""Dependency-light FFprobe inspector for final recap media QA."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


class MediaQAError(RuntimeError):
    """Raised when FFprobe cannot inspect final media."""


def inspect_video(path: Path, *, ffprobe: str = "ffprobe") -> dict[str, Any]:
    path = Path(path)
    if not path.is_file() or path.stat().st_size == 0:
        return {"valid": False, "error": f"Missing or empty video: {path}"}
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        return {"valid": False, "error": "ffprobe failed", "detail": (result.stderr or result.stdout).strip()}
    try:
        probe = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise MediaQAError("ffprobe returned invalid JSON") from exc
    streams = probe.get("streams", [])
    if not isinstance(streams, list):
        raise MediaQAError("ffprobe stream data must be an array")
    video = [stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "video"]
    audio = [stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "audio"]
    subtitle = [stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "subtitle"]
    try:
        duration = float((probe.get("format") or {}).get("duration", 0) or 0)
    except (TypeError, ValueError) as exc:
        raise MediaQAError("ffprobe reported an invalid media duration") from exc
    valid = bool(video) and bool(audio) and bool(subtitle) and duration > 0
    return {
        "valid": valid,
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "duration_seconds": duration,
        "video_streams": len(video),
        "audio_streams": len(audio),
        "subtitle_streams": len(subtitle),
        "has_video": bool(video),
        "has_audio": bool(audio),
        "has_subtitles": bool(subtitle),
        "probe": probe,
    }
