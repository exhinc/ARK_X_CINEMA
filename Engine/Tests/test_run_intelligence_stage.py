"""Tests for the isolated intelligence stage runner."""

from pathlib import Path
import json
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import run_intelligence_stage as runner  # noqa: E402


def test_stage_runner_uses_configured_model_and_writes_artifact(monkeypatch, tmp_path):
    timeline_path = tmp_path / "timeline.json"
    output_path = tmp_path / "intelligence.json"
    timeline_path.write_text(json.dumps({"scenes": []}), encoding="utf-8")

    class Config:
        ollama_model = "qwen3:1.7b"
        ollama_url = "http://127.0.0.1:11434/api/generate"

    monkeypatch.setattr(runner, "load_config", lambda: Config())
    monkeypatch.setattr(runner, "validate_runtime", lambda config: [])
    monkeypatch.setattr(runner, "analyze_timeline", lambda timeline, model, base_url: {
        "status": "complete", "model": model, "processed_packets": 0, "total_packets": 0
    })

    artifact = runner.run_stage(timeline_path, output_path)
    assert artifact["model"] == "qwen3:1.7b"
    assert json.loads(output_path.read_text(encoding="utf-8"))["status"] == "complete"


def test_stage_runner_does_not_override_explicit_model(monkeypatch, tmp_path):
    timeline_path = tmp_path / "timeline.json"
    output_path = tmp_path / "intelligence.json"
    timeline_path.write_text(json.dumps({"scenes": []}), encoding="utf-8")
    seen = {}

    class Config:
        ollama_model = "qwen3:1.7b"
        ollama_url = "http://127.0.0.1:11434/api/generate"

    monkeypatch.setattr(runner, "load_config", lambda: Config())
    monkeypatch.setattr(runner, "validate_runtime", lambda config: [])
    def fake_analyze(timeline, model, base_url):
        seen["model"] = model
        return {"status": "complete", "model": model, "processed_packets": 0, "total_packets": 0}
    monkeypatch.setattr(runner, "analyze_timeline", fake_analyze)

    runner.run_stage(timeline_path, output_path, model="test-model")
    assert seen["model"] == "test-model"
