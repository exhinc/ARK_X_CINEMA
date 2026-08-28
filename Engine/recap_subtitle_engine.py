"""Create final recap SRT timing from synthesized narration segment durations."""

from __future__ import annotations

from pathlib import Path
from typing import Any


class RecapSubtitleError(ValueError):
    """Raised when narration timing cannot produce a valid SRT."""


def _format_srt_time(seconds: float) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    h, rem = divmod(total_ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_recap_srt(segment_audio: list[dict[str, Any]]) -> str:
    if not segment_audio:
        raise RecapSubtitleError("No narration segment timing supplied")

    lines: list[str] = []
    cursor = 0.0
    for index, segment in enumerate(segment_audio, start=1):
        text = str(segment.get("text", "")).strip()
        try:
            duration = float(segment["duration_seconds"])
        except (KeyError, TypeError, ValueError) as exc:
            raise RecapSubtitleError(f"Invalid narration duration for segment {index}") from exc
        if not text or duration <= 0:
            raise RecapSubtitleError(f"Invalid narration segment {index}")
        start = cursor
        end = cursor + duration
        lines.extend([
            str(index),
            f"{_format_srt_time(start)} --> {_format_srt_time(end)}",
            text,
            "",
        ])
        cursor = end
    return "\n".join(lines)


def write_recap_srt(segment_audio: list[dict[str, Any]], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_recap_srt(segment_audio), encoding="utf-8")
    return destination
