# ARK X CINEMA — PROJECT STATE

**Project:** ARK X Cinema  
**Purpose:** Automated YouTube movie-recap production system  
**Current State:** Stage-A GitHub implementation complete; PC validation gate pending  
**Last Updated:** 2026-09-03

---

## 0. ACTIVE MULTI-AI COLLABORATION PROTOCOL

The mandatory coordination procedure for ChatGPT, Claude, Grok, and future owner-authorized AI agents is recorded in:

`Project_Control/AI_COLLABORATION_PROTOCOL.md`

It defines startup inspection, architectural-governance boundaries, implementation-evidence rules, current-commit CI verification, change recording, and handoff requirements. It does not replace this project-state record or the active architecture decision.

---

## 1. ACTIVE ARCHITECTURE DECISION

The current runtime and execution-architecture decisions are recorded in:

`Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`

That document is the active decision record for local-first execution, optional accelerator/cloud experiments, replaceable LLM backends, long-movie persistence, FFmpeg usage, runtime benchmarking, and monetization-oriented editing policy. It supplements this project-state record; it does not override the PC validation gate below.

---

## 2. PROJECT OBJECTIVE

ARK X Cinema is a $0/month movie-recap production system designed to automate as much of the production workflow as practical while retaining final human QA/approval.

Primary completion criterion:
- Reliably process one real, legally obtained 3–4 hour movie through the intended pipeline on the target Windows PC and produce a finished recap video that passes the required automated and human QA checks.

Supporting requirements:
- Free/open-source-first tooling
- Local processing wherever practical
- Low-RAM Windows laptop compatibility
- Legal movie/source acquisition
- No piracy or DRM bypass

Throughput is **not** a fixed project completion quota. Once reliable one-movie processing is achieved, practical throughput is measured empirically from actual end-to-end processing time, hardware limits, storage, and workload conditions. The system is not required to produce a predetermined number of movies per day for the core project to be considered complete.

---

## 3. HARDWARE BASELINE

Recorded target workstation baseline:
- HP Laptop 15-dy2xxx
- Windows 11
- approximately 7.65 GB usable RAM
- 11th Gen Intel Core i3-1115G4
- Intel UHD Graphics
- approximately 475.6 GB C: drive, with approximately 143.2 GB free at the recorded snapshot

The approximate <=2 GB additional AI-workload RAM target remains a validation target, not a proven result.

---

## 4. LOCKED AD ARCHITECTURE

The Audio Description asset is supplied separately from the movie.

We do not assume an AD SRT already exists.

```text
AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT -> MOVIE INTELLIGENCE
```

The AD transcription is a primary movie-understanding source containing spoken/dialogue information, visual descriptions, action descriptions, and scene/context information.

Do not replace this architecture without an explicit superseding decision.

---

## 5. CURRENT GITHUB IMPLEMENTATION STATUS

### Stage-A implementation: COMPLETE on `master`

Current master contains the complete repository-side production composition:

1. repository-relative runtime configuration
2. canonical per-movie workspace and source manifest
3. subtitle and external AD ingestion
4. whisper.cpp integration boundary
5. deterministic canonical timeline
6. bounded evidence packets
7. local Ollama intelligence adapter
8. strict structured-output extraction/validation
9. recap script engine + adapter
10. Piper TTS engine + timing metadata
11. deterministic script-to-scene edit mapping
12. final recap subtitle generation
13. deterministic FFmpeg recap assembly
14. deterministic FFprobe final-media QA
15. complete resumable Stage-A runner
16. checkpoint/state integrity and prerequisite enforcement
17. portable regression tests + GitHub Actions

PR #7 supplied the controlled current-master Stage-A integration and was merged as commit `3fd4a87c2a68df98eff3652fbc65c4f2f972267e`.

### CI evidence

The latest coordination-hardening master commit `98625c2b5aa6ddb9cdb53f1318449e4feb7b8679` was manually run through GitHub Actions after the coordination audit and completed with **Status: Success** (workflow run #33721190514 / job #100540507339). The run produced one Node.js deprecation warning for actions/checkout@v4 and actions/setup-python@v5; the warning did not cause failure.

Issue #1, the historical CI regression, is closed with completed state.

---

## 6. PC-ONLY VALIDATION STILL REQUIRED

GitHub CI cannot prove the user's Windows environment. The following remain UNVERIFIED:

- real whisper.cpp execution, speed, RAM, and AD->SRT quality
- real Ollama/Qwen execution, structured-output quality, speed, and RAM
- real Piper execution, voice quality, speed, and RAM
- real FFmpeg encoding and playback against real media
- real final-media QA on produced media
- interrupted-run/resume on real media
- <=2 GB additional AI workload RAM target
- first full-movie end-to-end success
- final human editorial/quality judgment

Therefore the project is **not yet declared Stage-A production-ready**.

---

## 7. NEXT MILESTONE

The next milestone is controlled PC validation, not another architectural rewrite.

```text
TINY TEST
   -> MEDIUM REAL-MEDIA TEST
   -> FIRST FULL 3–4 HOUR MOVIE
   -> HUMAN QA
   -> STAGE-A RELIABILITY
```

After core reliability is established, throughput may be measured and optimized empirically. Additional movies may then be processed sequentially as system capacity allows; no fixed daily quota is required for project completion.

No full movie is to be used as the first runtime test.

---

## 8. HANDOFF / CURRENT-STATE RULE

`Project_Control/AI_COLLABORATION_PROTOCOL.md` is the mandatory multi-AI coordination procedure. `AGENTS.md` is the shared engineering contract. `Project_Control/DECISIONS.md` governs architectural permission. Current master code/tests and applicable current-commit CI establish what is implemented/verified. Historical files, including `ARK_X_Cinema_Current_State.txt`, are evidence only and must not override active Project_Control records or current master evidence.
