# ARK X CINEMA — PROJECT STATE

**Project:** ARK X Cinema  
**Purpose:** Automated YouTube movie-recap production system  
**Current State:** Architecture/control system initialization  
**Last Updated:** 2026-08-27

---

## 1. PROJECT OBJECTIVE

ARK X Cinema is a $0/month movie-recap production system designed to automate
as much of the production workflow as practical while retaining final human
QA/approval.

Target:
- 3 different recap videos per day
- Free/open-source-first tooling
- Local processing wherever practical
- Low-RAM Windows laptop compatibility
- Legal movie/source acquisition
- No piracy or DRM bypass

---

## 2. HARDWARE BASELINE

System:
- HP Laptop 15-dy2xxx
- Windows 11
- RAM: approximately 7.65 GB usable
- CPU: 11th Gen Intel Core i3-1115G4
- Cores: 2
- Logical processors: 4
- GPU: Intel UHD Graphics
- Reported VRAM: 2 GB
- Storage: approximately 475.6 GB C: drive
- Free storage at audit: approximately 143.2 GB

Important constraint:
- Keep additional AI workload RAM as low as practical.
- Target remains approximately <=2 GB additional RAM for AI workload.
- Heavy AI stages should not run concurrently unless specifically tested.

---

## 3. CURRENT TOOL BASELINE

Verified:
- Python 3.14.6
- FFmpeg 9.0
- FFprobe
- Ollama 0.33.0
- Git
- Node.js
- npm

Ollama models currently present:
- llama3.2:1b
- qwen3:1.7b

---

## 4. LOCKED AD ARCHITECTURE

### CRITICAL DECISION

The Audio Description asset is supplied separately from the movie.

We do NOT assume that an AD SRT already exists.

Current input:

AD Audio MP3
    |
    v
whisper.cpp
    |
    v
Timestamped AD SRT
    |
    v
Movie Intelligence

The AD SRT is GENERATED from the AD audio by whisper.cpp.

The AD audio contains valuable information including:

1. Spoken/dialogue information
2. Visual descriptions
3. Action descriptions
4. Scene/context information

Therefore the AD transcription is NOT merely secondary context.

It is a primary movie-understanding source.

Example AD information:

"A red-haired white woman nearby nods."

"He touches meat hanging from the ceiling..."

These descriptions must remain available to the movie-intelligence layer.

---

## 5. LOCKED MOVIE-INTELLIGENCE DIRECTION

Current conceptual pipeline:

                    THE PLATFORM
                         |
                    AD Audio MP3
                         |
                    whisper.cpp
                         |
                      AD SRT
                         |
             +-----------+-----------+
             |                       |
       visual/action             dialogue
             |                       |
             +-----------+-----------+
                         |
                 MOVIE INTELLIGENCE
                         |
             timestamped factual notes
                         |
                  RECAP GENERATOR
                         |
                timestamped JSON
                         |
             +-----------+-----------+
             |                       |
         narration              timestamps
             |                       |
             +-----------+-----------+
                         |
                  SCENE SELECTION
                         |
                     FFmpeg
                         |
                    FINAL VIDEO

This is the current architecture.

Do not replace the AD-audio-to-SRT path without creating and recording
an explicit superseding architecture decision.

---

## 6. CURRENT TEST STATUS

### whisper.cpp full AD transcription

Input:
The Platform (2019) Audio Description (AD).mp3

Input type:
Separate AD audio file

Size:
Approximately 135.8 MB

Result:
SUCCESSFUL FULL TRANSCRIPTION TEST

The full AD audio was successfully processed with whisper.cpp without
the previously feared crash/failure.

This establishes:

AD MP3 -> whisper.cpp -> timestamped SRT

as a tested production candidate.

---

## 7. CURRENT PROJECT STRUCTURE

ARK_X_CINEMA/

- Analysis/
- Backups/
- Config/
- Control/
- Engine/
- Finished/
- Logs/
- Movies/
- Music/
- Narration/
- Projects/
- Research/
- Scenes/
- Scripts/
- SFX/
- Subtitles/
- Thumbnails/
- Transcripts/
- Upload/
- Visuals/

Additional project-control layer:

- Project_Control/
  - Archive/

---

## 8. CURRENT IMPORTANT FILES

Engine:
- Engine/orchestrator.py

Control:
- Control/ark_cinema.py
- Control/Launch_ARK_X_Cinema.vbs

Configuration:
- Config/config.json

Logs:
- Logs/orchestrator.log

Existing state audit:
- ARK_X_Cinema_Current_State.txt

Movie test:
- Movies/The Platform (2019)/The Platform (2019) Audio Description (AD).mp3

Whisper test outputs:
- Transcripts/whisper_cpp_test.srt
- Transcripts/whisper_cpp_test.txt
- Transcripts/deep_audit_whisper.srt

---

## 9. CURRENT DEVELOPMENT RULE

The project must not rely on conversational memory alone.

Project truth must be recoverable from files inside the ARK_X_CINEMA
project directory.

Every significant architecture change, implementation change, test,
failure, discovery, and milestone should be recorded.

---

## 10. CURRENT POSITION

We are establishing the permanent project-control/documentation system.

Production architecture is NOT being redesigned during this step.

Next immediate objective:

Initialize:
- PROJECT_STATE.md
- CHANGELOG.md
- DECISIONS.md
- TEST_RESULTS.md
- CURRENT_TASK.md
- Git repository

Then commit the initial project state.

---

## 11. AI AGENT HANDOFF RULE

Any AI agent working on ARK X Cinema should read:

1. PROJECT_STATE.md
2. CURRENT_TASK.md
3. DECISIONS.md
4. CHANGELOG.md
5. TEST_RESULTS.md

before modifying project architecture or production code.

The newest explicit recorded decision supersedes older decisions.

Do not infer that an asset exists merely because a workflow diagram
contains it.

Verify actual files before proceeding.

---

## STATUS

ARCHITECTURE:
LOCKED

AD AUDIO -> whisper.cpp -> AD SRT:
TESTED / SUCCESSFUL

PROJECT CONTROL SYSTEM:
BEING INITIALIZED

CURRENT TASK:
Initialize permanent project documentation and Git history.
