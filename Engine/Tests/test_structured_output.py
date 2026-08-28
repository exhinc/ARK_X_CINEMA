"""Regression tests for model structured-output parsing."""

from pathlib import Path
import sys

import pytest

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE))

from structured_output import StructuredOutputError, extract_json  # noqa: E402


def test_extracts_object_from_markdown_fence():
    assert extract_json('```json\n{"ok": true}\n```', expected_type=dict) == {"ok": True}


def test_extracts_object_with_leading_and_trailing_prose():
    text = 'Here is the JSON:\n{"ok": true}\nDone.'
    assert extract_json(text, expected_type=dict) == {"ok": True}


def test_extracts_array():
    assert extract_json('prefix [1, 2, 3] suffix', expected_type=list) == [1, 2, 3]


def test_malformed_output_fails_closed_with_stable_prefix():
    with pytest.raises(StructuredOutputError, match=r"^JSON parsing failed"):
        extract_json('{"broken"', expected_type=dict)


def test_wrong_json_type_fails_closed():
    with pytest.raises(StructuredOutputError, match=r"^JSON parsing failed"):
        extract_json('[1, 2]', expected_type=dict)
