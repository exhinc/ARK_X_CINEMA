# ARK X CINEMA — Multi-Agent Handoff

> Read this file before modifying the repository. It is the persistent handoff for future AI collaborators.

## 1. Mission

ARK X Cinema is a $0/month, highly automated YouTube movie-recap production system with final human QA and approval.

**Core project completion:** reliably process one real 3–4 hour movie end-to-end on the target Windows PC and produce a finished recap that passes the required automated and human QA.

There is no fixed daily movie quota. After core completion, throughput is measured and optimized from actual system performance.

Movies and source material must be legally obtained. No piracy, DRM bypass, or unauthorized acquisition workflows.

## 2. AI team and source of truth

The owner has identified ChatGPT, Claude, and Grok as the primary AI development team. Do not assume additional AI tools are part of the workflow unless the owner explicitly adds them.

GitHub `master` is the shared engineering source of truth. Current code, tests, and current GitHub Actions results outrank historical chat statements.

## 3. Mandatory collaboration protocol

The shared startup, authority, conflict-resolution, current-commit CI, and change-record rules are defined in `Project_Control/AI_COLLABORATION_PROTOCOL.md`.

Before significant changes, agents must follow that protocol instead of relying on conversation memory. `GROK.md` and `CLAUDE.md` are dedicated entry points; both ultimately follow `AGENTS.md` and the shared protocol.

## 4. Active execution architecture

The broader runtime/execution strategy is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`.

The locked production path is:

```text
Legal source -> ingestion -> subtitle/AD evidence -> whisper.cpp -> AD SRT
-> canonical timeline -> bounded evidence -> local intelligence -> recap script
-> local TTS -> FFmpeg assembly -> automated QA -> human QA
```

The AD asset is separate audio. It is not assumed to be embedded in the movie or to already exist as an SRT.

## 5. Hard constraints

- $0/month software/API budget.
- Local/free/open-source first.
- Windows 11 low-RAM target: approximately 7.65 GB usable RAM.
- Target approximately ≤2 GB additional RAM for the active AI workload.
- One heavy AI stage at a time; release resources between heavy stages.
- Human final QA is mandatory.
- Do not silently replace or rewrite established production orchestration.

## 6. Evidence-first intelligence

The LLM must receive bounded evidence packets rather than an unrestricted movie. Preserve scene IDs, timestamps, source provenance, dialogue, visual/action evidence, and evidence limits. Claims must be traceable to supplied evidence. Unsupported facts must remain unknown or unsupported.

## 7. Production stages and checkpoints

Stages are ordered:

1. ingestion
2. transcription
3. timeline
4. intelligence
5. script
6. TTS
7. video
8. QA

Later stages require completed prerequisites. A stage is complete only when its required artifact succeeds and is checkpointed and verified according to the current implementation. Failed stages must propagate failure. Resume may skip only intact, verified completed work.

## 8. CI truth

A CI result proves the commit/tree that was actually tested. Historical runs do not prove later commits. Repository tests prove portable code contracts; they do not prove Windows runtime behavior.

## 9. Windows validation still required

The following remain unverified until tested on the target Windows machine:

- actual whisper.cpp execution, performance, and AD-to-SRT quality;
- actual Ollama/Qwen runtime and structured-output behavior under resource limits;
- actual TTS execution, quality, speed, and memory use;
- actual FFmpeg production rendering and media inspection;
- the approximately ≤2 GB additional AI-workload RAM target;
- interruption and resume on real media;
- one complete real 3–4 hour movie run;
- final human editorial QA.

## 10. Completion and throughput

The core project is complete when one real 3–4 hour movie has passed the full pipeline reliably and the required QA has passed.

Throughput is a performance metric, not a completion requirement. Once core completion is proven, additional movies may be processed sequentially as hardware, storage, and processing time allow.

## 11. Safe multi-agent procedure

Before editing: read `AGENTS.md`, `Project_Control/AI_COLLABORATION_PROTOCOL.md`, the current Project_Control records, `docs/PROJECT_STATUS.md`, this file, and the affected code/tests. Check recent changes and the current CI result.

After editing: make the smallest safe change, add or update focused tests when behavior changes, synchronize affected documentation, and record significant changes in the changelog or decisions file as required. Never weaken tests, erase regression evidence, or revert another agent's work based only on old chat context.

## 12. Copyright discipline

Generated recap narration must be original prose derived from structured intelligence. Do not build a workflow that reproduces movie subtitles or dialogue as narration.

## 13. Current status language

Use:
- 🟢 Implemented/repository-tested
- 🟡 Requires Windows or current-commit verification
- 🔵 Next
- 🔴 Known defect

Current project state: **GitHub-side implementation and coordination controls are established; one full 3–4 hour movie has not yet been proven end-to-end on the target Windows PC.**
