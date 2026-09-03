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

---

# DECISION-004 — MULTI-AI COLLABORATION AUTHORITY AND HANDOFF PROTOCOL

**Date:** 2026-09-03  
**Status:** LOCKED

## Decision

ChatGPT, Claude, Grok, and any future AI agent explicitly added by the owner
must use the same repository-backed startup, authority, conflict-resolution,
CI-verification, and change-record rules.

The mandatory procedure is defined in:

`Project_Control/AI_COLLABORATION_PROTOCOL.md`

## Architectural governance

Locked architecture decisions constrain what changes are permitted. Current
code does not silently supersede a locked architecture decision. If the
implementation and a locked decision conflict, the agent must treat the
condition as a consistency/defect finding and determine whether the code should
be repaired or whether a new explicit superseding decision is required.

## Implementation truth

For the implementation currently on `master`, observed behavior follows this
evidence order:

CURRENT-COMMIT VERIFIED TEST / CI EVIDENCE
>
CURRENT MASTER CODE / VERIFIED ARTIFACTS
>
CURRENT PROJECT STATUS / HANDOFF RECORDS
>
INDIVIDUAL AI RECOMMENDATION
>
OLD CHAT HISTORY

A current-commit test/CI result is stronger evidence about tested behavior than
an untested code inspection. Status and handoff files explain intent/state but
do not override implementation evidence.

## Startup requirement

Agents must complete the repository inspection sequence defined in the
collaboration protocol before proposing or making significant changes.

## CI requirement

Historical CI results do not prove newer commits. Claims about CI status must
reference the current commit/tree that was actually tested.

## Change history requirement

Significant project changes are recorded in `Project_Control/CHANGELOG.md`.
Architectural changes are recorded in this file. Git commit history remains
the immutable chronological record.

---

# DECISION-005 — CORE PRODUCTION COMPLETION AND THROUGHPUT POLICY

**Date:** 2026-09-03  
**Status:** LOCKED

## Decision

The core ARK X Cinema production-completion criterion is **reliable end-to-end processing of one real 3–4 hour movie** on the target Windows PC, using legally obtained source material, through the intended pipeline to a finished recap video that passes required automated and human QA.

A fixed daily movie quota is **not** a core completion requirement.

After one full-length movie is proven reliable, additional throughput is treated as an empirical performance property of the system. Practical throughput depends on actual processing time, hardware capacity, RAM behavior, storage, workload characteristics, and later optimization.

The system may process additional movies sequentially whenever capacity permits. Targets such as one movie/day or multiple movies/day may be measured or optimized later, but failure to reach any predetermined daily quota does not mean the core project is incomplete.

## Reason

The project is intended to automate reliable production, not to impose an arbitrary production quota. A fixed daily target can distort engineering decisions and encourage premature scaling before one complete long-movie run is proven stable.

## Validation boundary

The one-movie completion criterion still requires real Windows validation, real media, measured resource use, successful end-to-end execution, and human QA. Repository implementation and CI remain necessary but are not sufficient evidence of completion.

## Supersession rule

Any future change to the core completion criterion should be recorded as a new explicit decision with evidence explaining why the target is being changed.
