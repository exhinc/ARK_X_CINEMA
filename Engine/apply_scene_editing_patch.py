from pathlib import Path
from datetime import datetime

target = Path(r"C:\Users\owena\Desktop\ARK_X_CINEMA\Engine\orchestrator.py")
backup = Path(r"C:\Users\owena\Desktop\ARK_X_CINEMA\Backups") / f"orchestrator_before_scene_editing_{datetime.now():%Y%m%d_%H%M%S}.py"

text = target.read_text(encoding="utf-8")

# ============================================================
# 1. REPLACE generate_recap TO OUTPUT TIMESTAMPED JSON SEGMENTS
# ============================================================

old_generate_recap = '''def generate_recap(
    analysis,
    movie_title,
    project,
    model
):

    notes = "\\n\\n".join(
        item["notes"]
        for item in analysis
    )

    notes = notes[:50000]

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

Write ONLY the narration.

MOVIE INTELLIGENCE:
{notes}
"""

    response = ollama_generate(
        prompt,
        model
    )

    if not response:
        raise RuntimeError(
            "Ollama produced no recap."
        )

    output = (
        project /
        "recap_script.txt"
    )

    output.write_text(
        response,
        encoding="utf-8"
    )

    master = (
        DIRS["scripts"] /
        f"{safe_name(movie_title)}_recap.txt"
    )

    master.write_text(
        response,
        encoding="utf-8"
    )

    return output'''

new_generate_recap = '''def parse_timestamp_to_seconds(value):

    value = value.replace(",", ".")
    parts = value.split(":")

    if len(parts) == 3:
        h, m, s = parts
        return float(h) * 3600 + float(m) * 60 + float(s)

    if len(parts) == 2:
        m, s = parts
        return float(m) * 60 + float(s)

    raise ValueError(f"Invalid timestamp: {value}")


def generate_recap(
    analysis,
    movie_title,
    project,
    model
):

    notes = "\\n\\n".join(
        item["notes"]
        for item in analysis
    )

    notes = notes[:50000]

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

    response = ollama_generate(
        prompt,
        model
    )

    if not response:
        raise RuntimeError(
            "Ollama produced no recap."
        )

    cleaned = response.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    try:
        segments = json.loads(cleaned)

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Recap generation did not return valid JSON: {exc}"
        )

    if not isinstance(segments, list) or not segments:
        raise RuntimeError(
            "Recap generation returned no usable segments."
        )

    valid_segments = []

    for entry in segments:

        text = str(entry.get("text", "")).strip()
        timestamp = str(entry.get("timestamp", "")).strip()

        if not text or not timestamp:
            continue

        try:
            parse_timestamp_to_seconds(timestamp)
        except Exception:
            continue

        valid_segments.append({
            "text": text,
            "timestamp": timestamp
        })

    if not valid_segments:
        raise RuntimeError(
            "Recap generation produced no valid "
            "timestamped segments."
        )

    narration_text = " ".join(
        s["text"] for s in valid_segments
    )

    output = (
        project /
        "recap_script.txt"
    )

    output.write_text(
        narration_text,
        encoding="utf-8"
    )

    segments_output = (
        project /
        "recap_segments.json"
    )

    segments_output.write_text(
        json.dumps(
            valid_segments,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    master = (
        DIRS["scripts"] /
        f"{safe_name(movie_title)}_recap.txt"
    )

    master.write_text(
        narration_text,
        encoding="utf-8"
    )

    return output, valid_segments'''

if old_generate_recap not in text:
    print("ERROR: Could not find generate_recap block to replace. No changes made.")
    raise SystemExit(1)

text = text.replace(old_generate_recap, new_generate_recap)

# ============================================================
# 2. ADD NEW FUNCTION: select_clip_ranges + build_edited_video
#    Insert right before "# RENDER" section
# ============================================================

render_marker = '''# ============================================================
# RENDER
# ============================================================'''

new_editing_functions = '''# ============================================================
# SCENE-BASED CLIP SELECTION
# ============================================================

def select_clip_ranges(
    segments,
    scenes,
    movie_duration,
    pad_before=1.5,
    pad_after=4.0
):

    ranges = []

    for segment in segments:

        try:
            point = parse_timestamp_to_seconds(
                segment["timestamp"]
            )
        except Exception:
            continue

        matching_scene = None

        for scene in scenes:
            if scene["start"] <= point <= scene["end"]:
                matching_scene = scene
                break

        if matching_scene:
            start = max(
                matching_scene["start"],
                point - pad_before
            )
            end = min(
                matching_scene["end"],
                point + pad_after
            )
        else:
            start = max(0.0, point - pad_before)
            end = min(
                movie_duration,
                point + pad_after
            )

        if end - start < 1.0:
            end = min(movie_duration, start + 1.0)

        ranges.append({
            "start": round(start, 3),
            "end": round(end, 3)
        })

    return ranges


# ============================================================
# BUILD EDITED HIGHLIGHT REEL
# ============================================================

def build_edited_video(
    movie,
    clip_ranges,
    project
):

    clips_dir = project / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)

    log("")
    log("BUILDING EDITED VIDEO FROM SCENE CLIPS")
    log("-" * 60)
    log(f"Clips requested: {len(clip_ranges)}")

    clip_paths = []

    for index, clip_range in enumerate(clip_ranges, start=1):

        start = clip_range["start"]
        end = clip_range["end"]

        clip_output = (
            clips_dir / f"clip_{index:03d}.mp4"
        )

        result = run([
            "ffmpeg",
            "-y",
            "-ss", f"{start:.3f}",
            "-to", f"{end:.3f}",
            "-i", str(movie),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            str(clip_output)
        ])

        if (
            result.returncode == 0
            and clip_output.exists()
            and clip_output.stat().st_size > 0
        ):
            clip_paths.append(clip_output)
        else:
            log(
                f"WARNING: Clip {index} failed "
                f"({start:.2f}-{end:.2f}), skipping."
            )

    if not clip_paths:
        raise RuntimeError(
            "No clips were successfully cut. "
            "Cannot build edited video."
        )

    concat_list = project / "concat_list.txt"

    with open(concat_list, "w", encoding="utf-8") as f:
        for clip in clip_paths:
            escaped = str(clip).replace("'", "'\\\\''")
            f.write(f"file '{escaped}'\\n")

    edited_output = project / "edited_reel.mp4"

    result = run([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(edited_output)
    ])

    if (
        result.returncode != 0
        or not edited_output.exists()
        or edited_output.stat().st_size == 0
    ):
        raise RuntimeError(
            "Failed to concatenate edited clips."
        )

    log(
        f"Edited reel built: {edited_output}"
    )
    log(
        f"Clips used: {len(clip_paths)} / {len(clip_ranges)}"
    )

    return edited_output


''' + render_marker

if render_marker not in text:
    print("ERROR: Could not find RENDER marker to insert new functions. No changes made.")
    raise SystemExit(1)

text = text.replace(render_marker, new_editing_functions, 1)

# ============================================================
# 3. UPDATE main() TO USE THE NEW FUNCTIONS
# ============================================================

old_recap_call = '''    script = generate_recap(
        analysis,
        movie_title,
        project,
        selected_model
    )

    project_state(
        project,
        "recap_generation",
        details={
            "script": str(script)
        }
    )'''

new_recap_call = '''    script, recap_segments = generate_recap(
        analysis,
        movie_title,
        project,
        selected_model
    )

    project_state(
        project,
        "recap_generation",
        details={
            "script": str(script),
            "segments": len(recap_segments)
        }
    )

    log("")
    log("=== 7b/10 SCENE-BASED VIDEO EDITING ===")

    clip_ranges = select_clip_ranges(
        recap_segments,
        scenes,
        duration
    )

    edited_movie = build_edited_video(
        movie,
        clip_ranges,
        project
    )

    project_state(
        project,
        "scene_editing",
        details={
            "edited_movie": str(edited_movie),
            "clips": len(clip_ranges)
        }
    )'''

if old_recap_call not in text:
    print("ERROR: Could not find recap call in main() to replace. No changes made.")
    raise SystemExit(1)

text = text.replace(old_recap_call, new_recap_call)

old_render_call = '''    final_video = render_video(
        movie,
        narration,
        project,
        movie_title
    )'''

new_render_call = '''    final_video = render_video(
        edited_movie,
        narration,
        project,
        movie_title
    )'''

if old_render_call not in text:
    print("ERROR: Could not find render_video call in main() to replace. No changes made.")
    raise SystemExit(1)

text = text.replace(old_render_call, new_render_call)

# ============================================================
# 4. FIX HARDCODED QWEN -> LLAMA (already-decided choice)
# ============================================================

old_model_choice = '''    selected_model = MODELS["qwen"]'''
new_model_choice = '''    # Llama 3.2 1B was selected after real grounding
    # tests: Qwen3-1.7B fabricated facts in multiple
    # tests and used more RAM. This is a settled choice,
    # not a placeholder.
    selected_model = MODELS["llama"]'''

if old_model_choice in text:
    text = text.replace(old_model_choice, new_model_choice)
else:
    print("NOTE: Could not find hardcoded qwen model line — skipped (not critical).")

# ============================================================
# WRITE OUT
# ============================================================

backup.parent.mkdir(parents=True, exist_ok=True)
backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
print(f"Backup saved: {backup}")

target.write_text(text, encoding="utf-8")
print("Scene-based editing patch applied successfully.")