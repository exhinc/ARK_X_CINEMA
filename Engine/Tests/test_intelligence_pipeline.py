"""Tests for evidence-to-Ollama stage orchestration without a live Ollama server."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from intelligence_pipeline import analyze_timeline  # noqa: E402
from ollama_intelligence import OllamaError, OllamaResult  # noqa: E402


def _result(packet, **kwargs):
    return OllamaResult(
        model=kwargs.get("model", "qwen3:1.7b"),
        response="{}",
        parsed={
            "summary": "Supported scene.", "characters": [], "location": None,
            "actions": ["moves"], "dialogue_points": [], "visual_description_points": [],
            "cause_effect": [], "importance": "low", "confidence": 0.8,
            "unsupported_claims": [],
        },
        duration_ms=10,
    )


def test_analyze_timeline_processes_each_packet_in_order():
    timeline = {"scenes": [{
        "scene_id": "s1", "start": "00:00:00,000", "end": "00:00:02,000", "duration_ms": 2000,
        "sources": ["subtitle"], "cues": [
            {"source": "subtitle", "start": "00:00:00,000", "end": "00:00:01,000", "text": "Hello."},
            {"source": "subtitle", "start": "00:00:01,000", "end": "00:00:02,000", "text": "Goodbye."},
        ]
    }]}
    seen = []
    def fake_infer(packet, **kwargs):
        seen.append(packet["packet_id"])
        return _result(packet)
    artifact = analyze_timeline(timeline, "qwen3:1.7b", infer=fake_infer)
    assert artifact["status"] == "complete"
    assert artifact["processed_packets"] == artifact["total_packets"]
    assert seen == ["s1"]


def test_analyze_timeline_preserves_partial_results_on_model_failure():
    timeline = {"scenes": [{
        "scene_id": "s1", "start": "00:00:00,000", "end": "00:00:01,000", "duration_ms": 1000,
        "sources": ["subtitle"], "cues": [{"source": "subtitle", "start": "00:00:00,000", "end": "00:00:01,000", "text": "One."}]
    }, {
        "scene_id": "s2", "start": "00:00:02,000", "end": "00:00:03,000", "duration_ms": 1000,
        "sources": ["ad"], "cues": [{"source": "ad", "start": "00:00:02,000", "end": "00:00:03,000", "text": "Two."}]
    }]}
    calls = 0
    def fake_infer(packet, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OllamaError("Ollama unavailable")
        return _result(packet)
    artifact = analyze_timeline(timeline, "qwen3:1.7b", infer=fake_infer)
    assert artifact["status"] == "failed"
    assert artifact["processed_packets"] == 1
    assert artifact["total_packets"] == 2
    assert artifact["results"][0]["scene_id"] == "s1"
    assert "unavailable" in artifact["error"]
