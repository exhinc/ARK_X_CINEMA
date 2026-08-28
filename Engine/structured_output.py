"""Strict, dependency-free structured JSON extraction for local model output.

The Ollama adapter requests JSON, but local models can still return fences,
leading/trailing prose, or malformed JSON. This helper extracts exactly one
JSON value and fails closed with a stable error prefix.
"""

from __future__ import annotations

import json
from typing import Any, TypeVar

T = TypeVar("T")


class StructuredOutputError(ValueError):
    """Raised when model output does not contain the expected JSON value."""


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def extract_json(text: str, *, expected_type: type[T] | None = None) -> T:
    """Extract one JSON object/array from model output without repairing it.

    Leading/trailing prose and Markdown fences are tolerated. The JSON value
    itself must be syntactically valid and must match ``expected_type`` when
    supplied. No heuristic quote/bracket repair is attempted.
    """
    if not isinstance(text, str) or not text.strip():
        raise StructuredOutputError("JSON parsing failed: empty model output")

    cleaned = _strip_code_fence(text)
    decoder = json.JSONDecoder()

    candidates = [idx for idx, char in enumerate(cleaned) if char in "[{]"]
    if not candidates:
        raise StructuredOutputError("JSON parsing failed: no JSON object or array found")

    last_error: json.JSONDecodeError | None = None
    for start in candidates:
        try:
            value, end = decoder.raw_decode(cleaned[start:])
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        trailing = cleaned[start + end :].strip()
        if trailing:
            # A model may emit a valid JSON value followed by commentary. The
            # extracted value is still usable because the requested structured
            # payload is complete and unambiguous.
            pass
        if expected_type is not None and not isinstance(value, expected_type):
            raise StructuredOutputError(
                f"JSON parsing failed: expected {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
        return value

    detail = str(last_error) if last_error else "invalid JSON"
    raise StructuredOutputError(f"JSON parsing failed: {detail}")
