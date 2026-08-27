# ARK X CINEMA — ARCHITECTURE DECISIONS

This file contains decisions that define the architecture.

A superseding decision must explicitly identify the decision it replaces.

---

# DECISION-001 — AD AUDIO IS TRANSCRIBED INTO AD SRT

**Date:** 2026-08-27  
**Status:** LOCKED

## Decision

The separately supplied Audio Description audio file is processed by
whisper.cpp to generate a timestamped SRT.

## Input

AD audio file.

## Processing

whisper.cpp.

## Output

Timestamped AD SRT.

## Pipeline

AD AUDIO
  ->
WHISPER.CPP
  ->
AD SRT
  ->
MOVIE INTELLIGENCE

## Reason

The AD audio contains both:
- spoken/dialogue information
- visual/action descriptions

The visual/action descriptions are valuable movie-understanding data.

## Explicit clarification

We do NOT require an existing AD SRT as an input asset.

The AD SRT is generated from the AD audio.

## Supersession rule

Do not change this architecture merely because another subtitle source
exists.

A future replacement requires a new explicit architecture decision.

---

# DECISION-002 — AD IS A PRIMARY INTELLIGENCE SOURCE

**Date:** 2026-08-27  
**Status:** LOCKED

The AD transcript must not be treated as disposable secondary context.

It is a structured source of:
- visual descriptions
- actions
- scene context
- spoken information
- timing

The system should preserve these attributes for downstream movie
intelligence and scene selection.

---

# DECISION-003 — PROJECT FILES ARE THE LONG-TERM SOURCE OF TRUTH

**Date:** 2026-08-27  
**Status:** LOCKED

Chat history and AI memory are useful but are not sufficient as the
permanent project record.

The project must maintain machine-readable/human-readable documentation
inside the ARK_X_CINEMA directory.

Required control documents:

- PROJECT_STATE.md
- CHANGELOG.md
- DECISIONS.md
- TEST_RESULTS.md
- CURRENT_TASK.md

Git provides historical file versions.

