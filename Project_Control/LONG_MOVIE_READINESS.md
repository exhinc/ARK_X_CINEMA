# ARK X CINEMA — LONG-MOVIE READINESS

**Status:** GitHub-side design complete; runtime validation pending  
**Last updated:** 2026-08-31

## Purpose

This document defines the safeguards used before attempting a full-length movie. It is a design and engineering contract, not proof of runtime performance.

## 1. Movie-scoped persistence

All production artifacts must belong to a specific movie workspace under:

```text
Projects/<movie>/
```

The source manifest, transcript outputs, timeline, bounded evidence, intelligence, script, narration metadata, edit manifest, subtitles, final video, QA results, and stage state must be traceable to that movie.

Global folders such as `Logs/`, `Backups/`, or historical fixtures are never the authoritative source for a current movie run.

## 2. Bounded intelligence

Do not send an entire movie transcript or unrestricted AD corpus to the local LLM in one prompt. The timeline and evidence stages must preserve source provenance while providing bounded scene-level or packet-level inputs.

This reduces memory pressure and limits the blast radius of malformed model output.

## 3. Deterministic stage boundaries

A long movie is processed as ordered stages with explicit artifacts:

```text
INGESTION
TRANSCRIPTION
TIMELINE
INTELLIGENCE
SCRIPT
TTS
VIDEO
QA
```

A stage may be skipped only when its expected artifact exists and passes the stage-state integrity rules.

## 4. Interruption and resume

On interruption or failure:

- preserve previously verified completed artifacts;
- record the failed stage and error;
- retry from the earliest invalid/incomplete stage;
- never treat a missing or modified completed artifact as safely resumable;
- never silently erase the earlier failure history.

## 5. Large artifact handling

For large SRTs, many scenes, and large manifests:

- use streaming/iterative parsing where practical;
- avoid unnecessary duplicate in-memory copies of full text blobs;
- keep evidence packets bounded;
- write intermediate JSON artifacts to disk instead of retaining every stage result in process memory;
- keep temporary render products separate from final outputs;
- verify paths before processing.

## 6. Disk-space policy

Before a full movie run, the runtime validation procedure must check:

- free space on the workspace volume;
- source media size;
- expected intermediate-artifact growth;
- expected final render size;
- available headroom for temporary FFmpeg files.

A run should fail closed rather than start a full render with obviously insufficient free space.

## 7. Cleanup policy

Artifacts fall into four classes:

1. **Source** — never deleted automatically by the pipeline.
2. **Authoritative production artifacts** — retained for resume, provenance, and QA.
3. **Temporary render artifacts** — eligible for cleanup after successful finalization and QA.
4. **Historical backups/test fixtures** — preserved unless explicitly archived/deleted by a separate decision.

Cleanup must never delete the only copy of an artifact required for resume or auditability.

## 8. Validation sequence

The first runtime validation must proceed from small to large:

```text
TINY TEST
  -> MEDIUM REAL-MEDIA TEST
  -> FIRST FULL MOVIE
```

Each step must pass before advancing. A failure must be repaired and re-tested rather than bypassed.

## 9. Non-claims

This design does not prove:

- completion time for a full movie;
- peak RAM on the target machine;
- Whisper.cpp transcription throughput;
- Ollama generation throughput;
- Piper generation throughput;
- FFmpeg render throughput;
- successful crash recovery on real media;
- suitability for 3 videos/day.

Those are runtime measurements and remain explicitly unverified until the Windows validation gate produces evidence.
