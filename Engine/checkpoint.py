"""Crash-safe stage checkpointing for ARK X Cinema.

Checkpoints are small JSON state files written atomically so a failed run can
resume from the last completed stage without pretending incomplete work is done.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


SCHEMA_VERSION = 1


class CheckpointError(ValueError):
    """Raised when checkpoint state is invalid or cannot be persisted."""


@dataclass(frozen=True)
class Checkpoint:
    movie_id: str
    stage: str
    status: str
    schema_version: int = SCHEMA_VERSION
    artifact: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "movie_id": self.movie_id,
            "stage": self.stage,
            "status": self.status,
            "artifact": self.artifact,
            "error": self.error,
        }


def _validate(data: dict[str, Any]) -> Checkpoint:
    required = ("movie_id", "stage", "status")
    missing = [key for key in required if not isinstance(data.get(key), str) or not data[key].strip()]
    if missing:
        raise CheckpointError(f"Missing checkpoint fields: {', '.join(missing)}")
    if data.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        raise CheckpointError("Unsupported checkpoint schema version")
    if data["status"] not in {"running", "complete", "failed"}:
        raise CheckpointError(f"Invalid checkpoint status: {data['status']}")
    return Checkpoint(
        movie_id=data["movie_id"],
        stage=data["stage"],
        status=data["status"],
        schema_version=SCHEMA_VERSION,
        artifact=data.get("artifact"),
        error=data.get("error"),
    )


def save_checkpoint(path: Path, checkpoint: Checkpoint) -> Path:
    """Atomically replace a checkpoint file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(checkpoint.to_dict(), indent=2, ensure_ascii=False) + "\n"
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temp:
            temp.write(payload)
            temp.flush()
            os.fsync(temp.fileno())
            temporary = Path(temp.name)
        os.replace(temporary, path)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except UnboundLocalError:
            pass
        raise CheckpointError(f"Unable to save checkpoint: {exc}") from exc
    return path


def load_checkpoint(path: Path) -> Checkpoint | None:
    """Load a checkpoint, returning None when it does not exist."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckpointError(f"Unable to read checkpoint: {exc}") from exc
    if not isinstance(data, dict):
        raise CheckpointError("Checkpoint root must be an object")
    return _validate(data)
