"""Tests for the thin Stage-A core composition layer."""

from pathlib import Path
import json
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import stage_a_runner as runner  # noqa: E402
from runtime_config import RuntimeConfig  # noqa: E402
from resumable_orchestrator import StageResult  # noqa: E402


def _config(tmp_path):
    return RuntimeConfig(
        root=tmp_path,
        whisper_executable=tmp_path / "whisper.exe",
        whisper_model=tmp_path / "model.bin",
        ollama_url="http://127.0.0.1:11434/api/generate",
        ollama_model="qwen3:1.7b",
        max_parallel_heavy_stages=1,
        ram_priority="strict",
    )


def test_run_stage_a_core_connects_existing_stages_in_order(tmp_path, monkeypatch):
    source = tmp_path / "Movie.mkv"
    source.write_bytes(b"movie")
    workspace = tmp_path / "Projects" / "movie"
    workspace.mkdir(parents=True)
    calls = []

    monkeypatch.setattr(runner, "create_workspace", lambda _: workspace)
    monkeypatch.setattr(runner, "validate_runtime", lambda _: [])

    def fake_run_bound_stage(root, movie_id, binding):
        calls.append(binding.name)
        binding.work()
        return StageResult(movie_id, binding.name, "complete", artifact=binding.artifact)
    monkeypatch.setattr(runner, "run_bound_stage", fake_run_bound_stage)

    manifest = {
        "schema_version": 1,
        "movie_id": "movie",
        "workspace": str(workspace),
        "video": {"path": str(source)},
        "subtitles": [{"path": str(tmp_path / "movie.srt")}],
        "ad_audio": [{"path": str(tmp_path / "movie_ad.mp3")}],
    }

    def fake_manifest(package, target):
        (target / "source_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return manifest
    monkeypatch.setattr(runner, "build_source_manifest", fake_manifest)

    for path in (tmp_path / "movie.srt", tmp_path / "movie_ad.mp3"):
        path.write_bytes(b"input")

    def fake_transcription(root, movie_id, ad_audio, output_srt, whisper_executable, whisper_model, ffmpeg_executable="ffmpeg"):
        calls.append("transcription")
        output_srt.parent.mkdir(parents=True, exist_ok=True)
        output_srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nDescription.\n", encoding="utf-8")
        return StageResult("movie", "transcription", "complete", artifact="transcripts/ad.srt")
    monkeypatch.setattr(runner, "bind_ad_transcription", fake_transcription)

    def fake_timeline(root, movie_id, subtitle_srt, ad_srt, output_json):
        calls.append("timeline")
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps({"scenes": []}), encoding="utf-8")
        return StageResult("movie", "timeline", "complete", artifact="scenes/timeline.json")
    monkeypatch.setattr(runner, "bind_timeline", fake_timeline)

    intelligence = [{
        "scene_id": "scene_001",
        "start": "00:00:00,000",
        "end": "00:00:01,000",
        "intelligence": {"summary": "Description.", "unsupported_claims": []},
    }]

    def fake_intelligence(root, movie_id, timeline, model, base_url="http://127.0.0.1:11434/api/generate", infer=runner.infer_scene):
        calls.append("intelligence")
        output = workspace / "intelligence" / "intelligence.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(intelligence), encoding="utf-8")
        return intelligence
    monkeypatch.setattr(runner, "run_intelligence_stage", fake_intelligence)

    def fake_script(root, movie_id, intelligence, generate):
        calls.append("script")
        output = workspace / "script" / "recap.txt"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("An original recap.", encoding="utf-8")
        return "An original recap."
    monkeypatch.setattr(runner, "run_script_stage", fake_script)

    result = runner.run_stage_a_core(
        source,
        config=_config(tmp_path),
        validate_dependencies=True,
        infer=lambda *args, **kwargs: None,
        generate=lambda _: "unused because script is mocked",
    )

    assert result == workspace
    assert calls == ["ingestion", "transcription", "timeline", "intelligence", "script"]
    assert (workspace / "script" / "recap.txt").is_file()
