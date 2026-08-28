"""Tests for the evidence-grounded recap script stage."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import pytest
from script_stage_adapter import ScriptStageError, run_script_stage
from orchestrator_stage_adapter import run_existing_stage


def _intelligence():
    return [{
        "packet_id": "scene_001:0",
        "scene_id": "scene_001",
        "start": 0,
        "end": 1000,
        "intelligence": {
            "summary": "Alice opens a door.",
            "characters": ["Alice"],
            "location": None,
            "actions": ["opens the door"],
            "dialogue_points": [],
            "visual_description_points": ["dark hallway"],
            "cause_effect": [],
            "importance": "normal",
            "confidence": 0.9,
            "unsupported_claims": [],
        },
    }]


def _complete_prerequisites(tmp_path):
    for stage, artifact in (("ingestion", "ingestion.txt"), ("transcription", "ad.srt"), ("timeline", "timeline.json"), ("intelligence", "intelligence/intelligence.json")):
        path = tmp_path / artifact
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(stage, encoding="utf-8")
        run_existing_stage(tmp_path, "movie-001", stage, lambda: None, artifact=artifact)


def test_script_uses_only_structured_intelligence_and_is_resumable(tmp_path):
    _complete_prerequisites(tmp_path)
    calls = []

    def generate(items):
        calls.append(items)
        return "Alice opens the door, revealing a dark hallway."

    first = run_script_stage(tmp_path, "movie-001", _intelligence(), generate)
    second = run_script_stage(tmp_path, "movie-001", _intelligence(), generate)

    assert first == second
    assert len(calls) == 1
    assert "Alice opens the door" in first
    assert (tmp_path / "script" / "recap.txt").is_file()


def test_missing_unsupported_claim_contract_is_rejected(tmp_path):
    _complete_prerequisites(tmp_path)
    bad = _intelligence()
    del bad[0]["intelligence"]["unsupported_claims"]
    with pytest.raises(ScriptStageError):
        run_script_stage(tmp_path, "movie-001", bad, lambda _: "should not run")
