"""ARK X Cinema production orchestrator foundation.

The orchestrator is intentionally conservative: one heavy AI stage at a time,
explicit runtime validation, and resumable project state.  Full downstream
production stages are added only after their inputs/outputs are validated.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from runtime_config import load_config, validate_runtime


ROOT = Path(__file__).resolve().parents[1]
CONFIG = load_config()

# Runtime paths come from Config/config.json / repository-relative defaults.
WHISPER = CONFIG.whisper_executable
WHISPER_MODEL = CONFIG.whisper_model
OLLAMA_URL = CONFIG.ollama_url
MODELS = {"qwen": CONFIG.ollama_model, "llama": "llama3.2:1b"}

DIRS = {
    "movies": ROOT / "Movies",
    "projects": ROOT / "Projects",
    "analysis": ROOT / "Analysis",
    "scenes": ROOT / "Scenes",
    "scripts": ROOT / "Scripts",
    "narration": ROOT / "Narration",
    "visuals": ROOT / "Visuals",
    "subtitles": ROOT / "Subtitles",
    "transcripts": ROOT / "Transcripts",
    "finished": ROOT / "Finished",
    "logs": ROOT / "Logs",
    "upload": ROOT / "Upload",
}

for directory in DIRS.values():
    directory.mkdir(parents=True, exist_ok=True)

LOG_FILE = DIRS["logs"] / "orchestrator.log"

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".ts", ".mts",
    ".m2ts", ".wmv", ".flv", ".ogv"
}
SUBTITLE_EXTENSIONS = {
    ".srt", ".vtt", ".ass", ".ssa", ".sub", ".sbv", ".dfxp", ".ttml"
}
AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma",
    ".ac3", ".eac3"
}


def log(message: str) -> None:
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run(cmd: list[Any], capture: bool = True) -> subprocess.CompletedProcess[str]:
    command = [str(item) for item in cmd]
    log("RUN: " + " ".join(command))
    result = subprocess.run(
        command,
        text=True,
        capture_output=capture,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if capture and result.stderr:
        with LOG_FILE.open("a", encoding="utf-8") as handle:
            handle.write(result.stderr[-15000:])
    return result


def safe_name(name: str) -> str:
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name).strip("_")
    return name or "Movie"


def project_state(project: Path, stage: str, status: str = "complete", details: dict[str, Any] | None = None) -> None:
    state = {
        "stage": stage,
        "status": status,
        "updated": datetime.now().isoformat(),
        "details": details or {},
    }
    (project / "pipeline_state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def ffprobe(path: Path) -> dict[str, Any]:
    result = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path])
    if result.returncode != 0:
        raise RuntimeError(f"FFprobe failed for: {path}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"FFprobe returned invalid JSON for: {path}") from exc


def discover_files(package: Path) -> dict[str, list[Path]]:
    package = Path(package)
    if not package.exists():
        raise RuntimeError(f"Movie source does not exist: {package}")
    files = [package] if package.is_file() else [p for p in package.rglob("*") if p.is_file()]
    if package.is_file() and package.suffix.lower() not in VIDEO_EXTENSIONS:
        raise RuntimeError(f"Unsupported movie format: {package.suffix}")
    return {
        "all": files,
        "videos": [p for p in files if p.suffix.lower() in VIDEO_EXTENSIONS],
        "subtitles": [p for p in files if p.suffix.lower() in SUBTITLE_EXTENSIONS],
        "audios": [p for p in files if p.suffix.lower() in AUDIO_EXTENSIONS],
    }


def filename_looks_like_ad(path: Path) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", " ", path.stem.lower()).strip()
    tokens = set(normalized.split())
    return (
        "ad" in tokens
        or "audiodescription" in tokens
        or "descriptive" in tokens
        or "audio description" in normalized
        or "descriptive audio" in normalized
    )


def inspect_media(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path)}
    probe = ffprobe(path)
    streams = probe.get("streams", [])
    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
    subtitle_streams = [s for s in streams if s.get("codec_type") == "subtitle"]
    fmt = probe.get("format", {})
    return {
        "exists": True,
        "path": str(path),
        "name": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": int(fmt.get("size", 0) or 0),
        "duration_seconds": float(fmt.get("duration", 0) or 0),
        "video_streams": len(video_streams),
        "audio_streams": len(audio_streams),
        "subtitle_streams": len(subtitle_streams),
        "has_video": bool(video_streams),
        "has_audio": bool(audio_streams),
        "has_subtitles": bool(subtitle_streams),
        "probe": probe,
    }


def find_embedded_subtitles(probe: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for stream in probe.get("streams", []):
        if stream.get("codec_type") != "subtitle":
            continue
        tags = stream.get("tags") or {}
        results.append({
            "index": stream.get("index"),
            "language": str(tags.get("language", "")).lower(),
            "title": str(tags.get("title", "")).lower(),
        })
    return results


def find_embedded_ad_audio(probe: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for stream in probe.get("streams", []):
        if stream.get("codec_type") != "audio":
            continue
        tags = stream.get("tags") or {}
        searchable = " ".join(str(tags.get(k, "")) for k in ("title", "handler_name", "comment")).lower()
        if "audio description" in searchable or "descriptive audio" in searchable or "descriptive" in searchable:
            results.append({"index": stream.get("index"), "title": searchable})
    return results


def identify_package(package: Path) -> dict[str, Any]:
    discovered = discover_files(package)
    candidates = []
    for video in discovered["videos"]:
        try:
            info = inspect_media(video)
        except Exception as exc:
            log(f"WARNING: Could not inspect {video.name}: {exc}")
            continue
        if info["has_video"]:
            candidates.append(info)
    if not candidates:
        raise RuntimeError("No usable video source could be inspected.")
    candidates.sort(key=lambda x: (x["size_bytes"], x["duration_seconds"]), reverse=True)
    movie_info = candidates[0]
    movie = Path(movie_info["path"])
    movie_stem = movie.stem.lower()
    external_subtitles = [p for p in discovered["subtitles"] if p.stem.lower() == movie_stem or movie_stem in p.stem.lower() or p.stem.lower() in movie_stem]
    if not external_subtitles and len(discovered["subtitles"]) == 1:
        external_subtitles = discovered["subtitles"][:]
    external_ad_audio = [p for p in discovered["audios"] if filename_looks_like_ad(p)]
    report = {
        "package": str(package),
        "movie": str(movie),
        "movie_info": movie_info,
        "video_candidates": [x["path"] for x in candidates],
        "external_subtitles": [str(x) for x in external_subtitles],
        "external_ad_audio": [str(x) for x in external_ad_audio],
        "all_files": [str(x) for x in discovered["all"]],
    }
    (DIRS["logs"] / "last_source_discovery.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report


def validate_runtime_or_raise() -> None:
    problems = validate_runtime(CONFIG)
    if problems:
        raise RuntimeError("Runtime validation failed:\n- " + "\n- ".join(problems))


if __name__ == "__main__":
    validate_runtime_or_raise()
    log("ARK X Cinema runtime foundation PASS")
