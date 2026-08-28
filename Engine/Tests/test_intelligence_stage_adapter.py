"""Tests for the resumable evidence-first intelligence stage."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from intelligence_stage_adapter import run_intelligence_stage
from ollama_intelligence import OllamaResult
from orchestrator_stage_adapter import StageBinding, run_bound_stage


def _timeline():
    return {"scenes": [{"scene_id": "scene_001", "start": 0, "end": 1000, "duration_ms": 1000, "sources": ["subtitle", "ad"], "cues": [{"source": "subtitle", "start": 0, "end": 500, "text": "Alice opens the door."}, {"source": "ad", "start": 500, "end": 1000, "text": "A dark hallway is visible."}]}]}


def test_intelligence_persists_validated_output_and_can_resume(tmp_path):
    calls = []

    def fake_infer(packet, model, base_url):
        calls.append(packet["packet_id"])
        parsed = {"summary": "Alice opens a door.", "characters": ["Alice"], "location": None, "actions": ["opens the door"], "dialogue_points": [], "visual_description_points": ["dark hallway"], "cause_effect": [], "importance": "normal", "confidence": 0.9, "unsupported_claims": []}
        return OllamaResult(model=model, response="{}", parsed=parsed)

    for stage, artifact in (("ingestion", "ingestion.txt"), ("transcription", "ad.srt"), ("timeline", "timeline.json")):
        path = tmp_path / artifact
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(stage, encoding="utf-8")
        run_bound_stage(tmp_path, "movie-001", StageBinding(stage, artifact, lambda: None))

    first = run_intelligence_stage(tmp_path, "movie-001", _timeline(), "qwen3:1.7b", infer=fake_infer)
    second = run_intelligence_stage(tmp_path, "movie-001", _timeline(), "qwen3:1.7b", infer=fake_infer)
    assert first == second
    assert calls == ["scene_001:0"]
    assert (tmp_path / "intelligence" / "intelligence.json").is_file()
