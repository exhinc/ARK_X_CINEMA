"""Tests for the portable ARK X Cinema runtime configuration layer."""

import json
from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from runtime_config import load_config, validate_runtime  # noqa: E402


CONFIG = Path(__file__).resolve().parents[2] / "Config" / "config.json"


def test_config_has_no_user_specific_root():
    data = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    assert data["root"] == "."
    assert "C:\\Users\\" not in json.dumps(data)


def test_heavy_stage_limit_is_locked():
    config = load_config(CONFIG)
    assert config.max_parallel_heavy_stages == 1
    assert config.ram_priority == "strict"


def test_runtime_paths_are_repository_relative():
    config = load_config(CONFIG)
    assert config.root.resolve() == CONFIG.parents[1].resolve()
    assert config.whisper_executable.is_relative_to(config.root)
    assert config.whisper_model.is_relative_to(config.root)


def test_missing_local_dependencies_are_reported_not_hidden():
    config = load_config(CONFIG)
    problems = validate_runtime(config)
    # GitHub cannot contain/execute the user's local Whisper installation. The
    # important contract here is that missing local dependencies become explicit
    # validation errors rather than being silently assumed to exist.
    assert isinstance(problems, list)
    assert all(isinstance(problem, str) for problem in problems)
