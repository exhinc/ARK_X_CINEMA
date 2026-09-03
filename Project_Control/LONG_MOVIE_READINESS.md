# ARK X CINEMA — LONG-MOVIE READINESS

**Status:** GitHub-side design complete; Windows validation pending  
**Last updated:** 2026-09-03

**Related architecture decision:** `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`

This document defines the safeguards for processing a full-length movie. It is a design and engineering contract, not proof of runtime performance.

## 1. Movie-scoped persistence

All production artifacts must belong to a specific movie workspace under:

```text
Projects/<movie>/
```

Artifacts must remain traceable to that movie. Global folders and historical fixtures are not authoritative sources for a current movie run.

## 2. Bounded intelligence

Do not send an entire movie transcript or unrestricted AD corpus to the local LLM in one prompt. Preserve source provenance while providing bounded scene-level or packet-level inputs.

This reduces memory pressure and limits the effect of malformed model output.

## 3. Deterministic stage boundaries

A long movie is processed as ordered stages with explicit artifacts:

```text
INGESTION -> TRANSCRIPTION -> TIMELINE -> INTELLIGENCE -> SCRIPT -> TTS -> VIDEO -> QA
```

A stage may be skipped only when its expected artifact exists and passes the stage-state integrity rules.

## 4. Interruption and resume

On interruption or failure:

- preserve verified completed artifacts;
- record the failed stage and error;
- retry from the earliest invalid or incomplete stage;
- never treat a missing or modified artifact as safely resumable;
- never erase earlier failure history.

## 5. Large-artifact handling

For large SRTs, many scenes, and large manifests:

- use streaming or iterative parsing where practical;
- avoid unnecessary duplicate in-memory copies of full text blobs;
- keep evidence packets bounded;
- write intermediate JSON artifacts to disk instead of retaining every result in process memory;
- keep temporary render products separate from final outputs;
- verify paths before processing.

## 6. Disk-space policy

Before a full movie run, check:

- free space on the workspace volume;
- source media size;
- expected intermediate-artifact growth;
- expected final render size;
- available headroom for temporary FFmpeg files.

A run should fail closed rather than begin a full render when free space is obviously insufficient.

## 7. Cleanup policy

Artifacts fall into four classes:

1. **Source** — never deleted automatically.
2. **Authoritative production artifacts** — retained for resume, provenance, and QA.
3. **Temporary render artifacts** — eligible for cleanup after successful finalization and QA.
4. **Historical backups/test fixtures** — preserved unless explicitly archived or deleted by a separate decision.

Cleanup must never delete the only copy of an artifact required for resume or auditability.

## 8. Validation sequence

The first runtime validation must proceed from small to large:

```text
TINY / SHORT TEST
  -> MEDIUM REAL-MEDIA TEST
  -> FIRST FULL 3–4 HOUR MOVIE
  -> HUMAN QA
  -> CORE RELIABILITY
```

Each step must pass before advancing. A failure must be repaired and re-tested rather than bypassed.

## 9. Completion boundary

The core project completion criterion is one reliable real 3–4 hour movie from input through final recap and required QA. Throughput is measured only after that criterion is achieved.

Additional movies may then be processed sequentially as actual hardware, storage, and processing time permit. There is no fixed daily quota.
