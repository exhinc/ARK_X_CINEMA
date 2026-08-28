"""Tests for the resumable canonical timeline adapter."""
from pathlib import Path
import sys
import pytest
ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))
from stage_state import mark_complete, mark_running, StageStateError
from timeline_stage_adapter import bind_timeline

def _srt(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding="utf-8"); return path

def _complete_upstream(root: Path, movie_id: str) -> None:
    ingestion = "state/movie-001/ingestion.txt"; transcription = "state/movie-001/ad.srt"
    (root / ingestion).parent.mkdir(parents=True, exist_ok=True); (root / ingestion).write_text("ready", encoding="utf-8")
    mark_running(root, movie_id, "ingestion"); mark_complete(root, movie_id, "ingestion", ingestion)
    (root / transcription).write_text("1\n00:00:01,000 --> 00:00:02,000\nA person enters.\n", encoding="utf-8")
    mark_running(root, movie_id, "transcription"); mark_complete(root, movie_id, "transcription", transcription)

def test_timeline_adapter_combines_subtitle_and_ad_provenance(tmp_path):
    _complete_upstream(tmp_path, "movie-001"); subtitle = _srt(tmp_path / "source" / "movie.srt", "1\n00:00:01,000 --> 00:00:02,000\nHello.\n"); ad = tmp_path / "state" / "movie-001" / "ad.srt"; output = tmp_path / "Projects" / "movie-001" / "scenes" / "timeline.json"
    result = bind_timeline(tmp_path, "movie-001", subtitle, ad, output)
    assert result.status == "complete" and result.stage == "timeline" and output.exists()
    text = output.read_text(encoding="utf-8"); assert '"subtitle"' in text and '"ad"' in text

def test_completed_timeline_is_skipped_when_artifact_is_intact(tmp_path):
    _complete_upstream(tmp_path, "movie-001"); ad = tmp_path / "state" / "movie-001" / "ad.srt"; subtitle = _srt(tmp_path / "source" / "movie.srt", "1\n00:00:01,000 --> 00:00:02,000\nHello.\n"); output = tmp_path / "Projects" / "movie-001" / "scenes" / "timeline.json"
    first = bind_timeline(tmp_path, "movie-001", subtitle, ad, output); second = bind_timeline(tmp_path, "movie-001", subtitle, ad, output)
    assert first.status == "complete" and second.status == "skipped"

def test_timeline_requires_transcription_stage(tmp_path):
    subtitle = _srt(tmp_path / "movie.srt", "1\n00:00:01,000 --> 00:00:02,000\nHello.\n"); output = tmp_path / "timeline.json"
    with pytest.raises(StageStateError): bind_timeline(tmp_path, "movie-001", subtitle, None, output)
