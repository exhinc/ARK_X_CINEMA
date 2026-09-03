"""Canonical command-line entry point for ARK X Cinema production runs."""

from __future__ import annotations

import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
ROOT = ENGINE.parent
sys.path.insert(0, str(ENGINE))

from stage_a_runner import StageARunnerError, run_stage_a  # noqa: E402

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".webm",
    ".m4v",
    ".ts",
    ".mts",
    ".m2ts",
    ".wmv",
    ".flv",
    ".ogv",
}


def discover_source() -> Path:
    """Return the single movie source under Movies or raise a clear error."""
    movies = ROOT / "Movies"
    movies.mkdir(parents=True, exist_ok=True)

    sources: list[Path] = []
    for item in sorted(movies.iterdir()):
        if item.is_file() and item.suffix.lower() in VIDEO_EXTENSIONS:
            sources.append(item)
            continue
        if item.is_dir():
            videos = [
                path
                for path in item.rglob("*")
                if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
            ]
            if videos:
                sources.append(item)

    if not sources:
        raise StageARunnerError(f"No usable movie source found under: {movies}")
    if len(sources) != 1:
        names = ", ".join(str(path.name) for path in sources[:10])
        raise StageARunnerError(
            "Expected exactly one movie source for a production run; "
            f"found {len(sources)}: {names}"
        )
    return sources[0].resolve()


def main() -> int:
    source = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else discover_source()
    if not source.exists():
        raise StageARunnerError(f"Production source does not exist: {source}")

    workspace = run_stage_a(source)
    print(f"ARK X Cinema production completed: {workspace}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StageARunnerError as exc:
        print(f"ARK X Cinema production failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
