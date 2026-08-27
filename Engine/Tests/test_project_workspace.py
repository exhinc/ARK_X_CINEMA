"""Tests for canonical per-movie workspace/manifest behavior."""

import json
from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from project_workspace import create_workspace, safe_movie_id  # noqa: E402


def test_movie_id_is_deterministic():
    assert safe_movie_id("The Matrix: Reloaded!") == "the_matrix_reloaded"


def test_workspace_is_isolated(tmp_path, monkeypatch):
    import project_workspace
    monkeypatch.setattr(project_workspace, "PROJECTS_ROOT", tmp_path / "Projects")
    workspace = create_workspace("Movie A")
    assert workspace == (tmp_path / "Projects" / "movie_a").resolve()
    for name in ("source", "transcripts", "subtitles", "scenes", "analysis", "script", "narration", "edit", "qa", "artifacts", "logs"):
        assert (workspace / name).is_dir()


def test_manifest_requires_exactly_one_video(tmp_path, monkeypatch):
    import project_workspace
    monkeypatch.setattr(project_workspace, "PROJECTS_ROOT", tmp_path / "Projects")
    package = tmp_path / "package"
    package.mkdir()
    (package / "movie.mkv").write_bytes(b"fake")
    (package / "movie2.mkv").write_bytes(b"fake")
    try:
        project_workspace.build_source_manifest(package)
    except ValueError as exc:
        assert "exactly one movie video" in str(exc)
    else:
        raise AssertionError("Ambiguous package was accepted")


def test_manifest_records_ad_separately(tmp_path, monkeypatch):
    import project_workspace
    monkeypatch.setattr(project_workspace, "PROJECTS_ROOT", tmp_path / "Projects")
    package = tmp_path / "package"
    package.mkdir()
    (package / "movie.mkv").write_bytes(b"movie")
    (package / "movie.srt").write_bytes(b"1\n00:00:00,000 --> 00:00:01,000\nHello\n")
    (package / "movie_AD.mp3").write_bytes(b"ad")
    # Patch hashing to avoid depending on media validity; discovery itself is filesystem-based.
    monkeypatch.setattr(project_workspace, "sha256_file", lambda path: "testhash")
    manifest = project_workspace.build_source_manifest(package)
    assert len(manifest["subtitles"]) == 1
    assert len(manifest["ad_audio"]) == 1
    assert manifest["ad_audio"][0]["name"] == "movie_AD.mp3"
    saved = json.loads((Path(manifest["workspace"]) / "source_manifest.json").read_text(encoding="utf-8"))
    assert saved["movie_id"] == "movie"
