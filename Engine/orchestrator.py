"""ARK X Cinema production orchestrator foundation.

The orchestrator is intentionally conservative: one heavy AI stage at a time,
explicit runtime validation, and resumable project state. Full downstream
production stages are added only after their inputs/outputs are validated.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from project_workspace import build_source_manifest, create_workspace
from runtime_config import load_config, validate_runtime

ROOT = Path(__file__).resolve().parents[1]
CONFIG = load_config()
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
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".ts", ".mts", ".m2ts", ".wmv", ".flv", ".ogv"}
SUBTITLE_EXTENSIONS = {".srt", ".vtt", ".ass", ".ssa", ".sub", ".sbv", ".dfxp", ".ttml"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma", ".ac3", ".eac3"}


def log(message: str) -> None:
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def run(cmd: list[Any], capture: bool = True) -> subprocess.CompletedProcess[str]:
    command = [str(item) for item in cmd]
    log("RUN: " + " ".join(command))
    return subprocess.run(command, text=True, capture_output=capture, encoding="utf-8", errors="replace", check=False)


def safe_name(name: str) -> str:
    name = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name).strip("_")
    return name or "Movie"


def project_state(project: Path, stage: str, status: str = "complete", details: dict[str, Any] | None = None) -> None:
    project.mkdir(parents=True, exist_ok=True)
    state = {"stage": stage, "status": status, "updated": datetime.now().isoformat(), "details": details or {}}
    (project / "pipeline_state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


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
    return "ad" in tokens or "audiodescription" in tokens or "descriptive" in tokens or "audio description" in normalized or "descriptive audio" in normalized


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
        "exists": True, "path": str(path), "name": path.name, "extension": path.suffix.lower(),
        "size_bytes": int(fmt.get("size", 0) or 0), "duration_seconds": float(fmt.get("duration", 0) or 0),
        "video_streams": len(video_streams), "audio_streams": len(audio_streams), "subtitle_streams": len(subtitle_streams),
        "has_video": bool(video_streams), "has_audio": bool(audio_streams), "has_subtitles": bool(subtitle_streams), "probe": probe,
    }


def find_embedded_subtitles(probe: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"index": s.get("index"), "language": str((s.get("tags") or {}).get("language", "")).lower(), "title": str((s.get("tags") or {}).get("title", "")).lower()}
        for s in probe.get("streams", []) if s.get("codec_type") == "subtitle"
    ]


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
    """Create the canonical per-movie workspace and deterministic source manifest."""
    package = Path(package)
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
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one usable movie video; found {len(candidates)}")

    movie = Path(candidates[0]["path"])
    workspace = create_workspace(movie.stem)
    manifest = build_source_manifest(package, workspace)
    manifest["movie_info"] = candidates[0]
    manifest["embedded_subtitles"] = find_embedded_subtitles(candidates[0]["probe"])
    manifest["embedded_ad_audio"] = find_embedded_ad_audio(candidates[0]["probe"])
    (workspace / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    project_state(workspace, "SOURCE_DISCOVERED", "complete", {"manifest": str(workspace / "source_manifest.json")})
    return manifest


def validate_runtime_or_raise() -> None:
    problems = validate_runtime(CONFIG)
    if problems:
        raise RuntimeError("Runtime validation failed:\n- " + "\n- ".join(problems))


if __name__ == "__main__":
    validate_runtime_or_raise()
    log("ARK X Cinema runtime foundation PASS")
