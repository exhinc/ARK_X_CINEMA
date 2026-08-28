# ARK X CINEMA — CURRENT TASK

**Last Updated:** 2026-08-28

---

## CURRENT PHASE

PHASE 2 — PRODUCTION ENGINE FOUNDATION

---

## PHASE 1 STATUS

**COMPLETE — FORENSIC AUDIT PROTOCOL ESTABLISHED; EXHAUSTIVE AUDIT NOT YET PERFORMED**

The repository now contains the permanent forensic-audit protocol and ledger mechanism required for a future full repository audit. Establishing the protocol does **not** mean that a new exhaustive forensic audit has already been completed.

Authoritative audit record:

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

### Build #2 — Canonical Workspace / Source Manifest

**PASS — implemented and integrated**

Completed:

- Canonical per-movie workspace.
- Deterministic source manifest.
- Source hashing/provenance.
- Explicit single-video selection policy.
- Source package discovery tests.

### Build #3 — Evidence / Intelligence / Script Core

**PASS — implemented on `master`; real runtime validation remains outstanding**

Completed:

- Bounded evidence packets.
- Structured-output extraction and validation.
- Ollama intelligence adapter.
- Recap script engine and stage adapter.
- Regression tests for structured-output handling.

### Build #4 — Permanent Forensic Audit Protocol

**PASS — implemented 2026-08-28**

Completed:

- Extended `AGENTS.md` with a repository-wide forensic audit protocol.
- Added `Project_Control/AUDIT_LEDGER.md` for formal audit coverage and uncertainty tracking.
- Updated this task record so future agents use the ledger during full audits.

The audit protocol requires complete repository accounting, system reconstruction, repository-wide defect-pattern searches, configuration/security review, root-cause repair, changed-file blast-radius checks, and a second audit after repair.

Important distinction: **the protocol is established; the exhaustive forensic audit is a separate operation and has not yet been declared complete.**

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

## FULL-AUDIT RULE

Whenever a future task calls for a full repository audit, use `Project_Control/AUDIT_LEDGER.md` together with `AGENTS.md` and the other Project_Control records.

Do not declare full coverage until the ledger accounts for the repository and significant items are classified as INSPECTED, PARTIALLY INSPECTED, NOT APPLICABLE, UNVERIFIED, or BLOCKED.

The actual exhaustive audit must populate the ledger with repository paths/items, statuses, evidence, findings, fixes, verification notes, and remaining UNVERIFIED/BLOCKED items. The ledger itself must never be treated as evidence that those inspections have already occurred.

---

## HANDOFF

Before future development, read:

AGENTS.md
Project_Control/PROJECT_STATE.md
Project_Control/CURRENT_TASK.md
Project_Control/DECISIONS.md
Project_Control/CHANGELOG.md
Project_Control/TEST_RESULTS.md
Project_Control/IMPLEMENTATION_STATUS.md
Project_Control/AUDIT_LEDGER.md

Then inspect the actual code/files before making assumptions.
