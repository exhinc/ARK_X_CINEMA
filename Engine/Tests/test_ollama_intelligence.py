"""Unit tests for the dependency-free Ollama adapter."""

from pathlib import Path
import json
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import ollama_intelligence as oi  # noqa: E402


VALID = {
    "summary": "A person runs outside.", "characters": ["person"], "location": "outside",
    "actions": ["runs"], "dialogue_points": [], "visual_description_points": ["person runs"],
    "cause_effect": [], "importance": "low", "confidence": 0.9, "unsupported_claims": []
}


def test_endpoint_normalizes_api_path():
    assert oi._endpoint("http://127.0.0.1:11434") == "http://127.0.0.1:11434/api/generate"
    assert oi._endpoint("http://127.0.0.1:11434/api/generate") == "http://127.0.0.1:11434/api/generate"


def test_validation_accepts_contract():
    oi._validate_intelligence(VALID)


def test_validation_rejects_missing_field():
    bad = dict(VALID)
    bad.pop("summary")
    try:
        oi._validate_intelligence(bad)
    except oi.OllamaError as exc:
        assert "summary" in str(exc)
    else:
        raise AssertionError("missing field was accepted")


def test_infer_scene_uses_non_streaming_json(monkeypatch):
    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self):
            return json.dumps({"response": json.dumps(VALID), "total_duration": 25_000_000}).encode()

    captured = {}
    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode())
        return FakeResponse()

    monkeypatch.setattr(oi, "urlopen", fake_urlopen)
    result = oi.infer_scene({"scene_id": "s1", "evidence": [{"text": "A person runs."}]}, "qwen3:1.7b")
    assert result.parsed == VALID
    assert result.duration_ms == 25
    assert captured["body"]["stream"] is False
    assert captured["body"]["format"] == "json"
    assert "A person runs." in captured["body"]["prompt"]


def test_infer_scene_reports_connection_failure(monkeypatch):
    def fake_urlopen(*args, **kwargs):
        from urllib.error import URLError
        raise URLError("connection refused")
    monkeypatch.setattr(oi, "urlopen", fake_urlopen)
    try:
        oi.infer_scene({"scene_id": "s1", "evidence": []}, "qwen3:1.7b", timeout_seconds=1)
    except oi.OllamaError as exc:
        assert "unavailable" in str(exc).lower()
    else:
        raise AssertionError("connection failure was not converted to OllamaError")
