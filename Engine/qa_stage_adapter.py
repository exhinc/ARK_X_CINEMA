"""Deterministic QA boundary for ARK X Cinema production artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from orchestrator_stage_adapter import StageBinding, run_bound_stage


class QAStageError(ValueError):
    """Raised when required QA inputs are invalid."""


def _require_file(path: Path, label: str, *, nonempty: bool = True) -> None:
    if not path.is_file():
        raise QAStageError(f"Missing {label}: {path}")
    if nonempty and path.stat().st_size == 0:
        raise QAStageError(f"Empty {label}: {path}")


def run_qa_stage(root: Path, movie_id: str, *, source_video: Path, narration: Path, script: Path, timeline: Path, intelligence: Path, inspect_video: Callable[[Path], dict[str, Any]]) -> dict[str, Any]:
    """Run deterministic artifact checks and persist a QA report."""
    required = ((source_video, "source video"), (narration, "narration"), (script, "script"), (timeline, "timeline"), (intelligence, "intelligence"))
    for path, label in required:
        _require_file(Path(path), label)

    artifact = Path("qa") / "report.json"
    destination = root / artifact

    def work() -> None:
        video_path = Path(source_video)
        report: dict[str, Any] = {
            "movie_id": movie_id,
            "checks": {"source_video_present": True, "narration_present": True, "script_present": True, "timeline_present": True, "intelligence_present": True},
            "video": inspect_video(video_path),
            "passed": True,
        }
        if not isinstance(report["video"], dict):
            raise QAStageError("Video inspector must return an object")
        if report["video"].get("valid") is False:
            report["passed"] = False
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        if not report["passed"]:
            raise QAStageError("QA checks failed")

    run_bound_stage(root, movie_id, StageBinding("qa", artifact.as_posix(), work))
    return json.loads(destination.read_text(encoding="utf-8"))
