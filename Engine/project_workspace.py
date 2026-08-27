"""Canonical per-movie workspace and deterministic source manifest support."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_ROOT = ROOT / "Projects"
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".ts", ".mts", ".m2ts", ".wmv", ".flv", ".ogv"}
SUBTITLE_EXTENSIONS = {".srt", ".vtt", ".ass", ".ssa", ".sub", ".sbv", ".dfxp", ".ttml"}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma", ".ac3", ".eac3"}


def safe_movie_id(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_").lower()
    return value or "movie"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_workspace(movie_name: str) -> Path:
    """Create the canonical isolated workspace for one movie."""
    workspace = PROJECTS_ROOT / safe_movie_id(movie_name)
    for relative in (
        "source", "transcripts", "subtitles", "scenes", "analysis",
        "script", "narration", "edit", "qa", "artifacts", "logs"
    ):
        (workspace / relative).mkdir(parents=True, exist_ok=True)
    return workspace


def _classify(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    if suffix in SUBTITLE_EXTENSIONS:
        return "subtitle"
    if suffix in AUDIO_EXTENSIONS:
        return "audio"
    return None


def looks_like_ad(path: Path) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", " ", path.stem.lower()).strip()
    tokens = set(normalized.split())
    return bool({"ad", "audiodescription", "descriptive"} & tokens) or "audio description" in normalized or "descriptive audio" in normalized


def build_source_manifest(movie_package: Path, workspace: Path | None = None) -> dict[str, Any]:
    """Discover one movie package and write a deterministic source_manifest.json.

    Discovery is read-only: source files remain where the user placed them. The
    manifest records absolute paths for execution plus relative names for audit.
    Ambiguous packages are rejected rather than silently selecting the wrong file.
    """
    movie_package = Path(movie_package).resolve()
    if not movie_package.exists():
        raise FileNotFoundError(f"Movie package does not exist: {movie_package}")

    files = [movie_package] if movie_package.is_file() else sorted(p for p in movie_package.rglob("*") if p.is_file())
    classified: dict[str, list[Path]] = {"video": [], "subtitle": [], "audio": []}
    for path in files:
        kind = _classify(path)
        if kind:
            classified[kind].append(path)

    if len(classified["video"]) != 1:
        raise ValueError(f"Expected exactly one movie video; found {len(classified['video'])}")

    video = classified["video"][0]
    if workspace is None:
        workspace = create_workspace(video.stem)
    workspace = Path(workspace).resolve()

    matching_subtitles = [p for p in classified["subtitle"] if p.stem.lower() == video.stem.lower()]
    if not matching_subtitles and len(classified["subtitle"]) == 1:
        matching_subtitles = classified["subtitle"][:]
    ad_audio = [p for p in classified["audio"] if looks_like_ad(p)]

    def describe(path: Path) -> dict[str, Any]:
        return {
            "name": path.name,
            "path": str(path),
            "relative_to_package": str(path.relative_to(movie_package.parent if movie_package.is_file() else movie_package)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "extension": path.suffix.lower(),
        }

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "created_utc": utc_now(),
        "movie_id": safe_movie_id(video.stem),
        "workspace": str(workspace),
        "package": str(movie_package),
        "video": describe(video),
        "subtitles": [describe(p) for p in matching_subtitles],
        "ad_audio": [describe(p) for p in ad_audio],
        "other_audio": [describe(p) for p in classified["audio"] if p not in ad_audio],
        "all_supported_files": [describe(p) for kind in ("video", "subtitle", "audio") for p in classified[kind]],
        "selection": {
            "video_selection": "exactly_one_video",
            "subtitle_selection": "matching_stem_then_single_candidate",
            "ad_selection": "filename_heuristics_only; embedded_AD_must_be_resolved_by_media_inspection",
        },
    }
    (workspace / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest
