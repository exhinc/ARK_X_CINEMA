# ARK X CINEMA — PROJECT STATE

**Project:** ARK X Cinema  
**Purpose:** Automated YouTube movie-recap production system  
**Current State:** Phase 2 — production engine foundation  
**Last Updated:** 2026-08-27

---

## 1. PROJECT OBJECTIVE

ARK X Cinema is a $0/month movie-recap production system designed to automate as much of the production workflow as practical while retaining final human QA/approval.

Target:
- 3 different movie recap videos per day
- Free/open-source-first tooling
- Local processing wherever practical
- Low-RAM Windows laptop compatibility
- Legal movie/source acquisition
- No piracy or DRM bypass

---

## 2. PHASE 1 AUDIT

Phase 1 is complete.

Authoritative audit:

`Project_Control/IMPLEMENTATION_STATUS.md`

The audit establishes that the repository has a functioning foundation but is not yet first-movie production-ready.

---

## 3. HARDWARE BASELINE

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

## 4. CURRENT TOOL BASELINE

Verified at the recorded audit:
- Python 3.14.6
- FFmpeg 9.0
- FFprobe
- Ollama 0.33.0
- Git
- Node.js
- npm

Ollama models recorded:
- llama3.2:1b
- qwen3:1.7b

---

## 5. LOCKED AD ARCHITECTURE

### CRITICAL DECISION

The Audio Description asset is supplied separately from the movie.

We do NOT assume that an AD SRT already exists.

Current input:

AD Audio MP3 / supported audio
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

Therefore the AD transcription is a primary movie-understanding source.

Do not replace this architecture without an explicit superseding decision.

---

## 6. CURRENT TEST STATUS

### Full AD transcription

Input:
The Platform (2019) Audio Description (AD).mp3

Size:
Approximately 135.8 MB

Result:
SUCCESSFUL FULL TRANSCRIPTION TEST

Established path:

AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT

### Recap JSON checkpoint

Current stored test result is FAIL.

The Llama 3.2 1B checkpoint produced malformed structured output and JSON parsing failed.

Therefore structured recap generation is NOT yet production-ready.

---

## 7. CURRENT IMPLEMENTATION STATE

### Proven foundation

- Source discovery foundation
- FFprobe media inspection
- Subtitle discovery/extraction/conversion foundation
- SRT validation
- Whisper.cpp environment validation
- Full AD transcription test
- Basic project state artifact
- Tkinter control center
- Gitignore/source-media protection

### Not yet production-ready

- Canonical configuration/runtime layer
- Full scene/timeline index
- Full movie intelligence
- Reliable structured LLM analysis
- Production recap generation
- Production TTS
- Script-to-scene synchronization
- Complete final video rendering
- Final recap subtitles
- Complete automated QA
- Full validated resume/recovery
- Multi-movie queue
- 3-different-movies/day throughput

---

## 8. IMPORTANT TECHNICAL RISKS

### Configuration portability

`Config/config.json` contains machine-specific absolute paths.

The active orchestrator also hard-codes Whisper paths.

The launch scripts contain hard-coded Desktop paths.

These must be consolidated into an authoritative runtime configuration/bootstrap layer.

### Test consistency

The active Whisper test script uses `faster-whisper`, while the locked production transcription architecture uses whisper.cpp.

That test should be classified as legacy/benchmark evidence rather than the authoritative production Whisper test.

### Patch-script architecture

The repository contains ad-hoc patch scripts that modify `orchestrator.py` through text replacement. These are historical engineering artifacts and should not remain the primary production modification mechanism.

### LLM structured output

The stored recap checkpoint currently fails JSON validation. This is an explicit blocker.

---

## 9. CURRENT PROJECT STRUCTURE

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

Project control:

- Project_Control/
  - PROJECT_STATE.md
  - CURRENT_TASK.md
  - DECISIONS.md
  - CHANGELOG.md
  - TEST_RESULTS.md
  - IMPLEMENTATION_STATUS.md

---

## 10. CURRENT DEVELOPMENT PLAN

The first complete movie is the next major milestone.

Build in this order:

1. Configuration/runtime foundation
2. Canonical movie workspace
3. Subtitle + AD ingestion
4. Scene/timeline index
5. Movie intelligence
6. LLM grounding and structured output
7. Recap generation
8. TTS narration
9. Script-to-scene mapping
10. FFmpeg renderer
11. Final recap subtitles
12. Automated QA
13. Resume/recovery
14. First full movie
15. Reliability repetitions
16. Multi-movie queue
17. 1/day -> 2/day -> 3 different movies/day

---

## 11. AI AGENT HANDOFF RULE

Any AI agent working on ARK X Cinema should read:

1. PROJECT_STATE.md
2. CURRENT_TASK.md
3. DECISIONS.md
4. CHANGELOG.md
5. TEST_RESULTS.md
6. IMPLEMENTATION_STATUS.md

before modifying project architecture or production code.

The newest explicit recorded decision supersedes older decisions.

Do not infer that an asset exists merely because a workflow diagram contains it.

Verify actual files before proceeding.

---

## STATUS

PHASE 1:
COMPLETE — FULL IMPLEMENTATION AUDIT ESTABLISHED

ARCHITECTURE:
LOCKED

AD AUDIO -> whisper.cpp -> AD SRT:
TESTED / SUCCESSFUL

FIRST-MOVIE PRODUCTION:
NOT READY

CURRENT PHASE:
PHASE 2 — PRODUCTION ENGINE FOUNDATION
