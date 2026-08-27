"""Run the evidence-first movie intelligence stage for an existing project.

This is intentionally a separate stage runner: it does not replace the main
orchestrator and therefore cannot accidentally remove existing ingestion logic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from intelligence_pipeline import analyze_timeline, write_intelligence_artifact
from runtime_config import load_config, validate_runtime


def load_timeline(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_stage(timeline_path: Path, output_path: Path, model: str | None = None) -> dict:
    config = load_config()
    problems = validate_runtime(config)
    if problems:
        raise RuntimeError("Runtime validation failed:\n- " + "\n- ".join(problems))

    selected_model = model or config.ollama_model
    artifact = analyze_timeline(
        load_timeline(timeline_path),
        model=selected_model,
        base_url=config.ollama_url,
    )
    write_intelligence_artifact(artifact, output_path)
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ARK X Cinema evidence-first Ollama intelligence.")
    parser.add_argument("timeline", type=Path, help="Canonical timeline JSON")
    parser.add_argument("output", type=Path, help="Intelligence artifact JSON")
    parser.add_argument("--model", default=None, help="Override configured Ollama model")
    args = parser.parse_args()
    artifact = run_stage(args.timeline, args.output, args.model)
    print(json.dumps({k: artifact[k] for k in ("status", "model", "processed_packets", "total_packets")}, indent=2))
    return 0 if artifact["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
