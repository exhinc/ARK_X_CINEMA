"""Manual Ollama recap checkpoint; not a portable CI test.

This checkpoint depends on a local movie/AD SRT and a running Ollama server, so
it must be executed on the Windows workstation during the local integration
phase rather than during repository-only CI.
"""

import pytest

pytest.skip("Manual local Ollama recap checkpoint; requires local movie data and Ollama", allow_module_level=True)

# Original manual checkpoint implementation is intentionally retained below the
# module-level CI skip for local execution/reference.
import json
import re
import urllib.request
import time
from pathlib import Path

ROOT = Path(r"C:\Users\owena\Desktop\ARK_X_CINEMA")
SRT = ROOT / r"Movies\The Platform (2019)\The Platform (2019) Audio Description (AD).mp3.srt"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2:1b"
OUTPUT = ROOT / "test_recap_json_result.json"
RAW_OUTPUT = ROOT / "test_recap_json_raw.txt"

def parse_srt(path):
    text = path.read_text(encoding="utf-8-sig")
    items = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [x.strip() for x in block.splitlines() if x.strip()]
        if len(lines) < 3 or not lines[0].isdigit() or "-->" not in lines[1]:
            continue
        items.append({"start": lines[1].split("-->")[0].strip(), "text": " ".join(lines[2:]).strip()})
    return items

def timestamp_to_seconds(timestamp):
    parts = timestamp.strip().split(":")
    if len(parts) != 3:
        raise ValueError("Invalid timestamp")
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2].replace(",", "."))

def ollama_generate(prompt):
    payload = json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode("utf-8")
    request = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=900) as response:
        return json.loads(response.read().decode("utf-8")).get("response", "").strip()

if __name__ == "__main__":
    if not SRT.exists():
        raise RuntimeError(f"AD SRT not found: {SRT}")
    items = parse_srt(SRT)
    if not items:
        raise RuntimeError("No usable SRT entries found.")
    notes = "\n\n".join(f"[{item['start']}] {item['text']}" for item in items[:15])
    prompt = f'''Write an original YouTube movie recap narration using ONLY this movie intelligence. Return ONLY a JSON array with objects containing text and timestamp. Movie: The Platform (2019).\n\nMOVIE INTELLIGENCE:\n{notes}'''
    response = ollama_generate(prompt)
    RAW_OUTPUT.write_text(response, encoding="utf-8")
    cleaned = response.strip().strip("`")
    if cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()
    segments = json.loads(cleaned)
    result = {"passed": False, "model": MODEL, "movie": "The Platform (2019)", "segments": [], "errors": []}
    if not isinstance(segments, list):
        result["errors"].append("Model output is not a JSON array.")
    else:
        for index, entry in enumerate(segments, 1):
            if not isinstance(entry, dict):
                result["errors"].append(f"Segment {index} is not an object.")
                continue
            text = str(entry.get("text", "")).strip()
            timestamp = str(entry.get("timestamp", "")).strip()
            if not text or not timestamp:
                result["errors"].append(f"Segment {index} missing text or timestamp.")
                continue
            try:
                seconds = timestamp_to_seconds(timestamp)
            except Exception:
                result["errors"].append(f"Segment {index} has invalid timestamp: {timestamp}")
                continue
            result["segments"].append({"text": text, "timestamp": timestamp, "seconds": seconds})
    result["passed"] = not result["errors"] and bool(result["segments"])
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    if not result["passed"]:
        raise SystemExit(1)
