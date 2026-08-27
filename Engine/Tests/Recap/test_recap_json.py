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
    blocks = re.split(r"\n\s*\n", text.strip())

    items = []

    for block in blocks:
        lines = [x.strip() for x in block.splitlines() if x.strip()]

        if len(lines) < 3:
            continue

        if not lines[0].isdigit():
            continue

        timestamp = lines[1]
        subtitle_text = " ".join(lines[2:]).strip()

        if "-->" not in timestamp:
            continue

        start = timestamp.split("-->")[0].strip()

        items.append({
            "start": start,
            "text": subtitle_text
        })

    return items


def timestamp_to_seconds(timestamp):
    timestamp = timestamp.strip()

    parts = timestamp.split(":")

    if len(parts) != 3:
        raise ValueError("Invalid timestamp")

    hours = int(parts[0])
    minutes = int(parts[1])

    seconds = float(parts[2].replace(",", "."))

    return hours * 3600 + minutes * 60 + seconds


def ollama_generate(prompt):
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=900
    ) as response:

        data = json.loads(
            response.read().decode("utf-8")
        )

    return data.get("response", "").strip()


print("=" * 70)
print("ARK X CINEMA — RECAP JSON CHECKPOINT")
print("=" * 70)
print()

print(f"SRT: {SRT}")
print(f"MODEL: {MODEL}")
print()

if not SRT.exists():
    raise RuntimeError(f"AD SRT not found: {SRT}")

items = parse_srt(SRT)

if not items:
    raise RuntimeError("No usable SRT entries found.")

sample = items[:15]

print(f"Total SRT entries: {len(items)}")
print(f"Testing first {len(sample)} entries")
print()

movie_title = "The Platform (2019)"

notes = "\n\n".join(
    f"[{item['start']}] {item['text']}"
    for item in sample
)

prompt = f"""
Write an original YouTube movie recap narration.

Movie:
{movie_title}

Use ONLY the supplied movie intelligence.

Requirements:

- chronological storytelling
- clear cause and effect
- important characters
- important decisions
- major reveals
- turning points
- engaging narration
- original wording
- no screenplay dialogue
- no invented facts
- no review
- no discussion of these instructions

CRITICAL OUTPUT FORMAT:

Return ONLY a JSON array. Each element is one narration
segment, in chronological order:

[
  {{"text": "narration sentence(s) for this beat",
    "timestamp": "HH:MM:SS"}},
  ...
]

The "timestamp" must be a real timestamp copied from the
supplied movie intelligence, marking roughly where in the
movie this narration beat corresponds to visually.

Return ONLY the JSON array. No commentary. No markdown
fences.

MOVIE INTELLIGENCE:
{notes}
"""

print("Sending production-style prompt to Llama...")
print()

start_time = time.time()

response = ollama_generate(prompt)

elapsed = round(time.time() - start_time, 2)

RAW_OUTPUT.write_text(
    response,
    encoding="utf-8"
)

print(f"Generation time: {elapsed} seconds")
print()
print("===== RAW MODEL RESPONSE =====")
print(response)
print()
print("=" * 70)

cleaned = response.strip()

if cleaned.startswith("```"):
    cleaned = cleaned.strip("`")
    cleaned = cleaned.replace("json", "", 1).strip()

result = {
    "passed": False,
    "model": MODEL,
    "movie": movie_title,
    "sample_entries": len(sample),
    "generation_seconds": elapsed,
    "segments": [],
    "errors": []
}

try:
    segments = json.loads(cleaned)

except json.JSONDecodeError as exc:
    result["errors"].append(
        f"JSON parsing failed: {exc}"
    )

    OUTPUT.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )

    print("RESULT: FAIL — INVALID JSON")
    print(f"Report: {OUTPUT}")
    print(f"Raw response: {RAW_OUTPUT}")
    raise SystemExit(1)


if not isinstance(segments, list):
    result["errors"].append(
        "Model output is not a JSON array."
    )


if isinstance(segments, list):

    for index, entry in enumerate(segments, start=1):

        if not isinstance(entry, dict):
            result["errors"].append(
                f"Segment {index} is not an object."
            )
            continue

        text = str(entry.get("text", "")).strip()
        timestamp = str(
            entry.get("timestamp", "")
        ).strip()

        if not text:
            result["errors"].append(
                f"Segment {index} has no text."
            )

        if not timestamp:
            result["errors"].append(
                f"Segment {index} has no timestamp."
            )
            continue

        try:
            seconds = timestamp_to_seconds(timestamp)
        except Exception:
            result["errors"].append(
                f"Segment {index} has invalid timestamp: {timestamp}"
            )
            continue

        result["segments"].append({
            "text": text,
            "timestamp": timestamp,
            "seconds": seconds
        })

if not result["segments"]:
    result["errors"].append(
        "No valid timestamped segments were produced."
    )

if not result["errors"] and result["segments"]:
    result["passed"] = True

OUTPUT.write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print()
print("===== VALIDATION =====")
print(f"Segments returned: {len(result['segments'])}")
print(f"Validation errors: {len(result['errors'])}")

if result["errors"]:
    print()
    for error in result["errors"]:
        print(f"ERROR: {error}")

    print()
    print("RESULT: FAIL")
    print(f"Report: {OUTPUT}")
    print(f"Raw response: {RAW_OUTPUT}")
    raise SystemExit(1)

print()
print("RESULT: PASS")
print()
print("The model produced valid JSON with usable timestamps.")
print(f"Report: {OUTPUT}")
print(f"Raw response: {RAW_OUTPUT}")
print("=" * 70)
