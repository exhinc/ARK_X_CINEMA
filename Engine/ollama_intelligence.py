"""Optional local Ollama adapter for ARK X Cinema intelligence inference."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from structured_output import StructuredOutputError, extract_json


@dataclass(frozen=True)
class OllamaResult:
    model: str
    response: str
    parsed: dict[str, Any]
    duration_ms: int | None = None


class OllamaError(RuntimeError):
    """Raised when local Ollama cannot produce a valid intelligence response."""


def _endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    return base if base.endswith("/api/generate") else f"{base}/api/generate"


def _validate_intelligence(data: dict[str, Any]) -> None:
    required = {
        "summary", "characters", "location", "actions", "dialogue_points",
        "visual_description_points", "cause_effect", "importance", "confidence",
        "unsupported_claims",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise OllamaError(f"LLM output missing required fields: {', '.join(missing)}")
    if not isinstance(data["summary"], str):
        raise OllamaError("LLM field 'summary' must be a string")
    if data["location"] is not None and not isinstance(data["location"], str):
        raise OllamaError("LLM field 'location' must be a string or null")
    if not isinstance(data["confidence"], (int, float)) or isinstance(data["confidence"], bool) or not 0 <= float(data["confidence"]) <= 1:
        raise OllamaError("LLM field 'confidence' must be a number from 0 to 1")
    for field in ("characters", "actions", "dialogue_points", "visual_description_points", "cause_effect", "unsupported_claims"):
        if not isinstance(data[field], list) or not all(isinstance(x, str) for x in data[field]):
            raise OllamaError(f"LLM field '{field}' must be an array of strings")
    if not isinstance(data["importance"], str):
        raise OllamaError("LLM field 'importance' must be a string")


def infer_scene(packet: dict[str, Any], model: str, base_url: str = "http://127.0.0.1:11434/api/generate", timeout_seconds: int = 120) -> OllamaResult:
    """Send one evidence packet to Ollama and validate its structured JSON output."""
    if not model.strip():
        raise ValueError("model must not be empty")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    schema = {
        "summary": "string",
        "characters": ["string"],
        "location": "string or null",
        "actions": ["string"],
        "dialogue_points": ["string"],
        "visual_description_points": ["string"],
        "cause_effect": ["string"],
        "importance": "string",
        "confidence": "number 0..1",
        "unsupported_claims": ["string"],
    }
    schema_text = json.dumps(schema, ensure_ascii=False)
    packet_text = json.dumps(packet, ensure_ascii=False)
    prompt = (
        "You are the ARK X Cinema evidence-first movie intelligence engine.\n"
        "Use ONLY the evidence supplied below. Never invent facts. If evidence does not support a fact, "
        "leave it out or put it in unsupported_claims. Return ONLY one JSON object matching the requested fields.\n\n"
        f"REQUESTED SCHEMA:\n{schema_text}\n\n"
        f"EVIDENCE PACKET:\n{packet_text}"
    )
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False, "format": "json"}).encode("utf-8")
    request = Request(_endpoint(base_url), data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        raise OllamaError(f"Ollama HTTP error {exc.code}") from exc
    except URLError as exc:
        raise OllamaError(f"Ollama unavailable: {exc.reason}") from exc
    except TimeoutError as exc:
        raise OllamaError("Ollama request timed out") from exc

    try:
        envelope = json.loads(raw)
        if not isinstance(envelope, dict):
            raise StructuredOutputError("JSON parsing failed: Ollama envelope must be an object")
        text = str(envelope.get("response", ""))
        parsed = extract_json(text, expected_type=dict)
    except (json.JSONDecodeError, TypeError) as exc:
        raise OllamaError(f"Ollama returned invalid JSON: {exc}") from exc
    except StructuredOutputError as exc:
        raise OllamaError(str(exc)) from exc

    _validate_intelligence(parsed)
    duration_ms = envelope.get("total_duration")
    duration_ms = duration_ms // 1_000_000 if isinstance(duration_ms, int) else None
    return OllamaResult(model=model, response=text, parsed=parsed, duration_ms=duration_ms)
