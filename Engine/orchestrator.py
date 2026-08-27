import json
import re
import sys
import time
import shutil
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime


# ============================================================
# ARK X CINEMA
# UNIVERSAL SOURCE PACKAGE ENGINE
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

WHISPER = Path(r"C:\Whisper\Release\whisper-cli.exe")
WHISPER_MODEL = Path(r"C:\Whisper\Release\ggml-base.en.bin")

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

MODELS = {
    "qwen": "qwen3:1.7b",
    "llama": "llama3.2:1b"
}

DIRS = {
    "movies": ROOT / "Movies",
    "projects": ROOT / "Projects",
    "analysis": ROOT / "Analysis",
    "scenes": ROOT / "Scenes",
    "scripts": ROOT / "Scripts",
    "narration": ROOT / "Narration",
    "visuals": ROOT / "Visuals",
    "subtitles": ROOT / "Subtitles",
    "transcripts": ROOT / "Transcripts",
    "finished": ROOT / "Finished",
    "logs": ROOT / "Logs",
    "upload": ROOT / "Upload",
}

for directory in DIRS.values():
    directory.mkdir(parents=True, exist_ok=True)

LOG_FILE = DIRS["logs"] / "orchestrator.log"


# ============================================================
# FILE TYPE DEFINITIONS
# ============================================================

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm",
    ".m4v", ".ts", ".mts", ".m2ts", ".wmv",
    ".flv", ".ogv"
}

SUBTITLE_EXTENSIONS = {
    ".srt", ".vtt", ".ass", ".ssa", ".sub",
    ".sbv", ".dfxp", ".ttml"
}

AUDIO_EXTENSIONS = {
    ".wav", ".mp3", ".m4a", ".aac", ".flac",
    ".ogg", ".opus", ".wma", ".ac3", ".eac3"
}

AD_KEYWORDS = {
    "ad",
    "audio description",
    "audio_description",
    "audiodescription",
    "descriptive audio",
    "description",
    "descriptive"
}


# ============================================================
# LOGGING
# ============================================================

def log(message):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}"
    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd, capture=True):
    cmd = [str(x) for x in cmd]

    log("RUN: " + " ".join(cmd))

    result = subprocess.run(
        cmd,
        text=True,
        capture_output=capture,
        encoding="utf-8",
        errors="replace"
    )

    if capture and result.stderr:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(result.stderr[-15000:])

    return result


# ============================================================
# SAFE NAMES
# ============================================================

def safe_name(name):
    name = re.sub(
        r"[^\w\s-]",
        "",
        name,
        flags=re.UNICODE
    )

    name = re.sub(
        r"\s+",
        "_",
        name
    ).strip("_")

    return name or "Movie"


# ============================================================
# PROJECT STATE
# ============================================================

def project_state(project, stage, status="complete", details=None):
    state = {
        "stage": stage,
        "status": status,
        "updated": datetime.now().isoformat(),
        "details": details or {}
    }

    output = project / "pipeline_state.json"

    output.write_text(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ============================================================
# FFPROBE
# ============================================================

def ffprobe(path):
    result = run([
        "ffprobe",
        "-v", "error",
        "-show_streams",
        "-show_format",
        "-of", "json",
        str(path)
    ])

    if result.returncode != 0:
        raise RuntimeError(
            f"FFprobe failed for: {path}"
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"FFprobe returned invalid JSON for: {path}"
        )


# ============================================================
# UNIVERSAL SOURCE DISCOVERY
# ============================================================

def discover_files(package):
    """
    Discover all usable source files inside a movie package.

    A package may be:
      Movies\MovieName\
          movie.mkv
          subtitles.srt
          audio_description.m4a

    or a single movie file:
      Movies\MovieName.mkv

    The largest valid video file is treated as the primary movie.
    """

    package = Path(package)

    if not package.exists():
        raise RuntimeError(
            f"Movie source does not exist: {package}"
        )

    if package.is_file():

        if package.suffix.lower() not in VIDEO_EXTENSIONS:
            raise RuntimeError(
                f"Unsupported movie format: {package.suffix}"
            )

        files = [package]

    elif package.is_dir():

        files = [
            p for p in package.rglob("*")
            if p.is_file()
        ]

    else:
        raise RuntimeError(
            f"Invalid movie source: {package}"
        )

    videos = []
    subtitles = []
    audios = []

    for path in files:

        suffix = path.suffix.lower()

        if suffix in VIDEO_EXTENSIONS:
            videos.append(path)

        elif suffix in SUBTITLE_EXTENSIONS:
            subtitles.append(path)

        elif suffix in AUDIO_EXTENSIONS:
            audios.append(path)

    return {
        "all": files,
        "videos": videos,
        "subtitles": subtitles,
        "audios": audios
    }


def filename_looks_like_ad(path):

    name = path.stem.lower()

    normalized = re.sub(
        r"[^a-z0-9]+",
        " ",
        name
    ).strip()

    tokens = set(normalized.split())

    return any(
        keyword in tokens
        for keyword in {
            "ad",
            "audiodescription",
            "descriptive"
        }
    ) or (
        "audio description" in normalized
        or "descriptive audio" in normalized
    )


def inspect_media(path):

    path = Path(path)

    if not path.exists():
        return {
            "exists": False,
            "path": str(path)
        }

    probe = ffprobe(path)

    streams = probe.get(
        "streams",
        []
    )

    video_streams = [
        s for s in streams
        if s.get("codec_type") == "video"
    ]

    audio_streams = [
        s for s in streams
        if s.get("codec_type") == "audio"
    ]

    subtitle_streams = [
        s for s in streams
        if s.get("codec_type") == "subtitle"
    ]

    format_info = probe.get(
        "format",
        {}
    )

    duration = float(
        format_info.get(
            "duration",
            0
        ) or 0
    )

    size = int(
        format_info.get(
            "size",
            0
        ) or 0
    )

    return {
        "exists": True,
        "path": str(path),
        "name": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": size,
        "duration_seconds": duration,
        "video_streams": len(video_streams),
        "audio_streams": len(audio_streams),
        "subtitle_streams": len(subtitle_streams),
        "has_video": bool(video_streams),
        "has_audio": bool(audio_streams),
        "has_subtitles": bool(subtitle_streams),
        "probe": probe
    }


def identify_package(package):

    discovered = discover_files(package)

    videos = discovered["videos"]
    subtitles = discovered["subtitles"]
    audios = discovered["audios"]

    if not videos:
        raise RuntimeError(
            "No valid movie video file was found."
        )

    # --------------------------------------------------------
    # INSPECT EVERY VIDEO
    # --------------------------------------------------------

    candidates = []

    for video in videos:

        try:
            info = inspect_media(video)

        except Exception as exc:

            log(
                f"WARNING: Could not inspect "
                f"{video.name}: {exc}"
            )

            continue

        if not info["has_video"]:
            continue

        candidates.append(info)

    if not candidates:
        raise RuntimeError(
            "No usable video source could be inspected."
        )

    # --------------------------------------------------------
    # SELECT PRIMARY MOVIE
    # --------------------------------------------------------
    #
    # Prefer the largest video by file size.
    # This avoids accidentally selecting:
    #
    #   trailer.mp4
    #   sample.mkv
    #   preview.mp4
    #
    # over the actual movie.
    #
    # A very large file is not automatically trusted;
    # it must first contain a valid video stream.
    # --------------------------------------------------------

    candidates.sort(
        key=lambda x: (
            x["size_bytes"],
            x["duration_seconds"]
        ),
        reverse=True
    )

    movie_info = candidates[0]

    movie = Path(
        movie_info["path"]
    )

    # --------------------------------------------------------
    # MATCH EXTERNAL SUBTITLES
    # --------------------------------------------------------

    external_subtitles = []

    movie_stem = movie.stem.lower()

    for subtitle in subtitles:

        stem = subtitle.stem.lower()

        if (
            stem == movie_stem
            or movie_stem in stem
            or stem in movie_stem
        ):
            external_subtitles.append(
                subtitle
            )

    # If there is only one subtitle file,
    # accept it even when its filename differs.
    if (
        not external_subtitles
        and len(subtitles) == 1
    ):
        external_subtitles = subtitles[:]

    # --------------------------------------------------------
    # IDENTIFY AUDIO DESCRIPTION
    # --------------------------------------------------------

    external_ad_audio = []

    for audio in audios:

        if filename_looks_like_ad(audio):
            external_ad_audio.append(audio)

    # --------------------------------------------------------
    # PACKAGE REPORT
    # --------------------------------------------------------

    report = {
        "package": str(package),
        "movie": str(movie),
        "movie_info": movie_info,
        "video_candidates": [
            x["path"]
            for x in candidates
        ],
        "external_subtitles": [
            str(x)
            for x in external_subtitles
        ],
        "external_ad_audio": [
            str(x)
            for x in external_ad_audio
        ],
        "all_files": [
            str(x)
            for x in discovered["all"]
        ]
    }

    log("")
    log("SOURCE PACKAGE DISCOVERY")
    log("-" * 60)

    log(
        f"Package: {package}"
    )

    log(
        f"Files found: "
        f"{len(discovered['all'])}"
    )

    for path in discovered["all"]:
        log(
            f"  {path.name}"
        )

    log("")
    log(
        f"MOVIE SELECTED: {movie.name}"
    )

    log(
        f"Movie size: "
        f"{movie_info['size_bytes']:,} bytes"
    )

    log(
        f"Movie duration: "
        f"{movie_info['duration_seconds']:.2f} seconds"
    )

    log(
        f"Video streams: "
        f"{movie_info['video_streams']}"
    )

    log(
        f"Audio streams: "
        f"{movie_info['audio_streams']}"
    )

    log(
        f"Embedded subtitle streams: "
        f"{movie_info['subtitle_streams']}"
    )

    log("")
    log("MATCHING RESULT")
    log("-" * 60)

    log(
        f"External subtitles: "
        f"{len(external_subtitles)}"
    )

    log(
        f"External Audio Description files: "
        f"{len(external_ad_audio)}"
    )

    # --------------------------------------------------------
    # SAVE DISCOVERY REPORT
    # --------------------------------------------------------

    discovery_file = (
        DIRS["logs"] /
        "last_source_discovery.json"
    )

    discovery_file.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return report
# ============================================================
# EMBEDDED SUBTITLE DETECTION
# ============================================================

def find_embedded_subtitles(probe):

    results = []

    for stream in probe.get("streams", []):

        if stream.get("codec_type") != "subtitle":
            continue

        tags = stream.get("tags") or {}

        language = str(
            tags.get("language", "")
        ).lower()

        title = str(
            tags.get("title", "")
        ).lower()

        results.append({
            "index": stream.get("index"),
            "language": language,
            "title": title
        })

    return results


# ============================================================
# EMBEDDED AD DETECTION
# ============================================================

def find_embedded_ad_audio(probe):

    results = []

    for stream in probe.get("streams", []):

        if stream.get("codec_type") != "audio":
            continue

        tags = stream.get("tags") or {}

        searchable = " ".join([
            str(tags.get("title", "")),
            str(tags.get("handler_name", "")),
            str(tags.get("language", "")),
            str(tags.get("comment", ""))
        ]).lower()

        if any(
            keyword in searchable
            for keyword in AD_KEYWORDS
        ):
            results.append(stream)

    return results


# ============================================================
# SUBTITLE CONVERSION
# ============================================================

def convert_subtitle_to_srt(source, output):

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if source.suffix.lower() == ".srt":

        shutil.copy2(
            source,
            output
        )

        return output

    result = run([
        "ffmpeg",
        "-y",
        "-i", str(source),
        str(output)
    ])

    if (
        result.returncode != 0
        or not output.exists()
        or output.stat().st_size == 0
    ):
        raise RuntimeError(
            f"Could not convert subtitle: {source}"
        )

    return output


# ============================================================
# EMBEDDED SUBTITLE EXTRACTION
# ============================================================

def extract_embedded_subtitle(
    movie,
    probe,
    output
):

    streams = find_embedded_subtitles(
        probe
    )

    if not streams:
        return None

    # Prefer English.
    english = [
        s for s in streams
        if s["language"] in (
            "eng",
            "en",
            "english"
        )
        or "english" in s["title"]
    ]

    candidates = english or streams

    selected = candidates[0]

    index = selected["index"]

    log(
        f"Using embedded subtitle stream "
        f"{index}"
    )

    result = run([
        "ffmpeg",
        "-y",
        "-i", str(movie),
        "-map", f"0:{index}",
        "-c:s", "srt",
        str(output)
    ])

    if (
        result.returncode == 0
        and output.exists()
        and output.stat().st_size > 0
    ):
        return output

    return None


# ============================================================
# WHISPER TRANSCRIPTION
# ============================================================

def validate_whisper_environment():

    log("")
    log("WHISPER.CPP ENVIRONMENT VALIDATION")
    log("-" * 60)

    if not WHISPER.exists():
        raise RuntimeError(
            f"Whisper executable missing: {WHISPER}"
        )

    if not WHISPER.is_file():
        raise RuntimeError(
            f"Whisper executable is not a file: {WHISPER}"
        )

    if not WHISPER_MODEL.exists():
        raise RuntimeError(
            f"Whisper model missing: {WHISPER_MODEL}"
        )

    if not WHISPER_MODEL.is_file():
        raise RuntimeError(
            f"Whisper model is not a file: {WHISPER_MODEL}"
        )

    log(
        f"Whisper executable: {WHISPER}"
    )

    log(
        f"Whisper model: {WHISPER_MODEL}"
    )

    log(
        f"Whisper executable size: "
        f"{WHISPER.stat().st_size:,} bytes"
    )

    log(
        f"Whisper model size: "
        f"{WHISPER_MODEL.stat().st_size:,} bytes"
    )

    # --------------------------------------------------------
    # EXECUTABLE SELF-TEST
    # --------------------------------------------------------

    try:

        result = run([
            str(WHISPER),
            "--help"
        ])

    except Exception as exc:

        raise RuntimeError(
            "Whisper.cpp executable could not be launched: "
            f"{exc}"
        )

    if result.returncode not in (
        0,
        1
    ):

        raise RuntimeError(
            "Whisper.cpp executable failed its launch test. "
            f"Exit code: {result.returncode}"
        )

    log(
        "Whisper.cpp executable launch test: PASS"
    )

    return True

def validate_whisper_output(path):
    return validate_srt(path)

def validate_srt(path):

    path = Path(path)

    if not path.exists():

        return {
            "valid": False,
            "entries": 0,
            "characters": 0,
            "reason": "output_missing"
        }

    if path.stat().st_size == 0:

        return {
            "valid": False,
            "entries": 0,
            "characters": 0,
            "reason": "output_empty"
        }

    try:

        items = parse_srt(path)

    except Exception as exc:

        return {
            "valid": False,
            "entries": 0,
            "characters": 0,
            "reason": f"parse_error: {exc}"
        }

    if not items:

        return {
            "valid": False,
            "entries": 0,
            "characters": 0,
            "reason": "no_valid_srt_entries"
        }

    text = " ".join(
        item["text"]
        for item in items
    ).strip()

    if len(text) < 10:

        return {
            "valid": False,
            "entries": len(items),
            "characters": len(text),
            "reason": "insufficient_transcribed_text"
        }

    # --------------------------------------------------------
    # TIMESTAMP ORDER CHECK
    # --------------------------------------------------------

    def timestamp_seconds(value):

        value = value.replace(",", ".")

        parts = value.split(":")

        if len(parts) == 3:

            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])

            return (
                hours * 3600
                + minutes * 60
                + seconds
            )

        if len(parts) == 2:

            minutes = float(parts[0])
            seconds = float(parts[1])

            return (
                minutes * 60
                + seconds
            )

        raise ValueError(
            f"Invalid timestamp: {value}"
        )

    previous_end = -1.0

    for index, item in enumerate(items, start=1):

        try:

            start = timestamp_seconds(
                item["start"]
            )

            end = timestamp_seconds(
                item["end"]
            )

        except Exception as exc:

            return {
                "valid": False,
                "entries": len(items),
                "characters": len(text),
                "reason":
                    f"invalid_timestamp_at_entry_{index}: {exc}"
            }

        if end <= start:

            return {
                "valid": False,
                "entries": len(items),
                "characters": len(text),
                "reason":
                    f"invalid_timing_at_entry_{index}"
            }

        if start < previous_end:

            return {
                "valid": False,
                "entries": len(items),
                "characters": len(text),
                "reason":
                    f"non_monotonic_timing_at_entry_{index}"
            }

        previous_end = end

    return {
        "valid": True,
        "entries": len(items),
        "characters": len(text),
        "reason": "ok"
    }


def whisper_audio(
    audio,
    output_srt,
    label
):

    audio = Path(audio)
    output_srt = Path(output_srt)

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if not audio.exists():

        raise RuntimeError(
            f"Whisper input audio does not exist: {audio}"
        )

    if not audio.is_file():

        raise RuntimeError(
            f"Whisper input is not a file: {audio}"
        )

    if audio.stat().st_size == 0:

        raise RuntimeError(
            f"Whisper input audio is empty: {audio}"
        )

    # ========================================================
    # WHISPER ENVIRONMENT VALIDATION
    # ========================================================

    validate_whisper_environment()

    # ========================================================
    # PREPARE WORKING AUDIO
    # ========================================================

    output_srt.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    working_wav = (
        output_srt.parent /
        f"_{label}_working.wav"
    )

    base = output_srt.with_suffix("")

    log("")
    log("WHISPER.CPP TRANSCRIPTION")
    log("-" * 60)

    log(
        f"Input: {audio}"
    )

    log(
        f"Label: {label}"
    )

    log(
        "Converting source audio to "
        "16 kHz mono PCM WAV."
    )

    # Remove stale working files.

    for stale in (
        working_wav,
        Path(str(base) + ".srt"),
        Path(str(base) + ".txt")
    ):

        try:

            if stale.exists():
                stale.unlink()

        except OSError:

            pass

    result = run([
        "ffmpeg",
        "-y",
        "-i", str(audio),
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(working_wav)
    ])

    if result.returncode != 0:

        raise RuntimeError(
            f"Whisper audio preparation failed: {audio}"
        )

    if not working_wav.exists():

        raise RuntimeError(
            "Whisper audio preparation reported success "
            "but the WAV file was not created."
        )

    if working_wav.stat().st_size == 0:

        raise RuntimeError(
            "Whisper audio preparation created an empty WAV."
        )

    log(
        f"Prepared WAV: {working_wav}"
    )

    log(
        f"WAV size: "
        f"{working_wav.stat().st_size:,} bytes"
    )

    # ========================================================
    # RUN WHISPER.CPP
    # ========================================================

    log("")
    log("Running Whisper.cpp...")
    log(
        "RAM policy: one heavy AI stage at a time."
    )

    try:

        result = run([
            str(WHISPER),
            "-m", str(WHISPER_MODEL),
            "-f", str(working_wav),
            "-otxt",
            "-osrt",
            "-of", str(base)
        ])

    except Exception as exc:

        raise RuntimeError(
            f"Whisper.cpp could not be launched: {exc}"
        )

    generated_srt = Path(
        str(base) + ".srt"
    )

    generated_txt = Path(
        str(base) + ".txt"
    )

    # ========================================================
    # PROCESS RESULT
    # ========================================================

    if result.returncode != 0:

        raise RuntimeError(
            "Whisper.cpp transcription failed. "
            f"Exit code: {result.returncode}"
        )

    if not generated_srt.exists():

        raise RuntimeError(
            "Whisper.cpp finished without creating an SRT file."
        )

    # ========================================================
    # VALIDATE GENERATED SRT
    # ========================================================

    validation = validate_whisper_output(
        generated_srt
    )

    log("")
    log("WHISPER OUTPUT VALIDATION")
    log("-" * 60)

    log(
        f"Valid: {validation['valid']}"
    )

    log(
        f"Entries: {validation['entries']}"
    )

    log(
        f"Characters: {validation['characters']}"
    )

    log(
        f"Result: {validation['reason']}"
    )

    if not validation["valid"]:

        try:
            generated_srt.unlink()
        except OSError:
            pass

        raise RuntimeError(
            "Whisper.cpp produced an invalid SRT: "
            f"{validation['reason']}"
        )

    # ========================================================
    # MOVE/COPY RESULT TO REQUESTED OUTPUT
    # ========================================================

    if generated_srt.resolve() != output_srt.resolve():

        shutil.copy2(
            generated_srt,
            output_srt
        )

    if not output_srt.exists():

        raise RuntimeError(
            "Whisper transcription succeeded but the "
            "requested output SRT was not created."
        )

    final_validation = validate_whisper_output(
        output_srt
    )

    if not final_validation["valid"]:

        raise RuntimeError(
            "Final Whisper SRT validation failed: "
            f"{final_validation['reason']}"
        )

    log("")
    log(
        "WHISPER.CPP TRANSCRIPTION SUCCESS"
    )

    log(
        f"Final SRT: {output_srt}"
    )

    log(
        f"Entries: "
        f"{final_validation['entries']}"
    )

    log(
        f"Characters: "
        f"{final_validation['characters']:,}"
    )

    # ========================================================
    # CLEAN TEMPORARY FILES
    # ========================================================

    for temporary in (
        working_wav,
        generated_txt
    ):

        try:

            if temporary.exists():
                temporary.unlink()

        except OSError as exc:

            log(
                f"WARNING: Could not remove temporary file "
                f"{temporary}: {exc}"
            )

    # Remove duplicate generated SRT if necessary.

    try:

        if (
            generated_srt.exists()
            and
            generated_srt.resolve()
            != output_srt.resolve()
        ):
            generated_srt.unlink()

    except OSError:

        pass

    return output_srt
def parse_srt(path):

    text = path.read_text(
        encoding="utf-8-sig",
        errors="replace"
    )

    blocks = re.split(
        r"\n\s*\n",
        text.strip()
    )

    items = []

    for block in blocks:

        lines = block.splitlines()

        timing_index = None

        for i, line in enumerate(lines):

            if "-->" in line:
                timing_index = i
                break

        if timing_index is None:
            continue

        parts = lines[timing_index].split(
            "-->"
        )

        if len(parts) < 2:
            continue

        start = parts[0].strip()
        end = parts[1].strip().split()[0]

        body = " ".join(
            line.strip()
            for line in lines[timing_index + 1:]
            if line.strip()
        )

        if body:

            items.append({
                "start": start,
                "end": end,
                "text": body
            })

    return items


# ============================================================
# AUDIO DESCRIPTION → TEXT
# ============================================================

def transcribe_external_ad(
    ad_file,
    project
):

    output = project / "audio_description.srt"

    log("")
    log("AUDIO DESCRIPTION TRANSCRIPTION")
    log("-" * 60)
    log(f"AD SOURCE: {ad_file}")

    whisper_audio(
        ad_file,
        output,
        "audio_description"
    )

    text_output = (
        project /
        "audio_description.txt"
    )

    items = parse_srt(output)

    text = "\n".join(
        f"[{x['start']} --> {x['end']}] "
        f"{x['text']}"
        for x in items
    )

    text_output.write_text(
        text,
        encoding="utf-8"
    )

    return output, text_output, items


# ============================================================
# EMBEDDED AD → WAV → TEXT
# ============================================================

def extract_embedded_ad(
    movie,
    probe,
    project
):

    streams = find_embedded_ad_audio(
        probe
    )

    if not streams:
        return None

    selected = streams[0]

    index = selected["index"]

    output = (
        project /
        "audio_description.wav"
    )

    log(
        f"Embedded Audio Description stream "
        f"detected: {index}"
    )

    result = run([
        "ffmpeg",
        "-y",
        "-i", str(movie),
        "-map", f"0:{index}",
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(output)
    ])

    if (
        result.returncode != 0
        or not output.exists()
    ):
        return None

    srt = (
        project /
        "audio_description.srt"
    )

    whisper_audio(
        output,
        srt,
        "embedded_ad"
    )

    items = parse_srt(srt)

    text = "\n".join(
        f"[{x['start']} --> {x['end']}] "
        f"{x['text']}"
        for x in items
    )

    text_output = (
        project /
        "audio_description.txt"
    )

    text_output.write_text(
        text,
        encoding="utf-8"
    )

    return srt, text_output, items


# ============================================================
# SCENE DETECTION
# ============================================================

# ============================================================
# SCENE DETECTION
# ============================================================

def detect_scenes(
    movie,
    duration,
    project
):

    movie = Path(movie)
    project = Path(project)

    output = (
        project /
        "scene_map.json"
    )

    log("")
    log("SCENE DETECTION")
    log("-" * 60)

    # --------------------------------------------------------
    # INPUT VALIDATION
    # --------------------------------------------------------

    if not movie.exists():
        raise RuntimeError(
            f"Scene detection movie does not exist: {movie}"
        )

    if not movie.is_file():
        raise RuntimeError(
            f"Scene detection movie is not a file: {movie}"
        )

    if duration <= 0:
        raise RuntimeError(
            f"Invalid movie duration for scene detection: {duration}"
        )

    project.mkdir(
        parents=True,
        exist_ok=True
    )

    log(
        f"Movie: {movie}"
    )

    log(
        f"Duration: {duration:.3f} seconds"
    )

    # --------------------------------------------------------
    # FFmpeg SCENE DETECTION
    # --------------------------------------------------------
    #
    # The threshold is deliberately kept moderate.
    # A later calibration stage can make this adaptive.
    #
    # 0.35 = useful starting point for general movie footage.
    #
    # --------------------------------------------------------

    threshold = 0.35

    filter_expression = (
        f"select='gt(scene,{threshold})',"
        "metadata=print"
    )

    log(
        f"Scene threshold: {threshold}"
    )

    try:

        result = run([
            "ffmpeg",
            "-hide_banner",
            "-i", str(movie),
            "-vf",
            filter_expression,
            "-an",
            "-f", "null",
            "-"
        ])

    except Exception as exc:

        raise RuntimeError(
            "FFmpeg scene detection could not be launched: "
            f"{exc}"
        )

    # --------------------------------------------------------
    # FFmpeg RESULT VALIDATION
    # --------------------------------------------------------

    if result.returncode != 0:

        stderr_preview = (
            (result.stderr or "")
            .strip()
        )

        raise RuntimeError(
            "FFmpeg scene detection failed. "
            f"Exit code: {result.returncode}. "
            f"Output: {stderr_preview[-1000:]}"
        )

    # --------------------------------------------------------
    # EXTRACT SCENE BOUNDARIES
    # --------------------------------------------------------

    times = []

    for line in (
        result.stderr or ""
    ).splitlines():

        match = re.search(
            r"pts_time:([0-9]+(?:\.[0-9]+)?)",
            line
        )

        if not match:
            continue

        try:

            value = float(
                match.group(1)
            )

        except ValueError:

            continue

        if (
            value > 0.5
            and
            value < duration - 0.5
        ):

            times.append(
                value
            )

    # Remove duplicates and sort.
    times = sorted(
        set(
            round(x, 3)
            for x in times
        )
    )

    log(
        f"Raw scene boundaries detected: "
        f"{len(times)}"
    )

    # --------------------------------------------------------
    # BUILD SCENE BOUNDARIES
    # --------------------------------------------------------

    boundaries = [0.0]

    for value in times:

        if value > boundaries[-1]:

            boundaries.append(
                value
            )

    if (
        boundaries[-1] <
        round(duration, 3)
    ):

        boundaries.append(
            round(duration, 3)
        )

    # --------------------------------------------------------
    # BUILD SCENE RECORDS
    # --------------------------------------------------------

    scenes = []

    for index in range(
        len(boundaries) - 1
    ):

        start = boundaries[index]
        end = boundaries[index + 1]

        scene_duration = (
            end - start
        )

        # Ignore pathological sub-second fragments.
        if scene_duration < 1.0:
            continue

        scenes.append({
            "scene": len(scenes) + 1,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(
                scene_duration,
                3
            )
        })

    # --------------------------------------------------------
    # GUARANTEE A USABLE SCENE MAP
    # --------------------------------------------------------

    if not scenes:

        log(
            "WARNING: No usable scene cuts were detected."
        )

        log(
            "Creating a single full-movie scene."
        )

        scenes = [{
            "scene": 1,
            "start": 0.0,
            "end": round(duration, 3),
            "duration": round(
                duration,
                3
            )
        }]

    # --------------------------------------------------------
    # FINAL SCENE NUMBERING
    # --------------------------------------------------------

    for index, scene in enumerate(
        scenes,
        start=1
    ):

        scene["scene"] = index

    # --------------------------------------------------------
    # SCENE MAP METADATA
    # --------------------------------------------------------

    scene_map = {
        "schema_version": 1,
        "movie": str(movie),
        "duration": round(
            duration,
            3
        ),
        "detector": "ffmpeg_scene_detection",
        "threshold": threshold,
        "scene_count": len(scenes),
        "scenes": scenes
    }

    # --------------------------------------------------------
    # WRITE SCENE MAP
    # --------------------------------------------------------

    output.write_text(
        json.dumps(
            scene_map,
            indent=2
        ),
        encoding="utf-8"
    )

    if not output.exists():
        raise RuntimeError(
            "Scene detection completed but "
            "scene_map.json was not created."
        )

    if output.stat().st_size == 0:
        raise RuntimeError(
            "Scene detection created an empty scene_map.json."
        )

    log(
        f"Scenes detected: {len(scenes)}"
    )

    log(
        f"Scene map: {output}"
    )

    return scenes


# ============================================================
# OLLAMA
# ============================================================
def ollama_generate(
    prompt,
    model
):

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    }).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={
            "Content-Type":
            "application/json"
        },
        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=900
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        return data.get(
            "response",
            ""
        ).strip()

    except Exception as exc:

        log(
            f"Ollama error with "
            f"{model}: {exc}"
        )

        return ""


# ============================================================
# TRANSCRIPT CHUNKING
# ============================================================

def chunk_items(
    items,
    max_chars=7000
):

    chunks = []
    current = []
    chars = 0

    for item in items:

        length = len(
            item["text"]
        )

        if (
            current
            and chars + length > max_chars
        ):

            chunks.append(current)
            current = []
            chars = 0

        current.append(item)
        chars += length

    if current:
        chunks.append(current)

    return chunks


# ============================================================
# MOVIE INTELLIGENCE
# ============================================================

def analyze_movie(
    transcript_items,
    ad_items,
    project,
    movie_title,
    model
):

    chunks = chunk_items(
        transcript_items
    )

    ad_text = "\n".join(
        f"[{x['start']} --> {x['end']}] "
        f"{x['text']}"
        for x in ad_items
    )

    # Keep AD context bounded.
    ad_text = ad_text[:20000]

    all_analysis = []

    log("")
    log(
        f"MOVIE INTELLIGENCE — {model}"
    )
    log(
        f"Transcript chunks: {len(chunks)}"
    )

    for number, chunk in enumerate(
        chunks,
        1
    ):

        transcript = "\n".join(
            f"[{x['start']} --> {x['end']}] "
            f"{x['text']}"
            for x in chunk
        )

        prompt = f"""
You are ARK X Cinema's movie-intelligence engine.

Movie:
{movie_title}

Analyze this timestamped movie transcript.

Extract factual information about:

- story events
- character introductions
- character actions
- relationships
- motivations
- conflicts
- locations
- important objects
- discoveries
- reveals
- turning points
- cause and effect
- emotional developments
- information useful for an original movie recap

The Audio Description transcript is a SECONDARY source.
Use it to identify visual/action information that dialogue subtitles may miss.

Do not invent events.

Do not reproduce screenplay dialogue.

Keep timestamps whenever possible.

AUDIO DESCRIPTION:
{ad_text}

MOVIE TRANSCRIPT:
{transcript}
"""

        response = ollama_generate(
            prompt,
            model
        )

        if response:

            all_analysis.append({
                "chunk": number,
                "model": model,
                "notes": response
            })

        time.sleep(0.5)

    output = (
        project /
        f"movie_intelligence_{safe_name(model)}.json"
    )

    output.write_text(
        json.dumps(
            all_analysis,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return output, all_analysis


# ============================================================
# MODEL BENCHMARK
# ============================================================

def benchmark_models(
    sample_items,
    ad_items,
    project,
    movie_title
):

    sample = sample_items[:40]

    transcript = "\n".join(
        f"[{x['start']}] {x['text']}"
        for x in sample
    )

    ad_text = "\n".join(
        f"[{x['start']}] {x['text']}"
        for x in ad_items[:20]
    )

    prompt = f"""
ARK X Cinema model evaluation.

Movie:
{movie_title}

Analyze the following movie material.

Return concise structured notes covering:

1. Events
2. Characters
3. Actions
4. Conflict
5. Cause/effect
6. Important visual/action information
7. Possible turning point

Do not invent information.

MOVIE:
{transcript}

AUDIO DESCRIPTION:
{ad_text}
"""

    results = {}

    for label, model in MODELS.items():

        log("")
        log(
            f"MODEL TEST: {label} / {model}"
        )

        start = time.time()

        response = ollama_generate(
            prompt,
            model
        )

        elapsed = round(
            time.time() - start,
            2
        )

        results[label] = {
            "model": model,
            "seconds": elapsed,
            "response": response
        }

    output = (
        project /
        "model_comparison.json"
    )

    output.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return output, results


# ============================================================
# RECAP SCRIPT
# ============================================================

def parse_timestamp_to_seconds(value):

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

    notes = "\n\n".join(
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

    return output, valid_segments


# ============================================================
# WINDOWS SAPI
# ============================================================

def generate_tts(
    script,
    project
):

    text_file = (
        project /
        "tts_input.txt"
    )

    output = (
        project /
        "narration.wav"
    )

    text_file.write_text(
        script.read_text(
            encoding="utf-8"
        ),
        encoding="utf-8"
    )

    ps1 = (
        project /
        "_sapi_tts.ps1"
    )

    ps1.write_text(
r'''
param(
    [string]$TextFile,
    [string]$OutputFile
)

Add-Type -AssemblyName System.Speech

$text = Get-Content `
    -LiteralPath $TextFile `
    -Raw

$synth = New-Object `
    System.Speech.Synthesis.SpeechSynthesizer

$synth.Rate = 0
$synth.Volume = 100

$synth.SetOutputToWaveFile(
    $OutputFile
)

$synth.Speak($text)
$synth.Dispose()
''',
        encoding="utf-8"
    )

    result = run([
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File", str(ps1),
        "-TextFile", str(text_file),
        "-OutputFile", str(output)
    ])

    try:
        ps1.unlink()
    except OSError:
        pass

    if (
        result.returncode != 0
        or not output.exists()
    ):
        raise RuntimeError(
            "Windows SAPI TTS failed."
        )

    return output


# ============================================================
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
            escaped = str(clip).replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")

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


# ============================================================
# RENDER
# ============================================================

def render_video(
    movie,
    narration,
    project,
    movie_title
):

    output = (
        DIRS["finished"] /
        f"{safe_name(movie_title)}_ARK_X_Cinema.mp4"
    )

    duration_result = run([
        "ffprobe",
        "-v", "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=nw=1:nk=1",
        str(narration)
    ])

    if duration_result.returncode != 0:
        raise RuntimeError(
            "Could not determine narration duration."
        )

    narration_duration = float(
        duration_result.stdout.strip()
    )

    movie_duration_result = run([
        "ffprobe",
        "-v", "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=nw=1:nk=1",
        str(movie)
    ])

    movie_duration = float(
        movie_duration_result.stdout.strip()
    )

    duration = min(
        narration_duration,
        movie_duration
    )

    result = run([
        "ffmpeg",
        "-y",
        "-i", str(movie),
        "-i", str(narration),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-t", f"{duration:.3f}",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(output)
    ])

    if (
        result.returncode != 0
        or not output.exists()
    ):
        raise RuntimeError(
            "FFmpeg rendering failed."
        )

    return output


# ============================================================
# QA
# ============================================================

def qa(
    final_video,
    source,
    srt,
    ad_srt,
    script,
    narration,
    project
):

    report = {
        "source_exists": source.exists(),
        "movie_source": str(source),
        "srt_exists": srt.exists(),
        "ad_transcript_exists": (
            ad_srt.exists()
            if ad_srt
            else False
        ),
        "script_exists": script.exists(),
        "narration_exists": narration.exists(),
        "final_exists": final_video.exists()
    }

    if final_video.exists():

        report[
            "final_size_bytes"
        ] = final_video.stat().st_size

        probe = ffprobe(
            final_video
        )

        streams = probe.get(
            "streams",
            []
        )

        report["video_stream"] = any(
            x.get("codec_type") == "video"
            for x in streams
        )

        report["audio_stream"] = any(
            x.get("codec_type") == "audio"
            for x in streams
        )

        report["duration"] = (
            probe.get("format", {})
            .get("duration")
        )

    report["passed"] = all([
        report["source_exists"],
        report["srt_exists"],
        report["script_exists"],
        report["narration_exists"],
        report["final_exists"],
        report.get(
            "video_stream",
            False
        ),
        report.get(
            "audio_stream",
            False
        ),
        report.get(
            "final_size_bytes",
            0
        ) > 0
    ])

    output = (
        project /
        "qa_report.json"
    )

    output.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return report


# ============================================================
# FIND MOVIE PACKAGES
# ============================================================

def find_packages():

    movies_root = DIRS["movies"]

    # Preferred architecture:
    # Movies\Movie_Name\files...
    packages = []

    for directory in movies_root.iterdir():

        if not directory.is_dir():
            continue

        discovered = discover_files(
            directory
        )

        if discovered["videos"]:
            packages.append(directory)

    # Backward-compatible flat folder:
    # Movies\movie.mkv
    flat_videos = [
        p for p in movies_root.iterdir()
        if p.is_file()
        and p.suffix.lower()
        in VIDEO_EXTENSIONS
    ]

    for video in flat_videos:
        packages.append(
            video.parent
        )

    return list(
        dict.fromkeys(packages)
    )


# ============================================================
# MAIN
# ============================================================

def main():

    log("")
    log("=" * 70)
    log("ARK X CINEMA — UNIVERSAL ENGINE")
    log("=" * 70)

    packages = find_packages()

    if not packages:

        raise RuntimeError(
            "No movie package found."
        )

    # One movie per run for RAM safety.
    package = packages[0]

    log(
        f"PACKAGE SELECTED: {package}"
    )

    package_info = identify_package(
        package
    )

    movie = Path(
        package_info["movie"]
    )

    movie_title = movie.stem

    project = (
        DIRS["projects"] /
        safe_name(movie_title)
    )

    project.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # SAVE PACKAGE MANIFEST
    # --------------------------------------------------------

    manifest = (
        project /
        "source_manifest.json"
    )

    manifest.write_text(
        json.dumps(
            package_info,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # SOURCE INSPECTION
    # --------------------------------------------------------

    log("")
    log("=== 1/10 SOURCE INSPECTION ===")

    probe = ffprobe(movie)

    (project / "source.json").write_text(
        json.dumps(
            probe,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    duration = float(
        probe.get(
            "format",
            {}
        ).get(
            "duration",
            0
        ) or 0
    )

    project_state(
        project,
        "source_inspection",
        details={
            "movie": str(movie),
            "duration": duration
        }
    )

    # --------------------------------------------------------
    # SUBTITLES
    # --------------------------------------------------------

    log("")
    log("")
    log("=== 2/10 SUBTITLE INGESTION ===")

    srt = (
        project /
        "production.srt"
    )

    external_subtitles = [
        Path(x)
        for x in package_info[
            "external_subtitles"
        ]
        if Path(x).exists()
    ]

    subtitle_source = None
    subtitle_source_file = None

    # --------------------------------------------------------
    # SOURCE PRIORITY
    #
    # 1. Matching external subtitle
    # 2. Valid embedded subtitle
    # 3. Whisper.cpp fallback
    # --------------------------------------------------------

    if external_subtitles:

        log("")
        log("EXTERNAL SUBTITLE CANDIDATES")
        log("-" * 60)

        selected_external = None

        # Prefer the subtitle whose filename best matches
        # the movie filename.

        movie_stem_lower = (
            movie.stem.lower()
        )

        scored = []

        for subtitle in external_subtitles:

            stem = subtitle.stem.lower()

            score = 0

            if stem == movie_stem_lower:
                score += 100

            elif movie_stem_lower in stem:
                score += 75

            elif stem in movie_stem_lower:
                score += 50

            if subtitle.suffix.lower() == ".srt":
                score += 10

            scored.append(
                (
                    score,
                    subtitle
                )
            )

            log(
                f"Candidate: {subtitle.name} "
                f"(score={score})"
            )

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        # Test candidates until one actually validates.

        for score, candidate in scored:

            log(
                f"Testing external subtitle: "
                f"{candidate.name}"
            )

            try:

                convert_subtitle_to_srt(
                    candidate,
                    srt
                )

                validation = validate_srt(
                    srt
                )

                if validation["valid"]:

                    selected_external = candidate

                    subtitle_source = (
                        "external_subtitle"
                    )

                    subtitle_source_file = (
                        str(candidate)
                    )

                    break

            except Exception as exc:

                log(
                    f"WARNING: Subtitle candidate "
                    f"rejected: {exc}"
                )

        if selected_external:

            log(
                f"External subtitle selected: "
                f"{selected_external.name}"
            )

    # --------------------------------------------------------
    # EMBEDDED SUBTITLE FALLBACK
    # --------------------------------------------------------

    if subtitle_source is None:

        log("")
        log(
            "No valid external subtitle selected."
        )

        log(
            "Checking embedded subtitles..."
        )

        embedded = (
            extract_embedded_subtitle(
                movie,
                probe,
                srt
            )
        )

        if embedded:

            subtitle_source = (
                "embedded_subtitle"
            )

            subtitle_source_file = (
                str(movie)
            )

            log(
                "Valid embedded subtitle selected."
            )

    # --------------------------------------------------------
    # WHISPER FALLBACK
    # --------------------------------------------------------

    if subtitle_source is None:

        log("")
        log(
            "No valid external or embedded "
            "subtitle available."
        )

        log(
            "Falling back to Whisper.cpp."
        )

        whisper_audio(
            movie,
            srt,
            "movie"
        )

        subtitle_source = (
            "whisper_cpp"
        )

        subtitle_source_file = (
            str(movie)
        )

    # --------------------------------------------------------
    # FINAL PRODUCTION SRT VALIDATION
    # --------------------------------------------------------

    validation = validate_srt(
        srt
    )

    if not validation["valid"]:

        raise RuntimeError(
            "Production SRT failed final validation: "
            f"{validation['reason']}"
        )

    items = parse_srt(
        srt
    )

    if not items:

        raise RuntimeError(
            "Production SRT contains "
            "no usable entries."
        )

    # --------------------------------------------------------
    # PRESERVE MASTER TRANSCRIPT
    # --------------------------------------------------------

    transcript_copy = (
        DIRS["transcripts"] /
        f"{safe_name(movie_title)}_production.srt"
    )

    shutil.copy2(
        srt,
        transcript_copy
    )

    log("")
    log("SUBTITLE INGESTION RESULT")
    log("-" * 60)

    log(
        f"Source type: {subtitle_source}"
    )

    log(
        f"Source file: {subtitle_source_file}"
    )

    log(
        f"Entries: {len(items)}"
    )

    log(
        f"Characters: "
        f"{validation['characters']:,}"
    )

    log(
        f"Production SRT: {srt}"
    )

    log(
        f"Master transcript copy: "
        f"{transcript_copy}"
    )

    project_state(
        project,
        "subtitle_ingestion",
        details={
            "source": subtitle_source,
            "source_file": subtitle_source_file,
            "entries": len(items),
            "characters": validation["characters"],
            "production_srt": str(srt),
            "transcript_copy": str(
                transcript_copy
            )
        }
    )

    # --------------------------------------------------------
    # SCENES
    # --------------------------------------------------------
    log("=== 3/10 SCENE DETECTION ===")

    scenes = detect_scenes(
        movie,
        duration,
        project
    )

    project_state(
        project,
        "scene_detection",
        details={
            "scene_count": len(scenes)
        }
    )

    # --------------------------------------------------------
    # AUDIO DESCRIPTION
    # --------------------------------------------------------

    log("")
    log("=== 4/10 AUDIO DESCRIPTION ===")

    ad_items = []
    ad_srt = None
    ad_text = None
    ad_source = None

    external_ad = [
        Path(x)
        for x in package_info[
            "external_ad_audio"
        ]
    ]

    if external_ad:

        ad_srt, ad_text, ad_items = (
            transcribe_external_ad(
                external_ad[0],
                project
            )
        )

        ad_source = (
            "external_audio_description"
        )

    else:

        embedded_ad = (
            extract_embedded_ad(
                movie,
                probe,
                project
            )
        )

        if embedded_ad:

            ad_srt, ad_text, ad_items = (
                embedded_ad
            )

            ad_source = (
                "embedded_audio_description"
            )

        else:

            log(
                "No Audio Description "
                "source detected."
            )

    project_state(
        project,
        "audio_description",
        details={
            "source": ad_source,
            "entries": len(ad_items)
        }
    )

    # --------------------------------------------------------
    # MODEL COMPARISON
    # --------------------------------------------------------

    log("")
    log("=== 5/10 MODEL EVALUATION ===")

    comparison_file, comparison = (
        benchmark_models(
            items,
            ad_items,
            project,
            movie_title
        )
    )

    project_state(
        project,
        "model_evaluation",
        details={
            "comparison": str(
                comparison_file
            )
        }
    )

    # --------------------------------------------------------
    # FULL MOVIE INTELLIGENCE
    # --------------------------------------------------------

    log("")
    log("=== 6/10 FULL MOVIE INTELLIGENCE ===")

    # For the first full build we use Qwen.
    # The benchmark above records both models.
    #
    # We will NOT permanently declare a winner
    # until real movie testing is complete.

    # Llama 3.2 1B was selected after real grounding
    # tests: Qwen3-1.7B fabricated facts in multiple
    # tests and used more RAM. This is a settled choice,
    # not a placeholder.
    selected_model = MODELS["llama"]

    analysis_file, analysis = (
        analyze_movie(
            items,
            ad_items,
            project,
            movie_title,
            selected_model
        )
    )

    if not analysis:

        raise RuntimeError(
            "Movie intelligence failed."
        )

    project_state(
        project,
        "movie_intelligence",
        details={
            "model": selected_model,
            "chunks": len(analysis),
            "analysis": str(
                analysis_file
            )
        }
    )

    # --------------------------------------------------------
    # RECAP
    # --------------------------------------------------------

    log("")
    log("=== 7/10 RECAP GENERATION ===")

    script, recap_segments = generate_recap(
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
    )

    # --------------------------------------------------------
    # TTS
    # --------------------------------------------------------

    log("")
    log("=== 8/10 NARRATION ===")

    narration = generate_tts(
        script,
        project
    )

    project_state(
        project,
        "tts",
        details={
            "narration": str(narration)
        }
    )

    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    log("")
    log("=== 9/10 VIDEO RENDER ===")

    final_video = render_video(
        edited_movie,
        narration,
        project,
        movie_title
    )

    project_state(
        project,
        "render",
        details={
            "final_video": str(
                final_video
            )
        }
    )

    # --------------------------------------------------------
    # QA
    # --------------------------------------------------------

    log("")
    log("=== 10/10 QA ===")

    report = qa(
        final_video,
        movie,
        srt,
        ad_srt,
        script,
        narration,
        project
    )

    project_state(
        project,
        "qa",
        status=(
            "passed"
            if report["passed"]
            else "failed"
        ),
        details=report
    )

    log("")
    log("=" * 70)

    if report["passed"]:

        log(
            "ARK X CINEMA — PIPELINE COMPLETE"
        )

        log(
            f"FINAL VIDEO: {final_video}"
        )

        log(
            f"PROJECT: {project}"
        )

        log(
            f"QA: {project / 'qa_report.json'}"
        )

        log("=" * 70)

        return 0

    log(
        "ARK X CINEMA — QA FAILED"
    )

    return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:
        sys.exit(main())

    except KeyboardInterrupt:

        log(
            "Pipeline interrupted by user."
        )

        sys.exit(130)

    except Exception as exc:

        log(
            f"FATAL ERROR: {exc}"
        )

        sys.exit(1)

