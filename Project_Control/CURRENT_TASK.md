# ARK X CINEMA — CURRENT TASK

**Last Updated:** 2026-09-03

---

## ACTIVE MULTI-AI COLLABORATION PROTOCOL

All ChatGPT, Claude, and Grok work must follow `Project_Control/AI_COLLABORATION_PROTOCOL.md` before significant repository changes.

The protocol defines the shared startup sequence, architectural-governance rules, implementation-evidence rules, current-commit CI verification, safe modification procedure, and change-record requirements.

---

## ACTIVE EXECUTION ARCHITECTURE DECISION

The active runtime/execution architecture is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`. Read it before proposing changes to model runtime, cloud or accelerator execution, long-movie persistence, FFmpeg usage, or monetization-oriented editing policy.

This decision record defines architecture. It does not prove Windows runtime validation or production readiness.

---

## CURRENT PHASE

**PHASE 2 — GITHUB IMPLEMENTATION COMPLETE / WINDOWS VALIDATION PENDING**

The repository-side production composition and multi-AI coordination framework are implemented. The next engineering work is controlled validation on the target Windows machine.

---

## COMPLETED GITHUB WORK

### Build #1 — Runtime / Configuration Foundation
**PASS**

Repository-relative runtime configuration is wired into the active orchestration foundation.

### Build #2 — Canonical Workspace / Source Manifest
**PASS**

Per-movie workspace and deterministic source-manifest handling are implemented and tested.

### Build #3 — Evidence / Intelligence / Script Core
**PASS**

Bounded evidence packets, Ollama integration, structured-output validation, recap generation, and stage adapters are implemented and covered by portable tests.

### Build #4 — Permanent Forensic Audit Protocol
**PASS**

The permanent audit rules and `Project_Control/AUDIT_LEDGER.md` are established.

### Build #5 — Controlled Forensic Audit & Repair
**PASS**

The repository-wide controlled forensic audit was completed and recorded. Confirmed control and documentation defects were repaired and the repository was re-verified.

### Build #6 — Stage-A Downstream Production Integration
**PASS**

PR #7 was rebuilt from the audited `master` and merged as `3fd4a87c2a68df98eff3652fbc65c4f2f972267e`.

Integrated components include Piper TTS, script-to-scene edit mapping, final recap subtitles, FFmpeg assembly, FFprobe QA, the Stage-A runner, and focused regression coverage.

### Build #7 — Multi-AI Coordination Hardening
**IMPLEMENTED / ACCEPTANCE PENDING**

Implemented controls include the shared collaboration protocol, explicit architecture-versus-implementation authority, current-commit CI verification, change recording, dedicated agent entry points, persistent handoff, and historical-state quarantine.

### Build #8 — Core Production Goal Correction
**IMPLEMENTED / CI-VERIFIED**

The core completion criterion is now one reliable end-to-end 3–4 hour movie on the target Windows PC, ending in a finished recap that passes required automated and human QA. There is no fixed daily production quota.

---

## CURRENT COORDINATION CHECKPOINT

**GITHUB COORDINATION IMPLEMENTATION: COMPLETE**

Current `master` is the repository source of truth. GitHub Actions must pass for the exact current commit before that tree is described as CI-verified.

The remaining coordination step is the acceptance record defined by Issue #3: two independent AI reviews followed by human project-owner acceptance.

---

## WINDOWS VALIDATION GATE

**NOT YET COMPLETE**

Required evidence includes:

1. real whisper.cpp execution, AD-to-SRT quality, timing, and resource use;
2. real Ollama/Qwen execution, structured-output quality, speed, and resource use;
3. real TTS execution, quality, speed, and resource use;
4. real FFmpeg rendering and playback against real movie media;
5. final automated and human media inspection;
6. interruption and resume behavior on real media;
7. the approximately ≤2 GB additional AI-workload RAM target;
8. a controlled short real-media run;
9. a controlled medium real-media run;
10. one complete real 3–4 hour movie run;
11. final human QA.

Do not declare the core production goal complete until the full-length real-movie validation succeeds.

---

## LOCKED ARCHITECTURE

Do not:

- assume an AD SRT already exists;
- require a user-supplied AD SRT;
- replace AD transcription with unrelated subtitles;
- discard visual/action information from AD;
- redesign the architecture without a new recorded decision.

Locked path:

```text
AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT -> MOVIE INTELLIGENCE
```

---

## NEXT EXECUTION ORDER

```text
1. Complete Issue #3 acceptance
2. Freeze the coordination architecture unless real use exposes a concrete defect
3. PC preflight
4. Tiny / short test
5. Medium real-media test
6. First full 3–4 hour movie
7. Human QA
8. Reliability fixes based on observed results
9. Measure throughput empirically
10. Process additional movies as system capacity allows
```

No fixed daily output target is required. No new architecture should be introduced during validation unless testing exposes a concrete defect that requires it.

---

## HANDOFF RULE

Future agents must read `AGENTS.md`, `Project_Control/AI_COLLABORATION_PROTOCOL.md`, and the current Project_Control and documentation status files before making significant changes or claiming completion.

Current `master` is the implementation source of truth. Locked decisions govern permitted architectural changes. Historical snapshots and old PRs provide context only and must not override current evidence.
