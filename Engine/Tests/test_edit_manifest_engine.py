"""Tests for script-to-source edit manifest construction."""

from pathlib import Path
import sys

import pytest

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from edit_manifest_engine import EditManifestError, build_edit_manifest  # noqa: E402


TIMELINE = {"scenes": [{"scene_id": "scene_001", "start": "00:00:00,000", "end": "00:00:10,000"}]}
SEGMENTS = [{"scene_id": "scene_001", "timestamp": "00:00:05", "text": "A door opens."}]


def test_build_manifest_maps_segment_to_source_range():
    manifest = build_edit_manifest(SEGMENTS, TIMELINE, 20.0, segment_durations=[2.0])
    edit = manifest["edits"][0]
    assert edit["scene_id"] == "scene_001"
    assert edit["source_start_seconds"] == 4.0
    assert edit["source_end_seconds"] == 8.0
    assert edit["narration_duration_seconds"] == 2.0


def test_build_manifest_rejects_unknown_scene():
    bad = [{"scene_id": "missing", "timestamp": "00:00:05", "text": "A door opens."}]
    with pytest.raises(EditManifestError, match="unknown scene"):
        build_edit_manifest(bad, TIMELINE, 20.0)


def test_build_manifest_rejects_timestamp_outside_scene():
    bad = [{"scene_id": "scene_001", "timestamp": "00:00:15", "text": "A door opens."}]
    with pytest.raises(EditManifestError, match="outside scene"):
        build_edit_manifest(bad, TIMELINE, 20.0)
