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
- `Project_Control/DECISIONS.md` contains DECISION-004 locking the multi-AI authority/handoff rules.
- `GROK.md` is the dedicated Grok entry point; `CLAUDE.md` is the dedicated Claude entry point.
- `docs/AI_HANDOFF.md` is the persistent cross-agent handoff.
- The historical root snapshot `ARK_X_Cinema_Current_State.txt` is dated 2026-08-26 and is evidence only, not current project state.
- Current `master` contains repository-relative runtime configuration, canonical per-movie workspace/source-manifest support, subtitle/AD ingestion, deterministic timeline processing, bounded evidence packets, local Ollama integration, structured-output validation, recap-script generation, resumable checkpoints, Piper TTS integration, deterministic script-to-scene edit mapping, final recap subtitles, deterministic FFmpeg assembly, deterministic FFprobe QA, and the full Stage-A runner composition.
- PR #7 was merged into `master` on 2026-08-28 as commit `3fd4a87c2a68df98eff3652fbc65c4f2f972267e`.
- The post-merge GitHub Actions run for that master commit succeeded: workflow `ARK X Cinema Tests`, run #123, job `tests`.
- Issue #1 (CI regression) is closed with completed state.
- The old PR #6 is historical/unmerged and is not evidence against current master; PR #7 was the controlled current-master rebuild and merge.
- The GitHub-only coordination hardening is implemented in the repository, but Issue #3 remains the formal acceptance gate until its stale historical checklist/state is reconciled and at least one independent second-AI or human acceptance is recorded.

---

## 4. GITHUB-SIDE IMPLEMENTATION BOUNDARY

The repository and portable regression suite cover the intended Stage-A production chain:

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

This remains repository-side implementation evidence, not proof of Windows runtime success.

---

## 5. PC/RUNTIME STATUS: UNVERIFIED

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

## 6. COORDINATION ACCEPTANCE GATE

Issue #3 is the formal GitHub-only coordination/acceptance gate. Its original body contains historical 2026-08-28 checklist text and should not be read as current status without reconciling it against current `master` evidence.

Current coordination hardening evidence:

- shared startup sequence: implemented in `AI_COLLABORATION_PROTOCOL.md`
- architectural-governance vs implementation-truth distinction: implemented
- current-commit-only CI rule: implemented
- significant-change record rule: implemented
- dedicated Grok entry point: implemented
- Claude entry point convergence: implemented
- persistent handoff convergence: implemented
- historical root state snapshot explicitly quarantined: implemented

The remaining acceptance event is independent review by another AI or the human operator, not another architecture rewrite.

---

## 7. NEXT CONTROLLED STEP

After Issue #3 acceptance and current-commit CI verification, close the GitHub-only gate and proceed to controlled Windows validation:

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

Do not jump directly to a full movie merely because repository CI is green.
