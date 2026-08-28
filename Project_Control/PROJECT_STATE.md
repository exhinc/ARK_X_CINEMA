# ARK X CINEMA — PROJECT STATE

**Project:** ARK X Cinema  
**Purpose:** Automated YouTube movie-recap production system  
**Current State:** Phase 2 — production engine foundation  
**Last Updated:** 2026-08-28

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

## 2. PHASE 1 STATUS

The historical Phase 1 implementation audit is complete.

Authoritative historical implementation record:

`Project_Control/IMPLEMENTATION_STATUS.md`

**Important distinction:** the historical Phase 1 implementation audit is not the new exhaustive forensic audit. The permanent forensic audit protocol is established, but a full forensic audit is a separate operation tracked in `Project_Control/AUDIT_LEDGER.md`.

---

## 3. HARDWARE BASELINE

System baseline recorded for the target workstation:
- HP Laptop 15-dy2xxx
- Windows 11
- RAM: approximately 7.65 GB usable
- CPU: 11th Gen Intel Core i3-1115G4
- Cores: 2
- Logical processors: 4
- GPU: Intel UHD Graphics
- Reported VRAM: 2 GB
- Storage: approximately 475.6 GB C: drive
- Free storage at recorded audit: approximately 143.2 GB

Important constraint:
- Keep additional AI workload RAM as low as practical.
- Target remains approximately <=2 GB additional RAM for AI workload.
- Heavy AI stages should not run concurrently unless specifically tested.

---

## 4. CURRENT TOOL BASELINE

Recorded environment evidence includes:
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

These are recorded workstation observations and are not substitutes for fresh PC validation.

---

## 5. LOCKED AD ARCHITECTURE

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

## 6. CURRENT VERIFIED TEST/IMPLEMENTATION STATUS

### Full AD transcription

Input:
The Platform (2019) Audio Description (AD).mp3

Size:
Approximately 135.8 MB

Result:
SUCCESSFUL HISTORICAL FULL TRANSCRIPTION TEST

Established path:

AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT

### Current master code

Current master contains:
- repository-relative runtime configuration
- canonical per-movie workspace/source manifest
- subtitle and AD ingestion
- whisper.cpp integration boundary
- deterministic timeline engine
- bounded evidence packets
- Ollama intelligence adapter
- structured-output extraction/validation
- recap script engine and adapter
- ordered/resumable checkpoint infrastructure

Real Windows runtime validation remains outstanding.

### Historical recap JSON checkpoint

The stored historical test result is FAIL because the Llama 3.2 1B checkpoint produced malformed structured output.

The current master has since added structured-output extraction/validation and regression coverage, but real local model behavior remains unverified until Windows testing.

---

## 7. CURRENT IMPLEMENTATION STATE

### Implemented / repository-tested foundations

- Repository-relative configuration foundation
- Canonical per-movie workspace
- Deterministic source manifest
- Subtitle normalization/validation
- External AD discovery
- AD transcription integration boundary
- Deterministic timeline
- Bounded evidence packets
- Local Ollama integration boundary
- Structured-output extraction
- Recap script engine/boundary
- Stage-state/checkpoint infrastructure
- Resumable execution boundaries
- Test suite and GitHub Actions workflow
- Permanent forensic audit protocol and ledger mechanism

### Not yet verified as real production runtime

- Actual Whisper.cpp execution/performance on target PC
- Actual Ollama/Qwen behavior/performance on target PC
- Production TTS engine/runtime
- Production script-to-scene editing implementation
- Production FFmpeg assembly
- Final narration subtitles
- Complete automated final-media QA
- Full end-to-end first-movie processing
- Multi-movie queue
- 3-different-movies/day throughput

---

## 8. IMPORTANT TECHNICAL RISKS / DEBT

### Configuration/runtime validation

`Engine/runtime_config.py` centralizes repository-relative configuration and validates the configured Whisper executable/model. Full external dependency validation remains a PC/runtime concern.

### Test consistency

`Engine/Tests/Whisper/test_whisper.py` is explicitly skipped as a portable CI test and uses faster-whisper with a historical local path. It is retained as legacy/manual evidence; the locked production transcription architecture remains whisper.cpp.

### Patch-script history

The repository retains ad-hoc patch scripts and historical orchestrator copies. These are historical development artifacts, not the primary production modification mechanism. Preserve them unless deliberate archival/deletion is justified by evidence.

### GUI integration

`Control/ark_cinema.py` still derives displayed stage progress primarily from console log keywords while launching the conservative `Engine/orchestrator.py`. The canonical checkpoint/state system is not yet the sole source for GUI stage display.

---

## 9. CURRENT PROJECT STRUCTURE

Core directories:

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
- Project_Control/
- docs/

Project control:

- PROJECT_STATE.md
- CURRENT_TASK.md
- DECISIONS.md
- CHANGELOG.md
- TEST_RESULTS.md
- IMPLEMENTATION_STATUS.md
- MULTI_AI_STATUS.md
- AUDIT_LEDGER.md

---

## 10. CURRENT DEVELOPMENT PLAN

The first complete movie is the next major milestone.

Build in this order, using surgical changes and existing architecture:

1. Finish/verify movie-intelligence production path.
2. Finish/verify recap-generation production path.
3. Integrate a production TTS implementation.
4. Build canonical script-to-scene edit mapping.
5. Build production FFmpeg renderer.
6. Build final narration subtitles.
7. Build deterministic final-media QA.
8. Connect all completed stages through one authoritative resumable Stage-A runner.
9. Complete repository/CI regression checks.
10. Validate real Whisper.cpp/Ollama/TTS/FFmpeg behavior on the Windows PC.
11. Run a short real-media test.
12. Run a medium test.
13. Run the first full movie.
14. Repeat until Stage A reliability is established.
15. Scale to Stage B/C/D only after Stage A is proven.

---

## 11. AI AGENT HANDOFF RULE

Any AI agent working on ARK X Cinema should read:

1. `AGENTS.md`
2. `Project_Control/PROJECT_STATE.md`
3. `Project_Control/CURRENT_TASK.md`
4. `Project_Control/DECISIONS.md`
5. `Project_Control/CHANGELOG.md`
6. `Project_Control/TEST_RESULTS.md`
7. `Project_Control/IMPLEMENTATION_STATUS.md`
8. `Project_Control/AUDIT_LEDGER.md`
9. `docs/AI_HANDOFF.md`
10. `docs/PROJECT_STATUS.md`

before modifying architecture or production code.

The newest explicit recorded decision supersedes older decisions.

Do not infer that an asset exists merely because a workflow diagram contains it.

Treat historical audits/status records as evidence of their original scope, not proof that the new forensic audit has been completed.

---

## STATUS

HISTORICAL PHASE 1 IMPLEMENTATION AUDIT:
COMPLETE

PERMANENT FORENSIC AUDIT PROTOCOL:
ESTABLISHED

CURRENT EXHAUSTIVE FORENSIC AUDIT:
IN PROGRESS

ARCHITECTURE:
LOCKED

AD AUDIO -> whisper.cpp -> AD SRT:
HISTORICAL TEST SUCCESS / CURRENT PC VALIDATION UNVERIFIED

FIRST-MOVIE PRODUCTION:
NOT READY

CURRENT PHASE:
PHASE 2 — PRODUCTION ENGINE FOUNDATION
