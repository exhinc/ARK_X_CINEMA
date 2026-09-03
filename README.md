# ARK X Cinema

### Stories Beyond the Screen

**A local-first, low-resource movie-recap production engine for Windows.**

ARK X Cinema is an automated YouTube movie-recap production system designed to transform a legally obtained movie/source package into the structured assets required for an original recap video.

The system is being engineered around three principles:

- **Maximum practical automation**
- **$0/month software and infrastructure**
- **Human final QA and approval**

The core production goal is to **reliably process one real 3–4 hour movie end-to-end** on the target Windows PC and produce a finished recap video that passes the required automated and human QA. There is no fixed daily movie quota. After the first full-length movie is reliable, additional throughput is measured and optimized empirically based on actual processing time, hardware, storage, and workload conditions.

> **Project status:** Active development  
> **Current architecture:** Locked  
> **Current milestone:** Production-engineering buildout  
> **Default branch:** `master`

---

## What ARK X Cinema Does

The system is designed to automate the production chain from source ingestion through final-video preparation:

```text
LEGAL MOVIE SOURCE PACKAGE
          │
          ▼
    SOURCE INSPECTION
          │
          ▼
  SUBTITLE / AUDIO DISCOVERY
          │
          ├───────────────┐
          ▼               ▼
   MOVIE SUBTITLES     AD AUDIO
                          │
                          ▼
                     whisper.cpp
                          │
                          ▼
                       AD SRT
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
    SPOKEN CONTENT                 VISUAL / ACTION
          │                               │
          └───────────────┬───────────────┘
                          ▼
                 MOVIE INTELLIGENCE
                          │
                          ▼
                  RECAP GENERATION
                          │
                          ▼
                    NARRATION
                          │
                          ▼
                  SCENE SELECTION
                          │
                          ▼
                       FFmpeg
                          │
                          ▼
                    FINAL VIDEO
                          │
                          ▼
                    HUMAN QA
                          │
                          ▼
                    UPLOAD READY
```

The architecture is intentionally staged so heavy AI workloads can be processed sequentially rather than simultaneously.

---

# Core Architecture

## 1. Source Package Inspection

ARK X Cinema accepts a movie as either:

```text
Movies/
└── Movie Name/
    ├── movie.mkv
    ├── subtitles.srt
    └── audio_description.mp3
```

or a standalone movie file.

The engine discovers available video, subtitle, and audio assets and uses FFprobe to inspect media properties.

The current canonical source-manifest implementation requires **exactly one usable movie video** in a source package and rejects ambiguous multi-video packages rather than silently selecting one. `project_workspace.py` is the authoritative implementation for that rule.

---

## 2. Subtitle Handling

The engine can work with:

- External subtitle files
- Embedded subtitle streams
- SRT and other supported subtitle formats

Subtitle data is normalized toward SRT for downstream processing.

English subtitle streams are preferred when multiple embedded streams are available.

---

# 3. Audio Description Pipeline

### This is a locked architectural decision.

ARK X Cinema does **not** require the user to supply an existing AD SRT.

The actual input is the separately supplied Audio Description audio:

```text
AD MP3 / M4A / WAV / etc.
             │
             ▼
        whisper.cpp
             │
             ▼
    Timestamped AD SRT
             │
             ▼
      Movie Intelligence
```

The AD transcript is treated as a **primary intelligence source**.

This matters because Audio Description can contain information that ordinary dialogue subtitles do not provide, including:

- Visual descriptions
- Character actions
- Physical movements
- Scene context
- Environmental information
- Spoken dialogue/information
- Timing information

Therefore, AD data must not be discarded after transcription.

### Locked rule

> **Never assume an AD SRT already exists when the source package contains AD audio.**

The AD audio must be capable of being converted into its timestamped SRT representation by the pipeline.

---

# 4. Movie Intelligence

The movie-intelligence layer combines timestamped information from available sources.

Conceptually:

```text
Movie subtitles ───────┐
                       │
AD transcript ─────────┤
                       │
Scene information ─────┤
                       ▼
                Movie Intelligence
                       │
                       ▼
             Timestamped factual notes
```

The objective is to create a structured understanding of the movie that can support original recap generation and downstream scene selection.

---

# 5. Recap Generation

The recap-generation layer transforms structured movie information into a recap representation suitable for narration and editing.

The current master includes dedicated structured-output validation and an evidence-grounded recap script engine.

The intended direction is:

```text
Movie Intelligence
        │
        ▼
Recap Generator
        │
        ▼
Validated structured recap
        │
        ├───────────────┐
        ▼               ▼
   Narration        Timestamps
```

Structured intermediate data is preferred over passing unstructured text directly between every stage.

---

# 6. Narration

The narration stage is designed to convert the approved recap script into spoken audio.

The architecture is intentionally modular so the narration implementation can evolve without redesigning the movie-intelligence pipeline.

The current master contains the TTS stage boundary, but a real production TTS engine remains subject to subsequent validation and is not yet claimed as Stage-A complete.

---

# 7. Scene Selection & Video Assembly

Timestamped recap information provides the basis for selecting appropriate portions of the legally obtained source material.

FFmpeg is the primary media-processing engine.

The intended production flow is:

```text
Recap timestamps
       │
       ▼
Scene selection
       │
       ▼
Source clips
       │
       ├── Narration
       ├── Subtitles
       ├── Music
       └── SFX / additional assets
              │
              ▼
          FFmpeg
              │
              ▼
         Final Video
```

The current master contains the video-stage boundary, while complete production rendering remains a later implementation/validation gate.

---

# 8. Quality Assurance

ARK X Cinema is designed around **human final approval**.

Automation should perform as much deterministic QA as practical, but a video is not considered production-ready merely because the script completed without an exception.

Final human QA is responsible for confirming:

- Story accuracy
- Narration quality
- Scene synchronization
- Visual relevance
- Audio balance
- Subtitle quality
- Rendering integrity
- Overall viewer quality
- Copyright/compliance considerations

---

# Resource-Constrained Design

ARK X Cinema is being developed for a low-resource Windows machine rather than assuming access to a cloud GPU.

Current recorded baseline includes approximately:

- Windows 11
- Intel Core i3-1115G4
- 2 physical CPU cores / 4 logical processors
- Approximately 7.65 GB usable RAM
- Intel UHD Graphics
- Approximately 475.6 GB system storage
- Approximately 143 GB free storage at the recorded audit

The system therefore follows a strict resource philosophy:

```text
ONE HEAVY AI STAGE
       │
       ▼
     RUN
       │
       ▼
RELEASE RESOURCES
       │
       ▼
NEXT HEAVY AI STAGE
```

The current target is approximately **≤2 GB additional RAM for the AI workload** where practical.

Configuration explicitly limits concurrent heavy stages:

```json
{
  "max_parallel_heavy_stages": 1,
  "ram_priority": "strict"
}
```

---

# Current Software Baseline

The recorded environment includes:

| Component | Recorded baseline |
|---|---|
| Operating System | Windows 11 |
| Python | 3.14.6 |
| FFmpeg | 9.0 |
| FFprobe | Available |
| Ollama | 0.33.0 |
| Qwen | `qwen3:1.7b` |
| Llama | `llama3.2:1b` |
| Whisper | whisper.cpp |
| Version Control | Git |
| Node.js | Installed |

These are recorded environment observations, not current GitHub-executed runtime validations.

The repository configuration points to the local Whisper installation and Qwen model. Configuration is kept separately in `Config/config.json`.

---

# Repository Structure

```text
ARK_X_CINEMA/
│
├── Analysis/                  # Movie intelligence / analysis outputs
├── Backups/                   # Historical development backups
├── Config/                    # Runtime configuration
│   └── config.json
│
├── Control/                   # User-facing production control
│   ├── ark_cinema.py
│   └── Launch_ARK_X_Cinema.vbs
│
├── Engine/                    # Core production engine
│   ├── orchestrator.py
│   └── Tests/
│
├── Finished/                  # Completed video outputs
├── Logs/                      # Runtime logs
├── Movies/                    # Legally obtained source packages (local; ignored by Git)
├── Music/                     # Music assets
├── Narration/                 # Generated narration
├── Projects/                  # Per-movie project state
├── Research/                  # Research material
├── Scenes/                    # Scene-selection assets/data
├── Scripts/                   # Generated recap scripts
├── SFX/                       # Sound effects
├── Subtitles/                 # Subtitle assets
├── Thumbnails/                # Thumbnail assets
├── Transcripts/               # Transcript and transcription outputs
├── Upload/                    # Upload-ready packages
├── Visuals/                   # Visual assets
│
├── Project_Control/           # Persistent project governance/evidence
│   ├── AUDIT_LEDGER.md
│   ├── PROJECT_STATE.md
│   ├── CURRENT_TASK.md
│   ├── DECISIONS.md
│   ├── CHANGELOG.md
│   ├── TEST_RESULTS.md
│   ├── IMPLEMENTATION_STATUS.md
│   └── MULTI_AI_STATUS.md
│
├── CLAUDE.md
├── AGENTS.md
└── RUN_ARK_X_CINEMA.bat
```

---

# Project Control System

ARK X Cinema does not rely on chat history as its permanent source of truth.

The repository contains a dedicated project-control layer.

### `PROJECT_STATE.md`

Defines the current authoritative project state.

### `CURRENT_TASK.md`

Defines what is being worked on now and what must happen next.

### `DECISIONS.md`

Contains architecture decisions that must not be silently reversed.

### `CHANGELOG.md`

Records significant implementation and architecture changes.

### `TEST_RESULTS.md`

Records test inputs, expected results, actual results, PASS/FAIL status, and observations.

### `IMPLEMENTATION_STATUS.md`

Records implementation state and the distinction between repository evidence and PC-only validation. Its historical Phase 1 audit is not itself evidence that the newer exhaustive forensic audit has been completed.

### `MULTI_AI_STATUS.md`

Records multi-agent evidence, disagreements, consensus state, and validation requirements. Historical claims remain visible until reconciled by newer evidence.

### `AUDIT_LEDGER.md`

The permanent instrument used during a **new full forensic audit**. It records repository coverage, system reconstruction, findings, repairs, verification, and remaining `UNVERIFIED`/`BLOCKED` items. Its existence does not mean the audit has already been performed.

### AI handoff rule

Any AI agent working on ARK X Cinema should read the project-control documents and `AGENTS.md` before making architectural or production-code changes.

The repository is the long-term source of truth.

---

# Current Test Evidence

## Full Audio Description Transcription

Tested against:

```text
The Platform (2019)
Audio Description (AD).mp3
```

Approximate input size:

```text
135.8 MB
```

Result:

```text
PASS
```

The complete AD audio successfully passed through:

```text
AD AUDIO
   ↓
whisper.cpp
   ↓
TIMESTAMPED SRT
```

This validates the fundamental AD transcription architecture.

Additional historical Whisper test artifacts are stored under:

```text
Transcripts/Tests/
Engine/Tests/Whisper/
```

---

# Example Project

The repository contains a working project-state package for:

```text
The Platform — Sci-Fi — 2019
```

Current tracked artifacts include:

```text
Projects/
└── The_Platform_-_Sci-Fi_2019/
    ├── pipeline_state.json
    ├── production.srt
    ├── source.json
    └── source_manifest.json
```

This project serves as an engineering test case rather than evidence that the complete end-to-end production pipeline is finished.

---

# Running ARK X Cinema

The primary user-facing launcher is:

```text
RUN_ARK_X_CINEMA.bat
```

The control interface launches the production engine and provides:

- Source detection
- Production start/stop controls
- Pipeline-stage display
- Live production logging
- Movie/finished/project folder access
- QA report access
- Runtime information

The underlying foundation engine is:

```text
Engine/orchestrator.py
```

The current Stage-A core composition path is:

```text
Engine/stage_a_runner.py
```

It currently reaches the script stage; downstream TTS, video, final subtitles, QA, and real-machine validation remain separate gates on `master`.

---

# Development Philosophy

ARK X Cinema follows several non-negotiable engineering principles.

### 1. Verify before assuming

An asset appearing in an architecture diagram does not mean the file actually exists.

Always inspect the repository/filesystem.

### 2. Preserve architecture decisions

A new implementation must not silently invalidate a locked architecture decision.

Superseding an architecture decision requires an explicit new decision.

### 3. Test before scaling

The development progression is:

```text
CORE COMPLETION
1 real 3–4 hour movie reliably end-to-end
        ↓
MEASURE THROUGHPUT
        ↓
OPTIMIZE WHEN USEFUL
        ↓
PROCESS ADDITIONAL MOVIES
AS HARDWARE / TIME / STORAGE ALLOW
```

There is no fixed number of videos per day required for the core project to be considered complete.

### 4. One heavy AI stage at a time

Memory pressure is a first-class engineering constraint.

### 5. Preserve failure history

Failed tests are recorded rather than deleted.

A later successful test does not erase earlier evidence.

### 6. Human QA remains mandatory

Automation increases throughput.

It does not eliminate final editorial responsibility.

---

# Legal & Copyright Boundary

ARK X Cinema is intended for content production using **legally obtained source material**.

The project does not authorize or implement:

- Piracy
- DRM circumvention
- Unauthorized acquisition
- Copyright infringement

Users are responsible for obtaining and using source material lawfully and for ensuring that resulting content complies with applicable copyright law and platform policies.

The system's purpose is production automation—not circumvention.

---

# Roadmap

## Phase 1 — Foundation

- [x] System audit protocol established
- [x] Repository established
- [x] Project-control system established
- [x] AD architecture locked
- [x] Full AD transcription test
- [x] Whisper output validation
- [x] Source-package discovery
- [x] Media inspection
- [x] Initial recap JSON validation tests
- [x] Permanent forensic audit protocol established

## Phase 2 — Production Engine

- [x] Runtime/configuration foundation
- [x] Canonical per-movie workspace/source manifest
- [x] Evidence packets and structured-output handling
- [x] Core recap script engine
- [ ] Complete movie-intelligence runtime validation
- [ ] Complete narration pipeline
- [ ] Complete scene-selection/edit pipeline
- [ ] Complete FFmpeg production rendering
- [ ] Final narration subtitles
- [ ] Automated final-media QA
- [ ] Complete end-to-end test movie

## Phase 3 — Reliability

- [ ] Reliable full-length movie production
- [ ] Failure recovery under real workload
- [ ] Pipeline resume under real workload
- [ ] Resource/RAM measurements
- [ ] Output validation under real workload
- [ ] Production logging verification
- [ ] Human-QA checkpoint

## Phase 4 — Throughput

Throughput is intentionally **not a fixed completion quota**. After one reliable 3–4 hour movie is proven, actual processing time and hardware capacity determine how many additional movies can be processed.

- [ ] Measure real end-to-end processing time
- [ ] Identify throughput bottlenecks
- [ ] Optimize only where the measured benefit is worthwhile
- [ ] Process additional movies as capacity allows

---

# Current Status

### Architecture

**LOCKED**

### AD Audio → whisper.cpp → AD SRT

**REPOSITORY IMPLEMENTED / HISTORICAL FULL-AD TEST SUCCESS; CURRENT PC VALIDATION UNVERIFIED**

### Source discovery

**IMPLEMENTED / TESTED**

### Media inspection

**IMPLEMENTED**

### Project state/checkpoint infrastructure

**IMPLEMENTED / TESTED**

### Production control GUI

**IMPLEMENTED FOUNDATION**

### Structured-output handling

**IMPLEMENTED / REGRESSION-TESTED**

### Recap script core

**IMPLEMENTED / CONTRACT-TESTED**

### Complete autonomous end-to-end production

**NOT YET PRODUCTION-READY**

### Core completion target

**1 real 3–4 hour movie reliably end-to-end with required automated and human QA**

### Throughput

**EMPIRICAL / MEASURE AFTER CORE COMPLETION — NO FIXED DAILY QUOTA**

---

# The ARK X Cinema Principle

> **Automate the production. Preserve the intelligence. Verify the output.**

ARK X Cinema is being built as a production system—not merely a collection of scripts.

Every stage should be:

**observable → testable → recoverable → replaceable → scalable**

The goal is not to chase an arbitrary daily quota.

The goal is to build a reliable production machine that can finish one full-length movie and then continue processing additional movies as real system capacity allows.
