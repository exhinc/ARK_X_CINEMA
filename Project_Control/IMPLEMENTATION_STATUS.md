# ARK X CINEMA — IMPLEMENTATION STATUS

**Audit date:** 2026-08-27  
**Branch audited:** `master`  
**Audit type:** Phase 1 repository/code audit  
**Purpose:** Establish the actual implementation state before further production engineering.

---

## 1. EXECUTIVE VERDICT

ARK X Cinema has a real foundation, but the repository is **NOT yet a complete first-movie production system**.

The current codebase contains a substantial monolithic `Engine/orchestrator.py`, a Tkinter control center, configuration, project-control documentation, source/project artifacts, test scripts, and multiple historical patch/backups.

The most important proven capability is:

```text
SEPARATE AD AUDIO
        ↓
    whisper.cpp
        ↓
 TIMESTAMPED AD SRT
```

That path is explicitly locked by the architecture decisions and has a recorded successful full-AD test.

The repository does **not** yet provide sufficient evidence that the complete pipeline:

```text
Movie → intelligence → recap → narration → scene selection → render → QA → upload package
```

works reliably end-to-end.

**Do not run a production movie yet. Finish the integration work identified below first.**

---

# 2. STATUS LEGEND

- 🟢 **IMPLEMENTED** — meaningful code/artifacts exist.
- 🟡 **PARTIAL / NEEDS INTEGRATION** — some implementation exists, but production readiness is not established.
- 🔴 **MISSING / NOT PROVEN** — required capability is absent or not demonstrated by repository evidence.
- ⚠️ **RISK / TECHNICAL DEBT** — implementation exists but has a portability, correctness, maintainability, or architecture risk.

Important: **implemented does not mean production-ready.**

---

# 3. REPOSITORY STRUCTURE AUDIT

## Core application

| Component | Status | Finding |
|---|---|---|
| `Engine/orchestrator.py` | 🟡 | Large monolithic production engine containing source, subtitle, Whisper, analysis/recap and rendering-related logic, but not proven as complete end-to-end pipeline. |
| `Control/ark_cinema.py` | 🟡 | Functional Tkinter control-center foundation; its displayed pipeline contains stages that are not all proven to exist as working production stages. |
| `Control/Launch_ARK_X_Cinema.vbs` | ⚠️ | Launcher works conceptually but contains an absolute user-specific path. |
| `RUN_ARK_X_CINEMA.bat` | ⚠️ | Uses `%USERPROFILE%\Desktop\ARK_X_CINEMA`, so it assumes the repo is on the Desktop. |
| `Config/config.json` | 🟡 | Central configuration exists, but the main orchestrator currently hard-codes important paths instead of consistently consuming this configuration. |
| `Project_Control/` | 🟢 | Permanent project-control layer exists. |
| `Projects/` | 🟢 | Per-movie project metadata exists for The Platform. |
| `Engine/Tests/` | 🟡 | Tests exist, but they are heterogeneous and some are legacy/non-authoritative. |
| `Backups/` | 🟢 | Historical versions/patch backups exist; useful for recovery but should not be treated as active production code. |

---

# 4. SOURCE INGESTION

## 4.1 Movie discovery — 🟢 IMPLEMENTED

`orchestrator.py` has explicit video extensions and can accept either a movie package directory or a single movie file.

It recursively discovers files and separates:

- video files
- subtitle files
- audio files

The engine rejects a package without a usable video source.

### Remaining work

- Make selection policy more deterministic.
- Explicitly distinguish movie vs trailer/sample/preview when possible.
- Record the final source decision in the per-movie project manifest.
- Add robust ambiguity handling instead of silently choosing the largest file in all cases.

---

## 4.2 Media inspection — 🟢 IMPLEMENTED

FFprobe integration exists and collects stream and format information including:

- duration
- file size
- video streams
- audio streams
- subtitle streams
- raw probe data

### Remaining work

- Add executable availability validation before production.
- Add stronger media-integrity checks.
- Persist canonical source metadata per project.

---

## 4.3 Source manifest — 🟡 PARTIAL

The repository contains a `source_manifest.json` for the The Platform test project, so the concept exists.

However, the production engine's source-discovery report currently writes `last_source_discovery.json` under `Logs`, while the project-level source manifest/state architecture needs to become the canonical production artifact.

### Required

```text
Projects/<movie>/source_manifest.json
```

should become the authoritative record of exactly what was discovered and selected for that movie.

---

# 5. SUBTITLE PIPELINE

## External subtitles — 🟢 IMPLEMENTED

The engine discovers external subtitle files and attempts filename matching against the selected movie.

## Embedded subtitles — 🟢 IMPLEMENTED

Embedded subtitle streams are detected with FFprobe and English is preferred when metadata indicates English.

## Subtitle conversion — 🟢 IMPLEMENTED

Non-SRT subtitle formats are converted using FFmpeg.

## SRT validation — 🟢 IMPLEMENTED

The engine contains structural/timestamp validation including:

- file existence
- non-empty output
- parseability
- usable text
- valid timestamps
- chronological ordering
- end > start

### Remaining work — 🟡

- Define one canonical subtitle-selection policy.
- Handle missing subtitles explicitly.
- Persist the selected source and reason.
- Add tests for language selection and malformed inputs.
- Ensure subtitle timing is appropriate for downstream movie intelligence.

---

# 6. AUDIO DESCRIPTION PIPELINE

## AD discovery — 🟢 IMPLEMENTED

External audio assets are discovered and filename heuristics identify likely AD files.

Embedded AD audio detection also exists in the engine.

## AD → Whisper.cpp → SRT — 🟢 TESTED / SUCCESSFUL

The architecture is explicitly locked:

```text
AD AUDIO
   ↓
whisper.cpp
   ↓
TIMESTAMPED AD SRT
   ↓
MOVIE INTELLIGENCE
```

The repository records a successful full AD transcription test using The Platform (2019) AD audio, approximately 135.8 MB.

## Whisper environment validation — 🟢 IMPLEMENTED

The orchestrator validates the configured Whisper executable/model and performs an executable launch self-test.

## AD production integration — 🟡 PARTIAL

The transcription capability exists, but the repository does not yet prove a clean complete production handoff from the generated AD SRT into the full movie-intelligence pipeline.

### Required

- Canonical per-project AD SRT output.
- Transcription metadata.
- Resume/no-retranscribe logic.
- Failure/retry handling.
- Stage state transition.
- Resource cleanup after transcription.
- Explicit handling when AD is unavailable.

---

# 7. SCENE / TIMELINE ENGINE

## Status: 🟡 PARTIAL / NOT PROVEN

The GUI includes a Scene Detection stage, and the repository contains historical scene-editing patch work. However, the current active production path is not sufficiently demonstrated as a stable canonical scene-index pipeline.

The repository contains `Engine/apply_scene_editing_patch.py`, which is itself a patch script designed to modify the orchestrator rather than being the canonical scene engine.

### Required canonical output

```text
Projects/<movie>/scene_index.json
```

containing timestamped scene ranges and associated source evidence.

### Required inputs

- movie duration
- subtitle timing
- AD timing
- scene boundaries
- dialogue/description information

### Required properties

- deterministic
- timestamp-valid
- resumable
- searchable
- consumable by recap generation and scene selection

---

# 8. MOVIE INTELLIGENCE

## Status: 🟡 PARTIAL / NEEDS HARDENING

The architecture calls for combining subtitle information, AD information, timing, and scene information into structured movie intelligence.

The current repository contains analysis-oriented code/artifacts, but there is not enough evidence to declare a complete production-grade movie-intelligence artifact for a full-length movie.

### Required canonical output

```text
Projects/<movie>/movie_intelligence.json
```

### Required content

- characters
- locations
- actions
- events
- scene context
- important objects
- relationships
- cause/effect
- plot progression
- major turning points
- timestamp references
- visual/action descriptions from AD

### Critical rule

The LLM must be grounded in timestamped source information and must not be treated as an unrestricted source of movie facts.

---

# 9. LOCAL LLM PIPELINE

## Status: 🟡 PARTIAL

Ollama integration exists in the codebase through the local HTTP API, and local small models are documented as available.

The repository currently references:

- `qwen3:1.7b`
- `llama3.2:1b`

### Important test evidence

The repository's recap JSON checkpoint used `llama3.2:1b` and failed to parse the model output. The recorded result is:

```text
passed: false
JSON parsing failed
```

Therefore the local LLM connection is **not yet a validated production structured-output pipeline**.

### Required

- One authoritative production model selection.
- Grounded prompts.
- Chunking for full movies.
- Structured-output enforcement.
- JSON validation.
- Retry/repair strategy.
- Context-size management.
- RAM measurement.
- Resource release.
- Checkpointing.

---

# 10. RECAP GENERATION

## Status: 🟡 PARTIAL / NOT PRODUCTION READY

The repository contains a recap JSON test and a patch script intended to change recap generation from plain text to timestamped JSON segments.

However, the committed test evidence currently contains a **FAIL**, with malformed model output.

The raw test response also demonstrates that the small model can produce malformed/nonconforming structured output.

### Required canonical outputs

```text
Projects/<movie>/recap_plan.json
Projects/<movie>/recap_segments.json
Projects/<movie>/recap_script.txt
```

### Required properties

- original wording
- chronological story
- cause/effect
- important characters/events
- grounded facts
- timestamp references
- narration-ready prose
- deterministic validation

---

# 11. NARRATION / TTS

## Status: 🔴 NOT PROVEN

The repository has a `Narration/` directory and the intended narration stage is represented in the architecture/GUI, but there is no sufficient repository evidence that a selected local TTS engine is integrated into the active production pipeline and has produced validated final narration for a full recap.

### Required

- Select production TTS engine.
- Verify license/availability for intended use.
- Measure RAM.
- Generate narration.
- Validate audio.
- Measure duration.
- Preserve output per project.
- Release resources.

---

# 12. SCRIPT → SCENE SYNCHRONIZATION

## Status: 🔴 NOT PROVEN

This is a critical integration bridge.

The system must map:

```text
Narration segment
       ↓
Movie event
       ↓
Movie timestamp
       ↓
Source scene/clip
```

The repository contains historical scene-editing patch work, but this is not sufficient evidence of a stable production implementation.

### Required output

```text
Projects/<movie>/edit_manifest.json
```

---

# 13. VIDEO EDITING / FFMPEG ASSEMBLY

## Status: 🟡 PARTIAL / NOT PRODUCTION PROVEN

FFmpeg execution infrastructure exists and the repository contains historical scene-editing/render patch work.

However, a complete validated render from a full movie recap—including narration, selected footage, captions and final output—has not been demonstrated in the repository evidence reviewed.

### Required

- clip extraction
- deterministic clip ordering
- clip normalization
- narration integration
- audio mixing
- subtitles
- optional music/SFX
- final encoding
- output validation
- render failure recovery

---

# 14. FINAL SUBTITLES

## Status: 🔴 NOT PROVEN

The repository supports subtitle data processing, but final recap-narration subtitle generation and synchronization with the generated narration are not demonstrated as a completed production stage.

### Required

```text
Narration
   ↓
Recap caption timing
   ↓
Final subtitle SRT
```

---

# 15. AUTOMATED QA

## Status: 🟡 PARTIAL

Existing validation includes SRT and structured-data validation concepts.

A complete final-video QA gate is not yet proven.

### Required final QA checks

- source integrity
- required artifacts exist
- JSON validity
- SRT validity
- timestamp validity
- narration validity
- video stream exists
- audio stream exists
- final duration is sane
- output file is non-empty
- FFprobe can inspect final output
- no required stage is silently skipped

---

# 16. PIPELINE STATE / RESUME

## Status: 🟡 PARTIAL

`project_state()` exists and writes a `pipeline_state.json` containing stage/status/details.

This is useful but is not yet a complete state machine.

### Current limitation

A single stage/status record is not enough to reliably represent all completed artifacts, retries, failed stages, dependencies, checksums, and resumability.

### Required

A canonical state model should record:

- movie identity
- pipeline version
- current stage
- completed stages
- artifact paths
- artifact validation status
- failure state
- retry count
- timestamps
- configuration/model information

The pipeline must resume from the last **validated** stage, not merely the last stage written to disk.

---

# 17. GUI / CONTROL CENTER

## Status: 🟡 FOUNDATION EXISTS

`Control/ark_cinema.py` provides:

- source detection
- start/stop
- runtime display
- stage display
- live log
- folder shortcuts
- QA/log access

The GUI currently explicitly states that ARK X Cinema processes **one movie per run**.

That is compatible with the current first-movie milestone.

### Risks

The GUI's stage list contains stages that are not all proven to correspond exactly to the active orchestrator implementation.

The GUI should eventually read stage/state information from the canonical state machine instead of relying primarily on keyword matching from console output.

---

# 18. CONFIGURATION / PORTABILITY

## Status: ⚠️ HIGH PRIORITY TECHNICAL DEBT

`Config/config.json` contains absolute paths tied to the current Windows machine, including the ARK root and Whisper installation.

The active orchestrator also directly defines:

```text
C:\Whisper\Release\whisper-cli.exe
C:\Whisper\Release\ggml-base.en.bin
```

The test scripts also contain hard-coded paths into the user's Desktop/Downloads.

The launcher contains hard-coded Desktop paths.

### Required

Create one authoritative configuration/bootstrap layer:

```text
Repository root
    ↓
configuration
    ↓
validated executable/model discovery
    ↓
runtime
```

The code should not depend on a specific Windows username or Desktop location.

---

# 19. TEST SUITE AUDIT

## Whisper tests — 🟡 MIXED / LEGACY

`Engine/Tests/Whisper/test_whisper.py` imports **faster-whisper**, while the locked production architecture uses **whisper.cpp**.

It also references an unrelated hard-coded Downloads video path.

This should be treated as historical/legacy benchmarking evidence, not the authoritative production Whisper test.

The `Engine/Tests/Whisper/Legacy/` directory confirms older test artifacts are being retained as historical evidence.

### Required

Create authoritative whisper.cpp tests that:

- use repository-relative/configured paths
- validate the actual production executable/model
- record runtime
- record peak RAM
- validate SRT
- support a short fixture for automated tests

---

## Recap JSON test — 🔴 CURRENTLY FAILING

The test script is explicitly designed to request JSON output from Llama and validate it.

The stored result says:

```text
passed: false
JSON parsing failed
```

Therefore recap structured output must be fixed and retested before this stage is considered complete.

---

# 20. PATCH / BACKUP HYGIENE

## Status: ⚠️ TECHNICAL DEBT

The repository contains multiple large historical orchestrator copies and patch scripts, including:

- `orchestrator_before_*`
- `apply_scene_editing_patch.py`
- `fix_duplicates.py`

This is valuable historical evidence, but patch scripts that modify production source in-place are not an ideal long-term architecture.

### Required

After the production engine is stabilized:

- keep intentional historical backups/archive
- remove obsolete patch scripts from the active execution surface or move them to an explicit archive
- establish normal Git commits as the primary change mechanism
- avoid editing production code through ad-hoc text replacement patches

Do not delete historical evidence until it has been deliberately classified.

---

# 21. GITIGNORE / SOURCE HYGIENE

## Status: 🟢 GOOD FOUNDATION

`.gitignore` correctly excludes large movie media and runtime files such as MP4/MKV/MOV/WAV/MP3/M4A and the `Movies/` working directory.

This protects the repository from accidentally committing large source media.

### Improvement needed

Review generated artifacts and test outputs so only intentional reproducible evidence is committed.

---

# 22. EXAMPLE MOVIE PROJECT

## The Platform (2019) — 🟢 TEST PROJECT EXISTS

The repository contains:

```text
Projects/The_Platform_-_Sci-Fi_2019/
    pipeline_state.json
    production.srt
    source.json
    source_manifest.json
```

This proves the project-state/artifact concept exists.

It does **not** prove a finished recap video exists.

The source media itself is intentionally excluded from Git by `.gitignore`.

---

# 23. FIRST-MOVIE READINESS GATE

Before Movie #1 is allowed to run as a real production test, all of the following should be true:

- [ ] Configuration is portable/validated.
- [ ] Source package is correctly identified.
- [ ] Subtitle path is canonical.
- [ ] AD audio is converted to AD SRT.
- [ ] AD SRT is validated.
- [ ] Scene/timeline index exists.
- [ ] Movie intelligence exists and is validated.
- [ ] LLM structured output passes validation.
- [ ] Recap script passes validation.
- [ ] TTS is integrated and validated.
- [ ] Script segments map to movie timestamps.
- [ ] Edit manifest validates.
- [ ] FFmpeg render completes.
- [ ] Final subtitles exist and validate.
- [ ] Automated QA passes.
- [ ] Project state reaches a validated completion state.
- [ ] Human QA checkpoint is presented.

Until these are satisfied, **do not classify the system as first-movie production-ready.**

---

# 24. EXACT NEXT BUILD ORDER

The audit establishes this order:

### Build 1 — Configuration/runtime foundation

Remove hard-coded machine-specific assumptions and establish validated runtime discovery.

### Build 2 — Canonical movie project workspace

Make every artifact movie-specific and deterministic.

### Build 3 — Canonical subtitle + AD pipeline

Finish source → subtitle → AD SRT integration.

### Build 4 — Scene/timeline index

Create the canonical timestamped movie map.

### Build 5 — Movie intelligence

Combine subtitles + AD + timeline into structured factual intelligence.

### Build 6 — LLM grounding/structured output

Fix the current JSON failure and build full-movie chunking/checkpointing.

### Build 7 — Recap engine

Generate validated timestamped recap segments and final script.

### Build 8 — TTS

Select, integrate and validate the production local TTS engine.

### Build 9 — Script-to-scene mapping

Create the edit manifest.

### Build 10 — FFmpeg production renderer

Produce the actual recap video.

### Build 11 — Final subtitles

Generate narration captions.

### Build 12 — Automated QA

Make QA a hard completion gate.

### Build 13 — Resume/recovery

Make every stage restartable without unnecessary reprocessing.

### Build 14 — First full movie

Only now run Movie #1.

---

# 25. PHASE 1 CONCLUSION

## What is genuinely working/proven

🟢 Repository/project-control foundation  
🟢 Source discovery foundation  
🟢 FFprobe media inspection foundation  
🟢 Subtitle discovery/extraction/conversion foundation  
🟢 SRT validation foundation  
🟢 Whisper.cpp environment validation  
🟢 **Full AD audio → whisper.cpp → timestamped SRT test**  
🟢 Basic project state artifact  
🟢 Tkinter control-center foundation  
🟢 Gitignore/source-media protection  

## What is not yet proven

🔴 Complete movie-intelligence production pipeline  
🔴 Reliable full-movie structured LLM output  
🔴 Production TTS  
🔴 End-to-end script/scene synchronization  
🔴 Complete final video rendering pipeline  
🔴 Final recap subtitles  
🔴 Complete automated QA gate  
🔴 Validated first-movie end-to-end run  
🔴 Multi-movie queue / 3-different-movies-per-day production  

## Overall Phase 1 assessment

**PHASE 1: COMPLETE — AUDIT ESTABLISHED.**

**FIRST-MOVIE PRODUCTION READINESS: NOT READY.**

**NEXT PHASE: PRODUCTION ENGINE FOUNDATION / CONFIGURATION + CANONICAL PROJECT PIPELINE.**

This document is the baseline against which future implementation work should be measured.
