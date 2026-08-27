"""Tests for evidence-first movie intelligence preparation."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from movie_intelligence import build_intelligence_schema, build_scene_packets  # noqa: E402


def test_packets_preserve_scene_provenance():
    timeline = {
        "scenes": [{
            "scene_id": "movie_scene_0001",
            "start": "00:00:01,000",
            "end": "00:00:04,000",
            "duration_ms": 3000,
            "sources": ["ad", "subtitle"],
            "cues": [
                {"source": "subtitle", "start": "00:00:01,000", "end": "00:00:02,000", "text": "Run!"},
                {"source": "ad", "start": "00:00:02,000", "end": "00:00:03,000", "text": "A man runs outside."},
            ],
        }]
    }
    packets = build_scene_packets(timeline)
    assert len(packets) == 1
    assert packets[0]["scene_id"] == "movie_scene_0001"
    assert [x["source"] for x in packets[0]["evidence"]] == ["subtitle", "ad"]


def test_packets_are_bounded():
    timeline = {"scenes": [{
        "scene_id": "s1", "start": "00:00:00,000", "end": "00:01:00,000", "duration_ms": 60000,
        "sources": ["ad"], "cues": [
            {"source": "ad", "start": "00:00:00,000", "end": "00:00:01,000", "text": "x" * 2000},
            {"source": "ad", "start": "00:00:02,000", "end": "00:00:03,000", "text": "y" * 5000},
        ]
    }]}
    packet = build_scene_packets(timeline, max_chars_per_packet=2500)[0]
    assert packet["evidence_characters"] <= 2500


def test_schema_requires_unknown_and_provenance_safe_outputs():
    schema = build_intelligence_schema()
    assert "unsupported_claims" in schema["scene_fields"]
    assert "confidence" in schema["scene_fields"]
    assert "traceable" in schema["rule"]
