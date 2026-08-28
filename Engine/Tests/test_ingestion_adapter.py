"""Tests for the ingestion adapter boundary."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from orchestrator_stage_adapter import bind_ingestion
from stage_state import load_state


def test_ingestion_adapter_preserves_existing_identify_then_ingest_flow(tmp_path):
    workspace = tmp_path / "Projects" / "movie-001"
    workspace.mkdir(parents=True)
    calls = []

    def identify():
        calls.append("identify")
        return {"workspace": str(workspace)}

    def ingest(manifest):
        calls.append(("ingest", manifest))
        artifact = workspace / "ingestion_manifest.json"
        artifact.write_text('{"status":"ready"}\n', encoding="utf-8")
        return {"status": "ready"}

    result = bind_ingestion(tmp_path, "movie-001", workspace, identify, ingest)

    assert result.status == "complete"
    assert calls[0] == "identify"
    assert calls[1][0] == "ingest"
    assert load_state(tmp_path, "movie-001").completed == ("ingestion",)


def test_completed_ingestion_is_not_called_again(tmp_path):
    workspace = tmp_path / "Projects" / "movie-001"
    workspace.mkdir(parents=True)
    (workspace / "ingestion_manifest.json").write_text('{"status":"ready"}\n', encoding="utf-8")
    calls = []

    def identify():
        calls.append("identify")
        return {}

    def ingest(_manifest):
        calls.append("ingest")

    first = bind_ingestion(tmp_path, "movie-001", workspace, identify, ingest)
    second = bind_ingestion(tmp_path, "movie-001", workspace, identify, ingest)

    assert first.status == "complete"
    assert second.status == "skipped"
    assert calls == ["identify", "ingest"]
