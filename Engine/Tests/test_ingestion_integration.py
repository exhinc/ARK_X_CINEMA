"""Contract tests for the integrated first-movie ingestion stage."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import orchestrator  # noqa: E402


def test_ingestion_function_is_exposed():
    assert callable(orchestrator.ingest_subtitles_and_ad)


def test_ingestion_rejects_ad_srt_as_audio(tmp_path):
    ad_srt = tmp_path / "movie_AD.srt"
    ad_srt.write_text("1\n00:00:01,000 --> 00:00:02,000\nA man enters.\n", encoding="utf-8")
    assert orchestrator.filename_looks_like_ad(ad_srt)
    # The actual audio detector is intentionally extension-gated. Import it
    # here so this test exercises the production detector rather than a stub.
    from subtitle_pipeline import find_ad_audio
    assert find_ad_audio([ad_srt]) == []


def test_ingestion_uses_external_ad_audio_contract(tmp_path, monkeypatch):
    workspace = tmp_path / "movie"
    workspace.mkdir()
    ad_audio = tmp_path / "movie_AD.mp3"
    ad_audio.write_bytes(b"not real audio")
    manifest = {"workspace": str(workspace), "subtitles": [], "ad_audio": [{"path": str(ad_audio)}]}
    calls = []

    def fake_transcribe(source, destination, whisper, model):
        calls.append((source, destination, whisper, model))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("1\n00:00:01,000 --> 00:00:02,000\nDescription.\n", encoding="utf-8")
        return destination

    monkeypatch.setattr(orchestrator, "transcribe_ad_to_srt", fake_transcribe)
    result = orchestrator.ingest_subtitles_and_ad(manifest)
    assert result["ad_srt"].endswith("transcripts/ad.srt")
    assert calls and calls[0][0] == ad_audio
