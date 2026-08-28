"""Tests for crash-safe stage checkpoints."""

import json
from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from checkpoint import Checkpoint, CheckpointError, load_checkpoint, save_checkpoint


def test_checkpoint_round_trip(tmp_path):
    path = tmp_path / "state.json"
    original = Checkpoint("movie-001", "intelligence", "complete", artifact="Analysis/movie-001/intelligence.json")
    save_checkpoint(path, original)
    assert load_checkpoint(path) == original


def test_missing_checkpoint_returns_none(tmp_path):
    assert load_checkpoint(tmp_path / "missing.json") is None


def test_invalid_status_is_rejected(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(json.dumps({"movie_id": "movie-001", "stage": "intelligence", "status": "bogus"}), encoding="utf-8")
    try:
        load_checkpoint(path)
        assert False, "expected CheckpointError"
    except CheckpointError:
        pass


def test_checkpoint_write_is_valid_json(tmp_path):
    path = tmp_path / "nested" / "state.json"
    save_checkpoint(path, Checkpoint("movie-001", "timeline", "running"))
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == "running"
