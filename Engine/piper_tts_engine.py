"""Low-dependency Piper TTS engine for ARK X Cinema.

Narration is synthesized one recap segment at a time so the exact audio duration
of every scripted beat is available to the editing stage. The engine itself is
not considered PC-validated until Piper is executed on the target Windows host.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


class PiperTTSError(RuntimeError):
    """Raised when Piper narration cannot be generated safely."""


def _duration_seconds(path: Path, ffprobe: str = "ffprobe") -> float:
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise PiperTTSError(f"ffprobe could not inspect narration segment: {path}")
    try:
        duration = float(result.stdout.strip())
    except ValueError as exc:
        raise PiperTTSError(f"Invalid narration duration reported for: {path}") from exc
    if duration <= 0:
        raise PiperTTSError(f"Narration segment has non-positive duration: {path}")
    return duration


def synthesize_segments(
    segments: list[dict[str, Any]],
    executable: Path,
    model: Path,
    output_wav: Path,
    metadata_path: Path,
    *,
    ffmpeg: str = "ffmpeg",
    ffprobe: str = "ffprobe",
) -> Path:
    """Synthesize recap segments with Piper and concatenate them losslessly."""
    if not executable.is_file():
        raise PiperTTSError(f"Piper executable not found: {executable}")
    if not model.is_file():
        raise PiperTTSError(f"Piper model not found: {model}")
    if not segments:
        raise PiperTTSError("No recap segments supplied to Piper")

    output_wav = Path(output_wav)
    metadata_path = Path(metadata_path)
    segment_dir = output_wav.parent / "segments"
    segment_dir.mkdir(parents=True, exist_ok=True)

    generated: list[dict[str, Any]] = []
    for index, segment in enumerate(segments, start=1):
        text = str(segment.get("text", "")).strip()
        timestamp = str(segment.get("timestamp", "")).strip()
        scene_id = str(segment.get("scene_id", "")).strip()
        if not text or not timestamp or not scene_id:
            raise PiperTTSError(f"Invalid recap segment {index}")

        destination = segment_dir / f"segment_{index:04d}.wav"
        result = subprocess.run(
            [str(executable), "--model", str(model), "--output_file", str(destination)],
            input=text,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0 or not destination.is_file() or destination.stat().st_size == 0:
            detail = (result.stderr or result.stdout or "unknown Piper error").strip()
            raise PiperTTSError(f"Piper failed for segment {index}: {detail}")
        generated.append(
            {
                "segment_index": index,
                "text": text,
                "timestamp": timestamp,
                "scene_id": scene_id,
                "audio_path": str(destination),
                "duration_seconds": _duration_seconds(destination, ffprobe=ffprobe),
            }
        )

    concat_list = segment_dir / "concat.txt"
    concat_list.write_text(
        "\n".join(f"file '{str(item['audio_path']).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for item in generated) + "\n",
        encoding="utf-8",
    )

    output_wav.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(output_wav)],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0 or not output_wav.is_file() or output_wav.stat().st_size == 0:
        detail = (result.stderr or result.stdout or "unknown FFmpeg error").strip()
        raise PiperTTSError(f"FFmpeg narration concatenation failed: {detail}")

    metadata = {
        "schema_version": 1,
        "segments": generated,
        "total_duration_seconds": sum(float(item["duration_seconds"]) for item in generated),
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_wav
