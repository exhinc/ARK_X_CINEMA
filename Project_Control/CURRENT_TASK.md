# ARK X CINEMA — CURRENT TASK

**Last Updated:** 2026-08-27

---

## CURRENT PHASE

PHASE 2 — PRODUCTION ENGINE FOUNDATION

---

## PHASE 1 STATUS

**COMPLETE — FULL REPOSITORY / CODE AUDIT ESTABLISHED**

Authoritative audit:

`Project_Control/IMPLEMENTATION_STATUS.md`

---

## PHASE 2 PROGRESS

### Build #1 — Runtime / Configuration Foundation

**PASS — implemented and integrated**

Completed:

- Repository-relative runtime configuration.
- Removed hard-coded Whisper paths from the active orchestrator.
- Centralized Whisper and Ollama configuration.
- Runtime dependency validation.
- Locked one-heavy-stage resource policy.
- Added orchestrator/runtime integration tests.

Remaining local validation is intentionally deferred to the Windows PC because GitHub cannot execute the user's installed Whisper/FFmpeg/Ollama environment.

### Build #2 — Next

Establish the canonical per-movie workspace and make source discovery produce a deterministic, validated source manifest without relying on global/historical output files.

---

## FIRST-MOVIE OBJECTIVE

Build the first-movie production pipeline in GitHub before running a real movie on the Windows PC.

Priority order:

1. Canonical per-movie workspace.
2. Harden source/subtitle/AD ingestion.
3. Establish canonical scene/timeline data.
4. Build validated movie intelligence.
5. Fix and harden local LLM structured output.
6. Build recap generation.
7. Integrate and validate local TTS.
8. Build script-to-scene edit mapping.
9. Build final FFmpeg rendering.
10. Build final narration subtitles.
11. Build automated QA gate.
12. Build validated resume/recovery behavior.
13. Only then run Movie #1 on the PC.

---

## LOCKED ARCHITECTURE — DO NOT CHANGE

Do NOT:

- Assume an AD SRT already exists.
- Require the user to provide an AD SRT.
- Replace AD audio transcription with an unrelated subtitle source.
- Treat AD as merely secondary context.
- Remove visual/action descriptions from the intelligence pipeline.
- Redesign the locked architecture without recording a new decision.

The locked path remains:

AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT -> MOVIE INTELLIGENCE

---

## DEVELOPMENT RULE

All implementation should be developed and reviewed in GitHub first whenever practical.

The PC is the execution/validation environment for local dependencies, RAM, media processing and final end-to-end behavior.

Do not declare a component production-ready until its required test passes.

---

## HANDOFF

Before future development, read:

Project_Control/PROJECT_STATE.md
Project_Control/CURRENT_TASK.md
Project_Control/DECISIONS.md
Project_Control/CHANGELOG.md
Project_Control/TEST_RESULTS.md
Project_Control/IMPLEMENTATION_STATUS.md

Then inspect the actual code/files before making assumptions.
