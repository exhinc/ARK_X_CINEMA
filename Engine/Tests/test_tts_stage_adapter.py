"""Tests for the resumable TTS stage boundary."""

from pathlib import Path
import sys

import pytest

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from orchestrator_stage_adapter import StageBinding, run_bound_stage
from tts_stage_adapter import TTSStageError, run_tts_stage


def _complete_prerequisites(tmp_path):
    for stage, artifact in (("ingestion", "ingestion.txt"), ("transcription", "ad.srt"), ("timeline", "timeline.json"), ("intelligence", "intelligence/intelligence.json"), ("script", "script/recap.txt")):
        path = tmp_path / artifact
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(stage, encoding="utf-8")
        run_bound_stage(tmp_path, "movie-001", StageBinding(stage, artifact, lambda: None))


def test_tts_synthesizes_once_and_is_resumable(tmp_path):
    _complete_prerequisites(tmp_path)
    calls = []
    def synthesize(script, destination):
        calls.append(script)
        destination.write_bytes(b"RIFF-test-audio")
    first = run_tts_stage(tmp_path, "movie-001", "An original recap.", synthesize)
    second = run_tts_stage(tmp_path, "movie-001", "An original recap.", synthesize)
    assert first == second
    assert len(calls) == 1
    assert first.is_file() and first.stat().st_size > 0


def test_empty_script_is_rejected(tmp_path):
    _complete_prerequisites(tmp_path)
    with pytest.raises(TTSStageError):
        run_tts_stage(tmp_path, "movie-001", "   ", lambda *_: None)


def test_empty_tts_output_is_rejected(tmp_path):
    _complete_prerequisites(tmp_path)
    def synthesize(_, destination):
        destination.write_bytes(b"")
    with pytest.raises(TTSStageError):
        run_tts_stage(tmp_path, "movie-001", "Valid script.", synthesize)
