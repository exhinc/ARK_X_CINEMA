"""FFmpeg-based production video assembly for ARK X Cinema."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


class FFmpegVideoError(RuntimeError):
    """Raised when clip extraction or final assembly fails."""


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def assemble_recap(
    source_video: Path,
    narration: Path,
    edit_manifest: Path,
    subtitle: Path,
    destination: Path,
    *,
    ffmpeg: str = "ffmpeg",
) -> Path:
    """Cut the selected source intervals, concatenate them, and add narration/subtitles."""
    source_video = Path(source_video)
    narration = Path(narration)
    edit_manifest = Path(edit_manifest)
    subtitle = Path(subtitle)
    destination = Path(destination)
    for path, label in ((source_video, "source video"), (narration, "narration"), (edit_manifest, "edit manifest"), (subtitle, "recap subtitle")):
        if not path.is_file() or path.stat().st_size == 0:
            raise FFmpegVideoError(f"Missing or empty {label}: {path}")

    try:
        manifest = json.loads(edit_manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FFmpegVideoError(f"Invalid edit manifest: {edit_manifest}") from exc
    edits = manifest.get("edits")
    if not isinstance(edits, list) or not edits:
        raise FFmpegVideoError("Edit manifest contains no edits")

    work_dir = destination.parent / "clips"
    work_dir.mkdir(parents=True, exist_ok=True)
    clip_paths: list[Path] = []
    for edit in edits:
        try:
            index = int(edit["edit_index"])
            start = float(edit["source_start_seconds"])
            end = float(edit["source_end_seconds"])
        except (KeyError, TypeError, ValueError) as exc:
            raise FFmpegVideoError("Edit manifest contains an invalid clip range") from exc
        if start < 0 or end <= start:
            raise FFmpegVideoError(f"Invalid clip range: {start} -> {end}")
        clip = work_dir / f"clip_{index:04d}.mp4"
        result = _run([
            ffmpeg, "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
            "-i", str(source_video), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            str(clip),
        ])
        if result.returncode != 0 or not clip.is_file() or clip.stat().st_size == 0:
            detail = (result.stderr or result.stdout or "unknown FFmpeg error").strip()
            raise FFmpegVideoError(f"FFmpeg failed cutting clip {index}: {detail}")
        clip_paths.append(clip)

    concat_list = work_dir / "concat.txt"
    concat_list.write_text(
        "\n".join(f"file '{str(path).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for path in clip_paths) + "\n",
        encoding="utf-8",
    )
    silent_video = work_dir / "silent_recap.mp4"
    result = _run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(silent_video),
    ])
    if result.returncode != 0 or not silent_video.is_file() or silent_video.stat().st_size == 0:
        detail = (result.stderr or result.stdout or "unknown FFmpeg error").strip()
        raise FFmpegVideoError(f"FFmpeg failed concatenating clips: {detail}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    result = _run([
        ffmpeg, "-y", "-i", str(silent_video), "-i", str(narration),
        "-i", str(subtitle),
        "-map", "0:v:0", "-map", "1:a:0", "-map", "2:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-c:s", "mov_text", "-shortest", str(destination),
    ])
    if result.returncode != 0 or not destination.is_file() or destination.stat().st_size == 0:
        detail = (result.stderr or result.stdout or "unknown FFmpeg error").strip()
        raise FFmpegVideoError(f"FFmpeg failed final assembly: {detail}")
    return destination
