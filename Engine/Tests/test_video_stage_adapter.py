"""Tests for the resumable video assembly boundary."""
from pathlib import Path
import sys
import pytest
ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))
from orchestrator_stage_adapter import StageBinding, run_bound_stage
from video_stage_adapter import VideoStageError, run_video_stage

def _complete_prerequisites(tmp_path):
    for stage, artifact in (("ingestion", "ingestion.txt"), ("transcription", "ad.srt"), ("timeline", "timeline.json"), ("intelligence", "intelligence/intelligence.json"), ("script", "script/recap.txt"), ("tts", "audio/narration.wav")):
        path = tmp_path / artifact; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(stage.encode())
        run_bound_stage(tmp_path, "movie-001", StageBinding(stage, artifact, lambda: None))

def test_video_assembly_is_resumable(tmp_path):
    _complete_prerequisites(tmp_path); source = tmp_path / "movie.mp4"; narration = tmp_path / "audio" / "narration.wav"; source.write_bytes(b"source"); calls = []
    def assemble(video, voice, destination): calls.append((video, voice)); destination.write_bytes(b"final-mp4")
    first = run_video_stage(tmp_path, "movie-001", source, narration, assemble); second = run_video_stage(tmp_path, "movie-001", source, narration, assemble)
    assert first == second and len(calls) == 1 and first.read_bytes() == b"final-mp4"

def test_missing_source_is_rejected(tmp_path):
    _complete_prerequisites(tmp_path); narration = tmp_path / "audio" / "narration.wav"
    with pytest.raises(VideoStageError): run_video_stage(tmp_path, "movie-001", tmp_path / "missing.mp4", narration, lambda *_: None)

def test_empty_output_is_recorded_as_failed(tmp_path):
    _complete_prerequisites(tmp_path); source = tmp_path / "movie.mp4"; narration = tmp_path / "audio" / "narration.wav"; source.write_bytes(b"source")
    def assemble(_, __, destination): destination.write_bytes(b"")
    result = run_video_stage(tmp_path, "movie-001", source, narration, assemble)
    assert result.status == "failed"
