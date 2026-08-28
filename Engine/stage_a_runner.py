"""Thin composition layer for the full ARK X Cinema Stage-A pipeline.

The runner preserves the existing stage implementations and resumable state
system. It composes them in canonical order and leaves real engine/performance
validation to the target Windows machine.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable

from edit_manifest_engine import build_edit_manifest, write_edit_manifest
from ffmpeg_video_engine import assemble_recap
from intelligence_stage_adapter import run_intelligence_stage
from media_qa_inspector import inspect_video
from ollama_intelligence import infer_scene
from orchestrator_stage_adapter import StageBinding, run_bound_stage
from piper_tts_engine import synthesize_segments
from project_workspace import build_source_manifest, create_workspace
from recap_script_engine import generate_recap
from recap_subtitle_engine import write_recap_srt
from runtime_config import RuntimeConfig, load_config, validate_runtime
from script_stage_adapter import run_script_stage
from stage_state import load_state
from timeline_stage_adapter import bind_timeline
from transcription_stage_adapter import bind_ad_transcription
from tts_stage_adapter import run_tts_stage
from video_stage_adapter import run_video_stage


class StageARunnerError(RuntimeError):
    """Raised when the Stage-A pipeline cannot advance safely."""


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


def _find_piper_paths(config: RuntimeConfig) -> tuple[Path, Path]:
    executable = Path(os.environ.get("ARK_PIPER_EXECUTABLE", config.root / "Tools" / "TTS" / "piper.exe"))
    model = Path(os.environ.get("ARK_PIPER_MODEL", config.root / "Tools" / "TTS" / "en_US-lessac-medium.onnx"))
    return executable, model


def _load_segments(path: Path) -> list[dict[str, Any]]:
    data = _load_json(path)
    if not isinstance(data, list) or not data:
        raise StageARunnerError(f"Recap segment artifact is invalid or empty: {path}")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise StageARunnerError(f"Recap segment {index} is not an object")
        result.append(item)
    return result


def _movie_duration_seconds(path: Path) -> float:
    import subprocess

    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise StageARunnerError(f"ffprobe could not determine movie duration: {path}")
    try:
        duration = float(result.stdout.strip())
    except ValueError as exc:
        raise StageARunnerError(f"Invalid movie duration reported by ffprobe: {path}") from exc
    if duration <= 0:
        raise StageARunnerError(f"Movie duration is not positive: {path}")
    return duration


def run_stage_a(
    source_package: Path,
    *,
    config: RuntimeConfig | None = None,
    validate_dependencies: bool = True,
    infer: Callable[..., Any] = infer_scene,
) -> Path:
    """Run all canonical Stage-A stages from ingestion through deterministic QA."""
    source_package = Path(source_package).resolve()
    if not source_package.exists():
        raise StageARunnerError(f"Source package does not exist: {source_package}")

    cfg = config or load_config()
    if validate_dependencies:
        problems = validate_runtime(cfg)
        if problems:
            raise StageARunnerError("Runtime validation failed:\n- " + "\n- ".join(problems))

    video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".ts", ".mts", ".m2ts", ".wmv", ".flv", ".ogv"}
    if source_package.is_file():
        movie_path = source_package
    else:
        videos = sorted(p for p in source_package.rglob("*") if p.is_file() and p.suffix.lower() in video_extensions)
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

    def generator(items: list[dict[str, Any]]) -> Any:
        return generate_recap(items, cfg.ollama_model, base_url=cfg.ollama_url)

    run_script_stage(
        root=workspace,
        movie_id=movie_id,
        intelligence=intelligence,
        generate=generator,
    )
    script_path = workspace / "script" / "recap.txt"
    segment_path = workspace / "script" / "recap_segments.json"
    if not script_path.is_file() or script_path.stat().st_size == 0:
        raise StageARunnerError("Script stage completed without a valid artifact")
    segments = _load_segments(segment_path)

    piper_executable, piper_model = _find_piper_paths(cfg)
    narration_path = workspace / "audio" / "narration.wav"
    narration_metadata_path = workspace / "audio" / "narration_segments.json"

    def synthesize(_: str, destination: Path) -> None:
        synthesize_segments(
            segments=segments,
            executable=piper_executable,
            model=piper_model,
            output_wav=destination,
            metadata_path=narration_metadata_path,
        )

    tts_result = run_tts_stage(
        root=workspace,
        movie_id=movie_id,
        script=script_path.read_text(encoding="utf-8"),
        synthesize=synthesize,
    )
    if not tts_result.is_file() or tts_result.stat().st_size == 0:
        raise StageARunnerError("TTS stage completed without a valid narration artifact")
    narration_metadata = _load_json(narration_metadata_path)
    if not isinstance(narration_metadata, dict) or not isinstance(narration_metadata.get("segments"), list):
        raise StageARunnerError("Narration timing artifact is invalid")

    duration = _movie_duration_seconds(movie_path)
    durations = [float(item["duration_seconds"]) for item in narration_metadata["segments"]]
    edit_manifest = build_edit_manifest(
        segments,
        timeline,
        duration,
        segment_durations=durations,
    )
    edit_manifest_path = workspace / "edit" / "edit_manifest.json"
    write_edit_manifest(edit_manifest, edit_manifest_path)

    recap_srt_path = workspace / "subtitles" / "recap.srt"
    write_recap_srt(narration_metadata["segments"], recap_srt_path)

    final_video = workspace / "video" / "final.mp4"

    def assemble(source: Path, narration: Path, destination: Path) -> None:
        assemble_recap(
            source_video=source,
            narration=narration,
            edit_manifest=edit_manifest_path,
            subtitle=recap_srt_path,
            destination=destination,
        )

    video_result = run_video_stage(
        root=workspace,
        movie_id=movie_id,
        source_video=movie_path,
        narration=narration_path,
        assemble=assemble,
        subtitle=recap_srt_path,
    )
    if not video_result.is_file() or video_result.stat().st_size == 0:
        raise StageARunnerError("Video stage completed without a valid final video")

    qa_result = __import__("qa_stage_adapter").run_qa_stage(
        root=workspace,
        movie_id=movie_id,
        final_video=final_video,
        narration=narration_path,
        script=script_path,
        timeline=timeline_path,
        intelligence=intelligence_path,
        inspect_video=inspect_video,
    )
    if qa_result.get("passed") is not True:
        raise StageARunnerError("Final QA did not pass")

    state = load_state(workspace, movie_id)
    if tuple(state.completed) != ("ingestion", "transcription", "timeline", "intelligence", "script", "tts", "video", "qa"):
        raise StageARunnerError(f"Stage A completed with unexpected state: {state}")
    return workspace


# Backwards-compatible name for the earlier pre-PC composition entry point.
def run_stage_a_core(
    source_package: Path,
    *,
    config: RuntimeConfig | None = None,
    validate_dependencies: bool = True,
    infer: Callable[..., Any] = infer_scene,
    generate: Callable[[list[dict[str, Any]]], str] | None = None,
) -> Path:
    """Run the canonical core through script generation for compatibility.

    If a custom generator is supplied, only the pre-PC portion is executed;
    the full production entry point is ``run_stage_a``.
    """
    if generate is not None:
        return _run_stage_a_core_compat(
            source_package,
            config=config,
            validate_dependencies=validate_dependencies,
            infer=infer,
            generate=generate,
        )
    return run_stage_a(source_package, config=config, validate_dependencies=validate_dependencies, infer=infer)


def _run_stage_a_core_compat(
    source_package: Path,
    *,
    config: RuntimeConfig | None,
    validate_dependencies: bool,
    infer: Callable[..., Any],
    generate: Callable[[list[dict[str, Any]]], str],
) -> Path:
    """Compatibility composition used only by focused adapter tests."""
    # Preserve the prior testable path without duplicating the production stages.
    source_package = Path(source_package).resolve()
    cfg = config or load_config()
    if validate_dependencies:
        problems = validate_runtime(cfg)
        if problems:
            raise StageARunnerError("Runtime validation failed:\n- " + "\n- ".join(problems))
    video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".ts", ".mts", ".m2ts", ".wmv", ".flv", ".ogv"}
    movie_path = source_package if source_package.is_file() else next(
        (p for p in source_package.rglob("*") if p.is_file() and p.suffix.lower() in video_extensions),
        None,
    )
    if movie_path is None:
        raise StageARunnerError("No usable movie video found")
    workspace = create_workspace(movie_path.stem)
    movie_id = workspace.name
    manifest_holder: dict[str, Any] = {}

    def ingestion_work() -> None:
        manifest_holder.update(build_source_manifest(source_package, workspace))

    result = run_bound_stage(workspace, movie_id, StageBinding("ingestion", "source_manifest.json", ingestion_work))
    if result.status == "failed":
        raise StageARunnerError(result.error or "Ingestion failed")
    manifest = manifest_holder or _load_json(workspace / "source_manifest.json")
    if not isinstance(manifest, dict):
        raise StageARunnerError("Source manifest is not an object")
    ad_audio = _find_ad_audio(manifest)
    subtitle_srt = _find_subtitle(manifest)
    ad_srt = workspace / "transcripts" / "ad.srt"
    result = bind_ad_transcription(workspace, movie_id, ad_audio, ad_srt, cfg.whisper_executable, cfg.whisper_model)
    if result.status == "failed":
        raise StageARunnerError(result.error or "AD transcription failed")
    timeline_path = workspace / "scenes" / "timeline.json"
    result = bind_timeline(workspace, movie_id, subtitle_srt, ad_srt, timeline_path)
    if result.status == "failed":
        raise StageARunnerError(result.error or "Timeline stage failed")
    timeline = _load_json(timeline_path)
    intelligence = run_intelligence_stage(workspace, movie_id, timeline, cfg.ollama_model, base_url=cfg.ollama_url, infer=infer)
    run_script_stage(workspace, movie_id, intelligence, generate)
    return workspace
