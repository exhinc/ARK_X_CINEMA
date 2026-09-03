# ARK X CINEMA — MULTI-AI COLLABORATION PROTOCOL

**Status:** ACTIVE
**Date:** 2026-09-03

This document defines the mandatory coordination procedure for ChatGPT, Claude, Grok, and any future AI agent explicitly added by the owner.

## 1. Mandatory startup sequence

Before proposing or making a repository change, the agent must:

1. Read `AGENTS.md`.
2. Read `Project_Control/PROJECT_STATE.md`.
3. Read `Project_Control/CURRENT_TASK.md`.
4. Read `Project_Control/MULTI_AI_STATUS.md`.
5. Read `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`.
6. Read `Project_Control/DECISIONS.md`.
7. Read `docs/PROJECT_STATUS.md` and `docs/AI_HANDOFF.md` when the task affects project status or multi-agent coordination.
8. Inspect the actual affected code/tests.
9. Inspect recent `master` commits.
10. Check GitHub Actions for the current commit before describing CI as verified.

An agent must not rely on a previous chat as a substitute for this repository inspection.

## 2. Authority and conflict resolution

The project has two distinct kinds of authority and they must not be confused.

### Architectural governance

Locked architecture decisions define what changes are permitted. Code must not silently supersede a locked architectural decision. To intentionally change a locked architecture, the agent must create a new explicit decision identifying the decision being superseded, the evidence supporting the change, affected paths, compatibility/rollback implications, and required validation.

### Implementation truth

For the implementation that is currently on `master`, use this evidence order:

```text
CURRENT-COMMIT VERIFIED TEST / CI EVIDENCE
        >
CURRENT MASTER CODE / VERIFIED ARTIFACTS
        >
CURRENT PROJECT STATUS / HANDOFF RECORDS
        >
INDIVIDUAL AI RECOMMENDATION
        >
OLD CHAT HISTORY
```

A passing current-commit test/CI result is stronger evidence about observed behavior than an untested code inspection. Current code remains the implementation source of truth when interpreting what is actually present. Project status and handoff records explain state and intent but do not override code or test evidence.

No AI may treat another AI's opinion as authoritative merely because it sounds more confident.

When a current implementation conflicts with a locked architecture decision, treat it as a **consistency/defect finding**, not as automatic permission to redefine the architecture. Determine whether the implementation is wrong or whether a formal superseding decision is required.

## 3. Current-commit CI rule

A CI result proves the commit/tree that was actually tested.

```text
CURRENT MASTER COMMIT
        ->
CI FOR THAT COMMIT
        ->
CLAIM VERIFIED
```

Historical CI runs remain historical evidence. They must not be presented as proof for later commits unless the exact tree/commit was tested and the result is applicable.

## 4. Change-record rule

Every significant AI-driven repository change must be represented by:

- a Git commit with a clear message;
- an update to `Project_Control/CHANGELOG.md` when the change is project-significant;
- an architecture decision in `Project_Control/DECISIONS.md` when the change establishes or changes an architectural rule.

The minimum useful change record is:

```text
Agent:
Date:
Commit:
Files/area:
What changed:
Why:
Evidence/tests:
Known limitations:
Next action:
```

Small typo-only/documentation corrections do not require an expanded narrative beyond the normal Git commit history unless they change project control behavior.

## 5. Safe modification rule

Before editing, establish the current state. During editing:

- preserve established architecture unless a documented decision changes it;
- make the smallest safe change;
- do not overwrite another agent's work based on old chat context;
- add or update focused tests when behavior changes;
- synchronize affected control/status documents;
- record unresolved defects rather than hiding them.

After editing, perform the repository's required re-scan and current-commit verification.

## 6. Production-readiness rule

No agent may declare production readiness from CI alone.

The project must continue to distinguish:

```text
REPOSITORY IMPLEMENTATION
        !=
PC RUNTIME VALIDATION
        !=
END-TO-END PRODUCTION RELIABILITY
```

The Windows validation gate, measured RAM/performance, real-media tests, interruption/resume testing, and human QA remain required where specified by the current project state.

## 7. Handoff rule

At the end of a significant task, leave the repository in a state where the next AI can continue without relying on private conversation memory. Update the relevant status/control record and make the next required action explicit.

The repository, not any individual AI's memory, is the persistent team memory.
