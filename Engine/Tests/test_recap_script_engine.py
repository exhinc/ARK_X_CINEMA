"""Tests for the local evidence-grounded recap script engine."""

from pathlib import Path
import json
import sys

import pytest

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import recap_script_engine as rse  # noqa: E402


INTELLIGENCE = [
    {
        "scene_id": "scene_001",
        "start": "00:00:00,000",
        "end": "00:00:05,000",
        "intelligence": {"summary": "Alice opens a door.", "unsupported_claims": []},
    },
    {
        "scene_id": "scene_002",
        "start": "00:00:05,000",
        "end": "00:00:10,000",
        "intelligence": {"summary": "A dark hallway is visible.", "unsupported_claims": []},
    },
]


def _fake_urlopen(monkeypatch, response_text):
    class FakeResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self):
            return json.dumps({"response": response_text}).encode("utf-8")

    monkeypatch.setattr(rse, "urlopen", lambda *args, **kwargs: FakeResponse())


def test_generate_recap_returns_chronological_grounded_segments(monkeypatch):
    _fake_urlopen(
        monkeypatch,
        '```json\n{"segments":[{"text":"Alice opens the door.","timestamp":"00:00:01","scene_id":"scene_001"},{"text":"Inside, a dark hallway waits.","timestamp":"00:00:06","scene_id":"scene_002"}]}\n```',
    )
    result = rse.generate_recap(INTELLIGENCE, "qwen3:1.7b")
    assert result.text == "Alice opens the door. Inside, a dark hallway waits."
    assert [s.scene_id for s in result.segments] == ["scene_001", "scene_002"]


def test_generate_recap_rejects_timestamp_outside_scene(monkeypatch):
    _fake_urlopen(
        monkeypatch,
        '{"segments":[{"text":"Invented timing.","timestamp":"00:00:09","scene_id":"scene_001"}]}',
    )
    with pytest.raises(rse.RecapScriptError, match="outside its declared scene evidence"):
        rse.generate_recap(INTELLIGENCE, "qwen3:1.7b")


def test_generate_recap_rejects_non_chronological_segments(monkeypatch):
    _fake_urlopen(
        monkeypatch,
        '{"segments":[{"text":"Later first.","timestamp":"00:00:07","scene_id":"scene_002"},{"text":"Earlier second.","timestamp":"00:00:02","scene_id":"scene_001"}]}',
    )
    with pytest.raises(rse.RecapScriptError, match="not chronological"):
        rse.generate_recap(INTELLIGENCE, "qwen3:1.7b")
