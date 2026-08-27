"""Canonical subtitle and Audio Description ingestion helpers.

AD remains audio-first by design: an AD audio file is transcribed with
whisper.cpp into a timestamped SRT. This module never treats an AD SRT as a
substitute for the AD audio path.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Iterable

SRT_TIMESTAMP = re.compile(r"^(\d{2}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2},\d{3})")
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma", ".ac3", ".eac3"}


def validate_srt(path: Path) -> list[str]:
    """Return validation errors; an empty list means the SRT is structurally valid."""
    errors: list[str] = []
    if not path.exists():
        return [f"SRT does not exist: {path}"]
    text = path.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if not blocks:
        return [f"SRT is empty: {path}"]
    previous_end = None
    for number, block in enumerate(blocks, 1):
        lines = block.split("\n")
        if len(lines) < 3 or not lines[0].strip().isdigit():
            errors.append(f"Block {number}: invalid cue number")
            continue
        match = SRT_TIMESTAMP.match(lines[1].strip())
        if not match:
            errors.append(f"Block {number}: invalid timestamp line")
            continue
        start, end = match.groups()
        start_ms, end_ms = _timestamp_ms(start), _timestamp_ms(end)
        if start_ms >= end_ms:
            errors.append(f"Block {number}: start must be before end")
        if previous_end is not None and start_ms < previous_end:
            errors.append(f"Block {number}: cue overlaps/reverses previous cue")
        previous_end = end_ms
        if not any(line.strip() for line in lines[2:]):
            errors.append(f"Block {number}: empty cue text")
    return errors


def _timestamp_ms(value: str) -> int:
    h, m, rest = value.split(":")
    s, ms = rest.split(",")
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)


def normalize_srt(source: Path, destination: Path) -> Path:
    """Copy a UTF-8-normalized SRT after structural validation."""
    errors = validate_srt(source)
    if errors:
        raise ValueError("Invalid SRT:\n- " + "\n- ".join(errors))
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = source.read_text(encoding="utf-8-sig", errors="replace")
    destination.write_text(text.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n", encoding="utf-8")
    return destination


def classify_external_subtitles(files: Iterable[Path], movie_stem: str) -> list[Path]:
    """Return subtitle candidates deterministically, strongest filename matches first."""
    stem = movie_stem.lower()
    candidates = [Path(p) for p in files]

    def score(path: Path) -> tuple[int, str]:
        name = path.stem.lower()
        exact = int(name == stem)
        contains = int(stem in name or name in stem)
        english = int(any(token in name for token in ("en", "eng", "english")))
        return (exact * 100 + contains * 10 + english, name)

    return sorted(candidates, key=score, reverse=True)


def find_ad_audio(files: Iterable[Path]) -> list[Path]:
    """Find likely external AD audio; non-audio files, including AD SRTs, are excluded."""
    result: list[Path] = []
    for path in files:
        p = Path(path)
        if p.suffix.lower() not in AUDIO_EXTENSIONS:
            continue
        normalized = re.sub(r"[^a-z0-9]+", " ", p.stem.lower()).strip()
        tokens = set(normalized.split())
        if {"ad", "audiodescription", "descriptive"} & tokens or "audio description" in normalized or "descriptive audio" in normalized:
            result.append(p)
    return sorted(result, key=lambda p: p.name.lower())


def transcribe_ad_to_srt(ad_audio: Path, output_srt: Path, whisper_executable: Path, whisper_model: Path, ffmpeg_executable: str = "ffmpeg") -> Path:
    """Run whisper.cpp against AD audio and require a valid timestamped SRT."""
    if not ad_audio.exists():
        raise FileNotFoundError(f"AD audio not found: {ad_audio}")
    if ad_audio.suffix.lower() not in AUDIO_EXTENSIONS:
        raise ValueError(f"AD input must be an audio file, not {ad_audio.suffix}")
    if not whisper_executable.exists():
        raise FileNotFoundError(f"Whisper executable not found: {whisper_executable}")
    if not whisper_model.exists():
        raise FileNotFoundError(f"Whisper model not found: {whisper_model}")
    output_srt.parent.mkdir(parents=True, exist_ok=True)
    temp_wav = output_srt.with_suffix(".ad16k.wav")
    try:
        convert = subprocess.run([ffmpeg_executable, "-y", "-i", str(ad_audio), "-ar", "16000", "-ac", "1", str(temp_wav)], text=True, capture_output=True, encoding="utf-8", errors="replace", check=False)
        if convert.returncode != 0:
            raise RuntimeError("FFmpeg failed while preparing AD audio for whisper.cpp")
        result = subprocess.run([str(whisper_executable), "-m", str(whisper_model), "-f", str(temp_wav), "-osrt", "-of", str(output_srt.with_suffix(""))], text=True, capture_output=True, encoding="utf-8", errors="replace", check=False)
        if result.returncode != 0:
            raise RuntimeError("whisper.cpp failed to transcribe AD audio")
        if not output_srt.exists():
            raise RuntimeError(f"whisper.cpp completed without creating SRT: {output_srt}")
        errors = validate_srt(output_srt)
        if errors:
            raise RuntimeError("whisper.cpp produced invalid SRT:\n- " + "\n- ".join(errors))
        return output_srt
    finally:
        if temp_wav.exists():
            temp_wav.unlink()
