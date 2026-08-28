"""Thin composition layer for the GitHub-side Stage-A core pipeline.

This module intentionally preserves the existing stage implementations. It only
connects their established boundaries in canonical order through the existing
resumable execution system. Real external engines remain subject to Windows
validation before Stage A can be declared complete.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from intelligence_stage_adapter import run_intelligence_stage
from movie_intelligence import build_scene_packets
from ollama_intelligence import infer_scene
from orchestrator_stage_adapter import StageBinding, run_bound_stage
from project_workspace import build_source_manifest, create_workspace
from recap_script_engine import generate_recap_text
from runtime_config import RuntimeConfig, load_config, validate_runtime
from script_stage_adapter import run_script_stage
from timeline_stage_adapter import bind_timeline
from transcription_stage_adapter import bind_ad_transcription


class StageARunnerError(RuntimeError):
    """Raised when the Stage-A core pipeline cannot advance safely."""


def _load_json(path: Path) -> dict[str, Any] | list[Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StageARunnerError(f"Could not read JSON artifact: {path}") from exc


def _find_subtitle(manifest: dict[str, Any]) -> Path | None:
    subtitles = manifest.get("subtitles")
    if isinstance(subtitles, list) and subtitles:
        path = subtitles[0].get("path") if isinstance(subtitles[0], dict) else None
        if path:
            return Path(path)
    return None


def _find_ad_audio(manifest: dict[str, Any]) -> Path:
    ad_audio = manifest.get("ad_audio")
    if isinstance(ad_audio, list) and ad_audio:
        path = ad_audio[0].get("path") if isinstance(ad_audio[0], dict) else None
        if path:
            return Path(path)
    raise StageARunnerError(
        "Stage A requires one external Audio Description audio file; none was found in the source manifest"
    )


def run_stage_a_core(
    source_package: Path,
    *,
    config: RuntimeConfig | None = None,
    validate_dependencies: bool = True,
    infer: Callable[..., Any] = infer_scene,
    generate: Callable[[list[dict[str, Any]]], str] | None = None,
) -> Path:
    """Run ingestion through script generation using existing stage boundaries.

    The run stops after the script artifact. TTS, scene synchronization, video,
    final subtitles, QA, and real-machine validation remain explicit next stages.
    """
    source_package = Path(source_package).resolve()
    if not source_package.exists():
        raise StageARunnerError(f"Source package does not exist: {source_package}")

    cfg = config or load_config()
    if validate_dependencies:
        problems = validate_runtime(cfg)
        if problems:
            raise StageARunnerError("Runtime validation failed:\n- " + "\n- ".join(problems))

    # Identify the single movie without changing the source package.
    video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".ts", ".mts", ".m2ts", ".wmv", ".flv", ".ogv"}
    if source_package.is_file():
        movie_path = source_package
    else:
        videos = sorted(
            p for p in source_package.rglob("*")
            if p.is_file() and p.suffix.lower() in video_extensions
        )
        if len(videos) != 1:
            raise StageARunnerError(f"Expected exactly one movie video; found {len(videos)}")
        movie_path = videos[0]

    workspace = create_workspace(movie_path.stem)
    movie_id = workspace.name

    manifest_holder: dict[str, Any] = {}

    def ingestion_work() -> None:
        manifest_holder.update(build_source_manifest(source_package, workspace))

    ingestion = run_bound_stage(
        workspace,
        movie_id,
        StageBinding("ingestion", "source_manifest.json", ingestion_work),
    )
    if ingestion.status == "failed":
        raise StageARunnerError(ingestion.error or "Ingestion failed")

    if not manifest_holder:
        loaded = _load_json(workspace / "source_manifest.json")
        if not isinstance(loaded, dict):
            raise StageARunnerError("Source manifest is not an object")
        manifest_holder = loaded

    manifest = manifest_holder
    ad_audio = _find_ad_audio(manifest)
    subtitle_srt = _find_subtitle(manifest)
    ad_srt = workspace / "transcripts" / "ad.srt"

    transcription = bind_ad_transcription(
        root=workspace,
        movie_id=movie_id,
        ad_audio=ad_audio,
        output_srt=ad_srt,
        whisper_executable=cfg.whisper_executable,
        whisper_model=cfg.whisper_model,
    )
    if transcription.status == "failed":
        raise StageARunnerError(transcription.error or "AD transcription failed")

    timeline_path = workspace / "scenes" / "timeline.json"
    timeline_result = bind_timeline(
        root=workspace,
        movie_id=movie_id,
        subtitle_srt=subtitle_srt,
        ad_srt=ad_srt,
        output_json=timeline_path,
    )
    if timeline_result.status == "failed":
        raise StageARunnerError(timeline_result.error or "Timeline stage failed")

    timeline = _load_json(timeline_path)
    if not isinstance(timeline, dict):
        raise StageARunnerError("Timeline artifact is not an object")

    intelligence = run_intelligence_stage(
        root=workspace,
        movie_id=movie_id,
        timeline=timeline,
        model=cfg.ollama_model,
        base_url=cfg.ollama_url,
        infer=infer,
    )

    intelligence_path = workspace / "intelligence" / "intelligence.json"
    if not intelligence_path.is_file() or intelligence_path.stat().st_size == 0:
        raise StageARunnerError("Intelligence stage completed without a valid artifact")

    generator = generate
    if generator is None:
        generator = lambda items: generate_recap_text(
            items,
            cfg.ollama_model,
            base_url=cfg.ollama_url,
        )

    run_script_stage(
        root=workspace,
        movie_id=movie_id,
        intelligence=intelligence,
        generate=generator,
    )
    script_path = workspace / "script" / "recap.txt"
    if not script_path.is_file() or script_path.stat().st_size == 0:
        raise StageARunnerError("Script stage completed without a valid artifact")
    return workspace
