"""Tests for the canonical Stage-A production entry point."""

from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

import pytest

import run_production  # noqa: E402


def test_discover_source_returns_single_movie_file(tmp_path, monkeypatch):
    movies = tmp_path / "Movies"
    movies.mkdir()
    movie = movies / "Movie.mkv"
    movie.write_bytes(b"movie")
    monkeypatch.setattr(run_production, "ROOT", tmp_path)

    assert run_production.discover_source() == movie.resolve()


def test_discover_source_returns_single_movie_package(tmp_path, monkeypatch):
    movies = tmp_path / "Movies"
    package = movies / "Movie"
    package.mkdir(parents=True)
    movie = package / "Movie.mkv"
    movie.write_bytes(b"movie")
    monkeypatch.setattr(run_production, "ROOT", tmp_path)

    assert run_production.discover_source() == package.resolve()


def test_discover_source_rejects_multiple_sources(tmp_path, monkeypatch):
    movies = tmp_path / "Movies"
    movies.mkdir()
    (movies / "A.mkv").write_bytes(b"a")
    (movies / "B.mkv").write_bytes(b"b")
    monkeypatch.setattr(run_production, "ROOT", tmp_path)

    try:
        run_production.discover_source()
    except run_production.StageARunnerError as exc:
        assert "Expected exactly one movie source" in str(exc)
    else:
        raise AssertionError("Expected discover_source() to reject multiple sources")


def test_main_runs_stage_a_for_explicit_source(monkeypatch, tmp_path, capsys):
    source = tmp_path / "Movie"
    source.mkdir()
    workspace = tmp_path / "Projects" / "Movie"
    calls = []

    def fake_run_stage_a(path):
        calls.append(path)
        return workspace

    monkeypatch.setattr(run_production, "run_stage_a", fake_run_stage_a)
    monkeypatch.setattr(run_production.sys, "argv", ["run_production.py", str(source)])

    assert run_production.main() == 0
    assert calls == [source.resolve()]
    assert str(workspace) in capsys.readouterr().out


def test_main_rejects_missing_explicit_source(monkeypatch, tmp_path):
    source = tmp_path / "MissingMovie"
    monkeypatch.setattr(run_production.sys, "argv", ["run_production.py", str(source)])

    with pytest.raises(run_production.StageARunnerError, match="Production source does not exist"):
        run_production.main()
