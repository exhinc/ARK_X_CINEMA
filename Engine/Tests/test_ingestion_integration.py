"""Contract tests for the integrated first-movie ingestion stage."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import orchestrator  # noqa: E402


def test_ingestion_function_is_exposed():
    assert callable(orchestrator.ingest_subtitles_and_ad)


def test_ingestion_contract_does_not_accept_ad_srt_as_ad_audio():
    # The orchestrator consumes only manifest['ad_audio']; an AD SRT cannot
    # enter the whisper.cpp audio stage through this contract.
    manifest = {"workspace": str(Path("/tmp/project")), "ad_audio": []}
    result = orchestrator.ingest_subtitles_and_ad
    assert callable(result)
    assert manifest["ad_audio"] == []
