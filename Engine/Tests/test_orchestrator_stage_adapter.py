"""Tests for the non-invasive orchestrator integration boundary."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from orchestrator_stage_adapter import StageBinding, run_bound_stage


def _artifact(root: Path, relative: str, text: str = "ok") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_adapter_records_existing_stage_output(tmp_path):
    calls = []
    _artifact(tmp_path, "workspace/ingestion.json")
    result = run_bound_stage(
        tmp_path,
        "movie-001",
        StageBinding("ingestion", "workspace/ingestion.json", lambda: calls.append("ingest")),
    )
    assert result.status == "complete"
    assert calls == ["ingest"]


def test_completed_bound_stage_is_not_called_again(tmp_path):
    calls = []
    binding = StageBinding("ingestion", "workspace/ingestion.json", lambda: calls.append("called"))
    _artifact(tmp_path, "workspace/ingestion.json")
    assert run_bound_stage(tmp_path, "movie-001", binding).status == "complete"
    assert run_bound_stage(tmp_path, "movie-001", binding).status == "skipped"
    assert calls == ["called"]


def test_adapter_does_not_hide_stage_failure(tmp_path):
    binding = StageBinding("ingestion", "workspace/ingestion.json", lambda: (_ for _ in ()).throw(RuntimeError("ingestion failed")))
    result = run_bound_stage(tmp_path, "movie-001", binding)
    assert result.status == "failed"
    assert result.error == "ingestion failed"
