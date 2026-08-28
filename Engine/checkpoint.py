"""Crash-safe, artifact-aware stage checkpointing for ARK X Cinema."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


SCHEMA_VERSION = 2


class CheckpointError(ValueError):
    """Raised when checkpoint state is invalid or cannot be persisted."""


@dataclass(frozen=True)
class Checkpoint:
    movie_id: str
    stage: str
    status: str
    schema_version: int = SCHEMA_VERSION
    artifact: str | None = None
    artifact_sha256: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "movie_id": self.movie_id,
            "stage": self.stage,
            "status": self.status,
            "artifact": self.artifact,
            "artifact_sha256": self.artifact_sha256,
            "error": self.error,
        }


def _validate(data: dict[str, Any]) -> Checkpoint:
    required = ("movie_id", "stage", "status")
    missing = [key for key in required if not isinstance(data.get(key), str) or not data[key].strip()]
    if missing:
        raise CheckpointError(f"Missing checkpoint fields: {', '.join(missing)}")
    if data.get("schema_version", 1) not in {1, SCHEMA_VERSION}:
        raise CheckpointError("Unsupported checkpoint schema version")
    if data["status"] not in {"running", "complete", "failed"}:
        raise CheckpointError(f"Invalid checkpoint status: {data['status']}")
    digest = data.get("artifact_sha256")
    if digest is not None and (not isinstance(digest, str) or len(digest) != 64):
        raise CheckpointError("Invalid artifact SHA-256")
    return Checkpoint(data["movie_id"], data["stage"], data["status"], SCHEMA_VERSION, data.get("artifact"), digest, data.get("error"))


def artifact_sha256(path: Path) -> str:
    """Return the SHA-256 digest of an artifact file."""
    if not path.is_file():
        raise CheckpointError(f"Artifact does not exist: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_checkpoint(path: Path, checkpoint: Checkpoint) -> Path:
    """Atomically replace a checkpoint file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(checkpoint.to_dict(), indent=2, ensure_ascii=False) + "\n"
    temporary: Path | None = None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as temp:
            temporary = Path(temp.name)
            temp.write(payload)
            temp.flush()
            os.fsync(temp.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
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


def artifact_is_intact(root: Path, checkpoint: Checkpoint) -> bool:
    """Verify a completed checkpoint's artifact exists and matches its digest."""
    if checkpoint.status != "complete" or not checkpoint.artifact or not checkpoint.artifact_sha256:
        return False
    path = root / checkpoint.artifact
    try:
        return artifact_sha256(path) == checkpoint.artifact_sha256
    except CheckpointError:
        return False
