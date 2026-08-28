"""Local Ollama recap-script generation built on canonical intelligence artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from movie_intelligence import build_intelligence_schema
from structured_output import StructuredOutputError, extract_json


@dataclass(frozen=True)
class RecapSegment:
    text: str
    timestamp: str
    scene_id: str


@dataclass(frozen=True)
class RecapScriptResult:
    text: str
    segments: list[RecapSegment]


class RecapScriptError(RuntimeError):
    """Raised when the local model cannot produce a valid grounded recap."""


def _endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    return base if base.endswith("/api/generate") else f"{base}/api/generate"


def _timestamp_seconds(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".")
    parts = text.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return float(h) * 3600 + float(m) * 60 + float(s)
    if len(parts) == 2:
        m, s = parts
        return float(m) * 60 + float(s)
    raise ValueError(f"Invalid timestamp: {value}")


def _evidence_context(intelligence: list[dict[str, Any]]) -> str:
    records: list[str] = []
    for item in intelligence:
        intel = item.get("intelligence")
        if not isinstance(intel, dict):
            raise RecapScriptError("Intelligence record is missing its intelligence object")
        records.append(
            json.dumps(
                {
                    "scene_id": item.get("scene_id"),
                    "start": item.get("start"),
                    "end": item.get("end"),
                    "intelligence": intel,
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(records)


def _validate_segments(raw: Any, intelligence: list[dict[str, Any]]) -> list[RecapSegment]:
    if not isinstance(raw, list) or not raw:
        raise RecapScriptError("Recap generation returned no segments")

    scene_ranges: list[tuple[str, float, float]] = []
    for item in intelligence:
        try:
            start = _timestamp_seconds(item["start"])
            end = _timestamp_seconds(item["end"])
            scene_id = str(item["scene_id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise RecapScriptError("Intelligence contains an invalid scene range") from exc
        if end < start:
            raise RecapScriptError("Intelligence contains a reversed scene range")
        scene_ranges.append((scene_id, start, end))

    validated: list[RecapSegment] = []
    previous_time = -1.0
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise RecapScriptError(f"Recap segment {index} is not an object")
        text = str(item.get("text", "")).strip()
        timestamp = str(item.get("timestamp", "")).strip()
        scene_id = str(item.get("scene_id", "")).strip()
        if not text or not timestamp or not scene_id:
            raise RecapScriptError(f"Recap segment {index} is missing text, timestamp, or scene_id")
        try:
            point = _timestamp_seconds(timestamp)
        except ValueError as exc:
            raise RecapScriptError(f"Recap segment {index} has an invalid timestamp") from exc
        if point < previous_time:
            raise RecapScriptError("Recap segment timestamps are not chronological")
        matching = any(
            scene_id == known_scene_id and start <= point <= end
            for known_scene_id, start, end in scene_ranges
        )
        if not matching:
            raise RecapScriptError(
                f"Recap segment {index} timestamp is outside its declared scene evidence"
            )
        validated.append(RecapSegment(text=text, timestamp=timestamp, scene_id=scene_id))
        previous_time = point
    return validated


def generate_recap(
    intelligence: list[dict[str, Any]],
    model: str,
    *,
    base_url: str = "http://127.0.0.1:11434/api/generate",
    timeout_seconds: int = 180,
) -> RecapScriptResult:
    """Generate an original, timestamped recap using only supplied intelligence."""
    if not intelligence:
        raise RecapScriptError("No intelligence records supplied")
    if not model.strip():
        raise RecapScriptError("model must not be empty")
    if timeout_seconds <= 0:
        raise RecapScriptError("timeout_seconds must be positive")

    output_schema = {
        "segments": [
            {
                "text": "string",
                "timestamp": "string copied from evidence timing",
                "scene_id": "string copied from evidence",
            }
        ]
    }
    prompt = (
        "You are the ARK X Cinema evidence-grounded recap writer.\n"
        "Use ONLY the supplied structured movie intelligence. Never invent plot facts, characters, "
        "events, motivations, or timestamps. Write original narration rather than copying dialogue.\n"
        "Return ONLY one JSON object with a 'segments' array. Each segment must contain text, timestamp, "
        "and scene_id. The timestamp and scene_id MUST be copied from the supplied evidence, and segments "
        "must be chronological. Every sentence must be supportable by its associated intelligence record.\n\n"
        f"OUTPUT SCHEMA:\n{json.dumps(output_schema, ensure_ascii=False)}\n\n"
        f"CANONICAL INTELLIGENCE SCHEMA:\n{json.dumps(build_intelligence_schema(), ensure_ascii=False)}\n\n"
        f"INTELLIGENCE:\n{_evidence_context(intelligence)}"
    )
    payload = json.dumps(
        {"model": model, "prompt": prompt, "stream": False, "format": "json"},
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(
        _endpoint(base_url),
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            envelope = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RecapScriptError(f"Ollama HTTP error {exc.code}") from exc
    except URLError as exc:
        raise RecapScriptError(f"Ollama unavailable: {exc.reason}") from exc
    except TimeoutError as exc:
        raise RecapScriptError("Ollama request timed out") from exc
    except json.JSONDecodeError as exc:
        raise RecapScriptError(f"Ollama returned invalid JSON envelope: {exc}") from exc

    if not isinstance(envelope, dict):
        raise RecapScriptError("Ollama response envelope must be an object")
    raw = str(envelope.get("response", ""))
    try:
        parsed = extract_json(raw, expected_type=dict)
    except StructuredOutputError as exc:
        raise RecapScriptError(str(exc)) from exc

    segments = _validate_segments(parsed.get("segments"), intelligence)
    text = " ".join(segment.text for segment in segments).strip()
    if not text:
        raise RecapScriptError("Recap generation produced empty narration text")
    return RecapScriptResult(text=text, segments=segments)


def generate_recap_text(intelligence: list[dict[str, Any]], model: str, **kwargs: Any) -> str:
    """Compatibility helper returning only narration text for the stage adapter."""
    return generate_recap(intelligence, model, **kwargs).text
