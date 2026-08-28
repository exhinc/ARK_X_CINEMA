"""Tests for the resumable AD transcription adapter."""
from pathlib import Path
import sys
ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))
from orchestrator_stage_adapter import StageBinding, run_bound_stage
from transcription_stage_adapter import bind_ad_transcription

def _complete_ingestion(root, movie_id):
    path = root / "ingestion.txt"
    path.write_text("ready", encoding="utf-8")
    run_bound_stage(root, movie_id, StageBinding("ingestion", "ingestion.txt", lambda: None))

def test_ad_transcription_is_bound_to_transcription_stage(tmp_path, monkeypatch):
    root = tmp_path; movie_id = "movie"
    _complete_ingestion(root, movie_id)
    ad_audio = root / "source" / "movie_ad.mp3"; output = root / "Projects" / "movie" / "transcripts" / "ad.srt"
    whisper = root / "bin" / "whisper-cli.exe"; model = root / "models" / "model.bin"
    ad_audio.parent.mkdir(parents=True); whisper.parent.mkdir(parents=True); model.parent.mkdir(parents=True)
    ad_audio.write_bytes(b"audio"); whisper.write_bytes(b"exe"); model.write_bytes(b"model")
    def fake_transcribe(**kwargs):
        kwargs["output_srt"].parent.mkdir(parents=True, exist_ok=True)
        kwargs["output_srt"].write_text("1\n00:00:00,000 --> 00:00:01,000\nA person enters.\n", encoding="utf-8")
        return kwargs["output_srt"]
    monkeypatch.setattr("transcription_stage_adapter.transcribe_ad_to_srt", fake_transcribe)
    result = bind_ad_transcription(root, movie_id, ad_audio, output, whisper, model)
    assert result.status == "complete" and result.stage == "transcription" and output.exists()

def test_completed_transcription_is_not_run_again(tmp_path, monkeypatch):
    root = tmp_path; movie_id = "movie"
    _complete_ingestion(root, movie_id)
    ad_audio = root / "ad.mp3"; output = root / "Projects" / "movie" / "transcripts" / "ad.srt"; whisper = root / "whisper.exe"; model = root / "model.bin"
    for path in (ad_audio, whisper, model): path.write_bytes(b"x")
    calls = []
    def fake_transcribe(**kwargs):
        calls.append(1); kwargs["output_srt"].parent.mkdir(parents=True, exist_ok=True); kwargs["output_srt"].write_text("1\n00:00:00,000 --> 00:00:01,000\nDescription.\n", encoding="utf-8"); return kwargs["output_srt"]
    monkeypatch.setattr("transcription_stage_adapter.transcribe_ad_to_srt", fake_transcribe)
    bind_ad_transcription(root, movie_id, ad_audio, output, whisper, model)
    second = bind_ad_transcription(root, movie_id, ad_audio, output, whisper, model)
    assert second.status == "skipped" and len(calls) == 1
