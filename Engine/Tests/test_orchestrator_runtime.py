"""Static integration tests for the Phase 2 runtime/orchestrator contract."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import orchestrator  # noqa: E402


def test_orchestrator_uses_runtime_configuration():
    source = (ENGINE / "orchestrator.py").read_text(encoding="utf-8-sig")
    assert "C:\\Whisper\\Release" not in source
    assert "load_config()" in source
    assert orchestrator.WHISPER == orchestrator.CONFIG.whisper_executable
    assert orchestrator.WHISPER_MODEL == orchestrator.CONFIG.whisper_model


def test_orchestrator_repository_root_is_dynamic():
    assert orchestrator.ROOT == ENGINE.parent.resolve()


def test_required_output_directories_are_declared():
    required = {
        "movies", "projects", "analysis", "scenes", "scripts", "narration",
        "visuals", "subtitles", "transcripts", "finished", "logs", "upload"
    }
    assert required.issubset(orchestrator.DIRS)
