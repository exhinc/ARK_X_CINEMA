# ARK X CINEMA — CURRENT TASK

**Last Updated:** 2026-09-03

---

## ACTIVE COLLABORATION PROTOCOL

All ChatGPT, Claude, and Grok work must follow `Project_Control/AI_COLLABORATION_PROTOCOL.md` before significant repository changes.

The protocol defines the mandatory startup sequence, architectural-governance vs implementation-truth boundaries, authority/conflict resolution, current-commit CI rule, safe modification procedure, and change-record requirements. It supplements the shared instructions in `AGENTS.md` and this task record.

---

## ACTIVE ARCHITECTURE DECISION

The active runtime/execution architecture decision is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`. Read that record before proposing changes to model runtime, cloud/accelerator execution, long-movie persistence, FFmpeg usage, or monetization-oriented editing policy.

It supplements this task record. The immediate gate remains PC validation; do not treat the decision record as evidence that runtime validation has been completed.

---

## CURRENT PHASE

**PHASE 2 — STAGE-A IMPLEMENTATION COMPLETE / PC VALIDATION GATE**

The GitHub-side Stage-A production composition is complete on `master`. The remaining work is controlled runtime validation on the target Windows machine, followed by reliability testing. Throughput optimization is secondary and is not a core completion gate.

---

## COMPLETED GITHUB WORK

### Build #1 — Runtime / Configuration Foundation
**PASS**

Repository-relative runtime configuration is wired into the active orchestration foundation. Machine-specific Whisper paths are no longer required in the active repository configuration contract.

### Build #2 — Canonical Workspace / Source Manifest
**PASS**

Per-movie workspace and deterministic source-manifest handling are implemented and tested.

### Build #3 — Evidence / Intelligence / Script Core
**PASS**

Bounded evidence packets, Ollama integration, strict structured-output parsing/validation, recap generation, and stage adapters are implemented and covered by portable tests.

### Build #4 — Permanent Forensic Audit Protocol
**PASS**

The permanent audit rules and `Project_Control/AUDIT_LEDGER.md` are established.

### Build #5 — Controlled Forensic Audit & Repair
**PASS**

The repository-wide controlled forensic audit was completed and recorded in the ledger. Confirmed documentation/control defects were repaired and the master tree was re-verified.

### Build #6 — Stage-A Downstream Production Integration
**PASS**

PR #7 was rebuilt from the current audited master and merged as `3fd4a87c2a68df98eff3652fbc65c4f2f972267e`.

Integrated on current master:

- Piper TTS engine + timing metadata
- deterministic script-to-scene edit manifest
- final recap SRT generation
- deterministic FFmpeg assembly
- deterministic FFprobe final-media QA
- complete Stage-A runner composition
- focused regression coverage

Post-merge GitHub Actions run #123 for the merge commit completed successfully.

### Build #7 — Multi-AI Coordination Hardening
**REPOSITORY IMPLEMENTED / ACCEPTANCE PENDING**

Implemented:

- mandatory shared collaboration protocol
- explicit architectural-governance vs implementation-truth distinction
- current-commit-only CI rule
- formal change-record rule
- dedicated Grok entry point
- Claude/shared-handoff convergence
- explicit quarantine of the historical root state snapshot

The formal acceptance point remains Issue #3, which still contains historical checklist/state text and requires reconciliation plus independent acceptance before closure.

### Build #8 — Core Production Completion Goal Correction
**IMPLEMENTED / CI-VERIFIED**

The project objective has been corrected so that the core completion criterion is reliable end-to-end processing of one real 3–4 hour movie on the target Windows PC, producing a finished recap that passes required QA.

A fixed daily movie quota is no longer a completion requirement. Throughput is measured and optimized only after reliable one-movie processing is established.

---

## CURRENT GATE

### GitHub implementation gate

**IMPLEMENTATION COMPLETE / CURRENT-MASTER CI VERIFIED**

The current master coordination-hardening tree was manually run through GitHub Actions at commit `98625c2b5aa6ddb9cdb53f1318449e4feb7b8679` and completed successfully. A Node.js deprecation warning was present but did not fail the workflow.

The remaining coordination acceptance event is the independent acceptance required by Issue #3.

### PC gate

**NOT YET COMPLETE**

Required evidence:

1. real whisper.cpp execution from the target PC
2. AD audio -> timestamped SRT quality and timing inspection
3. real Ollama/Qwen structured output and RAM measurement
4. real Piper TTS execution, audio quality, and RAM measurement
5. real FFmpeg rendering
6. automated + human inspection of the produced video
7. interrupted-run/resume test on real media
8. short real-media end-to-end run
9. medium real-media run
10. first full 3–4 hour movie run
11. final human QA

Do not call the core production goal complete until the full-length real-movie validation is passed.

---

## LOCKED ARCHITECTURE

Do NOT:

- assume an AD SRT already exists
- require a user-supplied AD SRT
- replace AD transcription with unrelated subtitles
- discard visual/action descriptions from AD
- redesign the architecture without a new recorded decision

Locked path:

```text
AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT -> MOVIE INTELLIGENCE
```

---

## NEXT EXECUTION ORDER

```text
1. Complete Issue #3 acceptance and close the GitHub-only coordination gate
2. Freeze coordination architecture unless real use exposes a concrete defect
3. PC preflight
4. Tiny test
5. Medium real-media test
6. First full 3–4 hour movie
7. Human QA
8. Reliability fixes only
9. Measure/optimize throughput empirically
10. Process additional movies as system capacity allows
```

No new architecture should be introduced during the runtime-validation gate unless testing exposes a concrete defect that requires it.

---

## HANDOFF RULE

Future agents must read `AGENTS.md`, `Project_Control/AI_COLLABORATION_PROTOCOL.md`, plus the current Project_Control and docs status files before changing architecture or claiming completion. Current master is the source of truth for implementation and verified current-commit evidence; locked decisions govern permitted architectural changes; old PR #6 and historical audit wording must not override current evidence.
