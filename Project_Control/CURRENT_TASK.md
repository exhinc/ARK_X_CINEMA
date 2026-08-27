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

Phase 1 established the actual implementation state of the repository and identified the exact blockers between the current foundation and a validated first-movie production run.

---

## CURRENT OBJECTIVE

Build the first-movie production pipeline in GitHub before running a real movie on the Windows PC.

Immediate priority:

1. Fix configuration/runtime portability.
2. Establish canonical per-movie project/artifact paths.
3. Harden source/subtitle/AD ingestion.
4. Establish canonical scene/timeline data.
5. Build validated movie intelligence.
6. Fix and harden local LLM structured output.
7. Build recap generation.
8. Integrate and validate local TTS.
9. Build script-to-scene edit mapping.
10. Build final FFmpeg rendering.
11. Build final narration subtitles.
12. Build automated QA gate.
13. Build validated resume/recovery behavior.
14. Only then run Movie #1 on the PC.

---

## COMPLETED / PROVEN

[X] Repository established
[X] Project-control system established
[X] Architecture decisions recorded
[X] Source discovery foundation
[X] FFprobe media inspection foundation
[X] Subtitle discovery/extraction/conversion foundation
[X] SRT validation foundation
[X] Whisper.cpp environment validation
[X] Full AD audio -> whisper.cpp -> timestamped SRT test
[X] Basic project state artifact
[X] Tkinter production-control foundation
[X] Gitignore protection for large source media
[X] Full Phase 1 implementation audit

---

## CURRENT BLOCKERS

[ ] Hard-coded runtime paths
[ ] Canonical project workspace integration
[ ] Full scene/timeline index
[ ] Production movie intelligence
[ ] Reliable structured LLM output
[ ] Production TTS integration
[ ] Script-to-scene synchronization
[ ] Complete final renderer
[ ] Final narration subtitles
[ ] Automated final QA
[ ] Full resume/recovery state machine

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
