# ARK X CINEMA — PROJECT STATE

**Project:** ARK X Cinema  
**Purpose:** Automated YouTube movie-recap production system  
**Current State:** GitHub implementation complete; Windows validation pending  
**Last Updated:** 2026-09-03

---

## 0. ACTIVE MULTI-AI COLLABORATION PROTOCOL

The mandatory coordination procedure for ChatGPT, Claude, Grok, and future owner-authorized AI agents is recorded in `Project_Control/AI_COLLABORATION_PROTOCOL.md`.

It defines startup inspection, architectural governance, implementation evidence, current-commit CI verification, change recording, and handoff requirements.

---

## 1. ACTIVE EXECUTION ARCHITECTURE DECISION

The active runtime/execution architecture is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`.

It governs local-first execution, optional accelerator/cloud experiments, replaceable LLM backends, long-movie persistence, FFmpeg usage, benchmark-first runtime decisions, and monetization-oriented editing policy. It does not constitute Windows runtime validation.

---

## 2. PROJECT OBJECTIVE

ARK X Cinema is a $0/month movie-recap production system designed to automate as much of the production workflow as practical while retaining final human QA and approval.

**Core completion criterion:** Reliably process one real, legally obtained 3–4 hour movie through the intended pipeline on the target Windows PC and produce a finished recap video that passes the required automated and human QA checks.

Supporting requirements:
- Free/open-source-first tooling
- Local processing wherever practical
- Low-RAM Windows laptop compatibility
- Legal movie/source acquisition
- No piracy or DRM bypass

There is no fixed daily movie quota. After the core one-movie goal is achieved, throughput is measured and optimized from actual processing time, hardware limits, storage, and workload conditions.

---

## 3. HARDWARE BASELINE

Recorded target workstation baseline:
- HP Laptop 15-dy2xxx
- Windows 11
- approximately 7.65 GB usable RAM
- 11th Gen Intel Core i3-1115G4
- Intel UHD Graphics
- approximately 475.6 GB C: drive, with approximately 143.2 GB free at the recorded snapshot

The approximate ≤2 GB additional AI-workload RAM target remains a validation target, not a proven result.

---

## 4. LOCKED AD ARCHITECTURE

The Audio Description asset is supplied separately from the movie. We do not assume an AD SRT already exists.

```text
AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT -> MOVIE INTELLIGENCE
```

The AD transcription is a primary movie-understanding source containing spoken/dialogue information, visual descriptions, action descriptions, and scene/context information.

Do not replace this architecture without an explicit superseding decision.

---

## 5. CURRENT GITHUB IMPLEMENTATION STATUS

### Stage-A implementation: COMPLETE on `master`

Current master contains the repository-side production composition, including:

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

PR #7 supplied the controlled Stage-A integration and was merged as commit `3fd4a87c2a68df98eff3652fbc65c4f2f972267e`.

### Current CI evidence

The current master commit for this control record must be verified by GitHub Actions before it is described as CI-verified. Repository tests do not substitute for Windows runtime validation.

---

## 6. WINDOWS-ONLY VALIDATION STILL REQUIRED

GitHub CI cannot prove the user's Windows environment. The following remain UNVERIFIED:

- real whisper.cpp execution, speed, resource use, and AD-to-SRT quality
- real Ollama/Qwen execution, structured-output quality, speed, and resource use
- real Piper execution, voice quality, speed, and resource use
- real FFmpeg encoding and playback against real media
- real final-media QA
- interrupted-run/resume on real media
- the approximately ≤2 GB additional AI-workload RAM target
- one complete real 3–4 hour movie end-to-end
- final human editorial/quality judgment

Therefore the core production goal is not yet declared complete.

---

## 7. NEXT MILESTONE

The next milestone is controlled Windows validation, not another architectural rewrite.

```text
PC PREFLIGHT
   -> TINY / SHORT TEST
   -> MEDIUM REAL-MEDIA TEST
   -> FIRST FULL 3–4 HOUR MOVIE
   -> HUMAN QA
   -> CORE RELIABILITY
```

After core reliability is established, throughput may be measured and optimized empirically. Additional movies may then be processed sequentially as system capacity allows.

No fixed daily quota is required for project completion.

---

## 8. HANDOFF / CURRENT-STATE RULE

`Project_Control/AI_COLLABORATION_PROTOCOL.md` is the mandatory multi-AI coordination procedure. `AGENTS.md` is the shared engineering contract. `Project_Control/DECISIONS.md` governs architectural permission. Current master code/tests and applicable current-commit CI establish what is implemented and verified. Historical files, including `ARK_X_Cinema_Current_State.txt`, are evidence only and must not override active Project_Control records or current master evidence.
