"""Optional local Ollama adapter for ARK X Cinema intelligence inference."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


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
    if not isinstance(data["confidence"], (int, float)) or not 0 <= float(data["confidence"]) <= 1:
        raise OllamaError("LLM field 'confidence' must be a number from 0 to 1")
    for field in ("characters", "actions", "dialogue_points", "visual_description_points", "cause_effect", "unsupported_claims"):
        if not isinstance(data[field], list) or not all(isinstance(x, str) for x in data[field]):
            raise OllamaError(f"LLM field '{field}' must be an array of strings")


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
        text = str(envelope.get("response", ""))
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise OllamaError("Ollama returned invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise OllamaError("Ollama intelligence output must be a JSON object")
    _validate_intelligence(parsed)
    duration_ms = envelope.get("total_duration")
    duration_ms = duration_ms // 1_000_000 if isinstance(duration_ms, int) else None
    return OllamaResult(model=model, response=text, parsed=parsed, duration_ms=duration_ms)
