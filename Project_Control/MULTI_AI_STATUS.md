# ARK X CINEMA — MULTI-AI STATUS

**Repository:** https://github.com/exhinc/ARK_X_CINEMA  
**Purpose:** Shared, evidence-based status document for all AI agents and the human operator.

**Last updated:** 2026-09-03

---

## 0. STATUS RULE

No single AI may declare final production truth. Repository claims must cite current evidence. PC-dependent behavior remains unverified until tested on the target Windows machine.

---

## 1. ACTIVE MULTI-AI COLLABORATION PROTOCOL

The mandatory shared startup, authority/conflict-resolution, current-commit CI, and change-record rules are defined in:

`Project_Control/AI_COLLABORATION_PROTOCOL.md`

All ChatGPT, Claude, and Grok work must follow that protocol before significant repository changes.

---

## 2. ACTIVE EXECUTION ARCHITECTURE DECISION

The active runtime/execution architecture decision is recorded in:

`Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`

It governs local-first execution, optional accelerator/cloud experiments, replaceable LLM backends, long-movie persistence, FFmpeg usage, benchmark-first runtime decisions, and monetization-oriented editing policy. It supplements this status record; it does not prove PC validation or production readiness.

---

## 3. AGREED CURRENT FACTS

- `AGENTS.md` is the authoritative AI engineering contract.
- `Project_Control/AI_COLLABORATION_PROTOCOL.md` is the mandatory multi-AI coordination procedure.
- `Project_Control/AUDIT_LEDGER.md` records the completed controlled forensic GitHub audit.
- The active execution architecture decision is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`.
- Architecture decision DECISION-001 remains locked for the separate AD audio -> whisper.cpp -> timestamped AD SRT -> movie intelligence boundary; the newer execution decision does not replace that source-specific constraint.
- The historical full AD transcription test for *The Platform (2019)* recorded successful AD audio -> whisper.cpp -> timestamped SRT conversion.
- Current `master` contains repository-relative runtime configuration, canonical per-movie workspace/source-manifest support, subtitle/AD ingestion, deterministic timeline processing, bounded evidence packets, local Ollama integration, structured-output validation, recap-script generation, resumable checkpoints, Piper TTS integration, deterministic script-to-scene edit mapping, final recap subtitles, deterministic FFmpeg assembly, deterministic FFprobe QA, and the full Stage-A runner composition.
- PR #7 was merged into `master` on 2026-08-28 as commit `3fd4a87c2a68df98eff3652fbc65c4f2f972267e`.
- The post-merge GitHub Actions run for that master commit succeeded: workflow `ARK X Cinema Tests`, run #123, job `tests`.
- Issue #1 (CI regression) is closed with completed state.
- The old PR #6 is historical/unmerged and is not evidence against current master; PR #7 was the controlled current-master rebuild and merge.
- Current repository evidence therefore supports a **GitHub-side Stage-A implementation complete / PC validation pending** status.

---

## 4. PRODUCTION BOUNDARY

### GitHub-side implementation status: COMPLETE

The code and portable regression suite now cover the intended Stage-A production chain:

```text
INGESTION
  -> AD TRANSCRIPTION BOUNDARY
  -> CANONICAL TIMELINE
  -> BOUNDED EVIDENCE
  -> LOCAL LLM INTELLIGENCE
  -> RECAP SCRIPT
  -> PIPER TTS
  -> SCRIPT/SCENE EDIT MANIFEST
  -> FINAL RECAP SRT
  -> FFMPEG ASSEMBLY
  -> FINAL MEDIA QA
```

Underlying all stages: checkpoint/state handling, artifact validation, provenance, and one-heavy-AI-stage-at-a-time policy.

### PC/runtime status: UNVERIFIED

The following are still deliberately unverified because GitHub cannot reproduce the user's Windows runtime:

1. Real whisper.cpp execution, speed, peak RAM, and AD->SRT quality.
2. Real Ollama/Qwen execution, structured-output quality, speed, and peak RAM.
3. Real Piper execution, voice quality, speed, and peak RAM.
4. Real FFmpeg rendering against real movie media.
5. Real final-media playback/inspection.
6. Interrupted-run/resume behavior on real media.
7. Approximately <=2 GB additional AI workload RAM target.
8. Full first-movie end-to-end success and human editorial QA.

No GitHub result should be interpreted as proof of these items.

---

## 5. EVIDENCE SNAPSHOT

| Area | Current evidence | Status |
|---|---|---|
| Runtime configuration | `Engine/runtime_config.py` + runtime tests | COMPLETE / repository-tested |
| Canonical workspace | `Engine/project_workspace.py` + ingestion tests | COMPLETE / repository-tested |
| AD ingestion | `Engine/transcription_stage_adapter.py` and source-manifest path | COMPLETE / boundary-tested; PC execution unverified |
| Timeline | deterministic timeline engine + tests | COMPLETE / repository-tested |
| Intelligence | Ollama adapter + structured-output validation + tests | COMPLETE / repository-tested; real model unverified |
| Recap script | recap engine + adapter + tests | COMPLETE / repository-tested; real model unverified |
| TTS | Piper engine + adapter + tests | COMPLETE / repository-tested; PC runtime unverified |
| Edit mapping | `Engine/edit_manifest_engine.py` + tests | COMPLETE / repository-tested |
| Recap subtitles | `Engine/recap_subtitle_engine.py` + tests | COMPLETE / repository-tested |
| Video assembly | `Engine/ffmpeg_video_engine.py` + tests | COMPLETE / command construction tested; real encoding unverified |
| Final QA | `Engine/media_qa_inspector.py` + tests | COMPLETE / repository-tested; real media unverified |
| Stage-A runner | `Engine/stage_a_runner.py` + tests | COMPLETE / repository-tested; real end-to-end unverified |
| Checkpoint/resume | `checkpoint.py`, `stage_state.py`, `resumable_orchestrator.py` + tests | COMPLETE / repository-tested; real crash/recovery unverified |
| CI | master run #123 success for the Stage-A merge commit; later documentation changes require current-commit CI verification | COMPLETE / repository evidence for merge; current docs baseline requires fresh CI |

---

## 6. LONG-MOVIE READINESS

Repository design target for long movies:

- Keep artifacts per movie under `Projects/<movie>/`.
- Process transcript/timeline/evidence structures as bounded, explicit artifacts rather than one monolithic prompt.
- Preserve stage boundaries so interrupted work can resume from the last verified artifact.
- Validate artifact integrity before skipping a completed stage.
- Do not retain large intermediate media longer than required by the production policy.
- Keep final outputs separate from source media and historical backups.
- Treat disk space as a runtime preflight condition before full-movie processing.

The broader runtime strategy is governed by `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`; the exact large-movie throughput, memory profile, and interruption behavior remain PC validation items.

---

## 7. MULTI-AI CONSENSUS RULE

The GitHub engineering baseline is now sufficiently evidenced for the next controlled decision, but the project should not claim final Stage-A production readiness until at least one additional AI assessment or the human operator explicitly accepts this evidence.

Until that consensus event occurs, Issue #3 remains the active coordination gate.

---

## 8. NEXT CONTROLLED STEP

After the GitHub-only gate is accepted, run PC validation in this order:

```text
TINY SYNTHETIC / SHORT MEDIA
        -> MEDIUM REAL-MEDIA TEST
        -> FIRST FULL MOVIE
        -> HUMAN QA
        -> STAGE-A RELIABILITY
        -> SCALE TO 1/DAY
        -> 2/DAY
        -> 3/DAY
```

Do not jump directly to a full movie merely because CI is green.
