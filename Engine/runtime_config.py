"""Runtime configuration and dependency discovery for ARK X Cinema.

This module is intentionally independent from the production orchestrator so it can
be unit-tested before being wired into the remaining pipeline stages.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "Config" / "config.json"


@dataclass(frozen=True)
class RuntimeConfig:
    root: Path
    whisper_executable: Path
    whisper_model: Path
    ollama_url: str
    ollama_model: str
    max_parallel_heavy_stages: int
    ram_priority: str


def _path_from_config(root: Path, value: str | None, default_relative: str) -> Path:
    """Resolve a configured path without depending on a specific Windows user."""
    raw = value or default_relative
    path = Path(os.path.expandvars(os.path.expanduser(raw)))
    return path if path.is_absolute() else root / path


def load_config(config_file: Path = CONFIG_FILE) -> RuntimeConfig:
    """Load and normalize ARK X Cinema runtime configuration."""
    data = json.loads(config_file.read_text(encoding="utf-8-sig"))

    configured_root = data.get("root")
    root = ROOT if not configured_root else _path_from_config(ROOT, configured_root, ".")

    # A root that points at this repository is canonical. Absolute legacy roots are
    # accepted for backwards compatibility but are not allowed to control launcher
    # location; callers should prefer the repository root.
    if configured_root in (None, "", ".", "./"):
        root = ROOT

    whisper_root = _path_from_config(root, data.get("whisper_root"), "Tools/Whisper")
    whisper_executable = _path_from_config(
        root,
        data.get("whisper_executable"),
        "Tools/Whisper/whisper-cli.exe",
    )
    whisper_model = _path_from_config(
        root,
        data.get("whisper_model"),
        "Tools/Whisper/ggml-base.en.bin",
    )

    # If an explicit whisper_root is supplied, preserve the documented executable
    # and model defaults relative to it unless explicit paths override them.
    if not data.get("whisper_executable"):
        whisper_executable = whisper_root / "whisper-cli.exe"
    if not data.get("whisper_model"):
        whisper_model = whisper_root / "ggml-base.en.bin"

    limits = data.get("limits", {})
    max_parallel = int(limits.get("max_parallel_heavy_stages", 1))
    if max_parallel != 1:
        raise ValueError("ARK X Cinema requires max_parallel_heavy_stages=1")

    ram_priority = str(limits.get("ram_priority", "strict"))
    if ram_priority != "strict":
        raise ValueError("ARK X Cinema requires strict RAM priority")

    return RuntimeConfig(
        root=root,
        whisper_executable=whisper_executable,
        whisper_model=whisper_model,
        ollama_url=str(data.get("ollama_url", "http://127.0.0.1:11434/api/generate")),
        ollama_model=str(data.get("ollama_model", "qwen3:1.7b")),
        max_parallel_heavy_stages=max_parallel,
        ram_priority=ram_priority,
    )


def validate_runtime(config: RuntimeConfig) -> list[str]:
    """Return actionable configuration/runtime errors without executing tools."""
    errors: list[str] = []

    if not config.root.exists():
        errors.append(f"Repository root does not exist: {config.root}")

    if not config.whisper_executable.exists():
        errors.append(f"Whisper executable not found: {config.whisper_executable}")

    if not config.whisper_model.exists():
        errors.append(f"Whisper model not found: {config.whisper_model}")

    if config.max_parallel_heavy_stages != 1:
        errors.append("max_parallel_heavy_stages must remain 1")

    return errors


if __name__ == "__main__":
    cfg = load_config()
    problems = validate_runtime(cfg)
    print(f"ARK X Cinema root: {cfg.root}")
    print(f"Whisper executable: {cfg.whisper_executable}")
    print(f"Whisper model: {cfg.whisper_model}")
    if problems:
        print("RUNTIME VALIDATION: FAIL")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)
    print("RUNTIME VALIDATION: PASS")
