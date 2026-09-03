# ARK X CINEMA — Multi-Agent Handoff

> Read this file before modifying the repository. It is the persistent handoff for future AI collaborators.

## 1. Mission
ARK X Cinema is a $0/month, highly automated YouTube movie-recap production system. The ultimate target is 3 distinct recap videos/day, with final human QA/approval. Movies/source material must be legally obtained. No piracy, DRM bypass, or unauthorized acquisition workflows.

## 2. AI team and source of truth
The owner has explicitly identified ChatGPT, Claude, and Grok as the primary AI development team. Do not assume additional AI tools are part of the workflow unless the owner explicitly adds them.

GitHub `master` is the shared engineering source of truth. Current code, tests, and current GitHub Actions results outrank historical chat statements.

## 3. Mandatory collaboration protocol
The shared startup, authority, conflict-resolution, current-commit CI, and change-record rules are defined in `Project_Control/AI_COLLABORATION_PROTOCOL.md`.

Before significant changes, agents must follow that protocol rather than relying on conversation memory. Grok's dedicated entry point is `GROK.md`; Claude's entry point is `CLAUDE.md`; both ultimately inherit `AGENTS.md` and the shared collaboration protocol.

## 4. Active execution architecture decision
The broader runtime/execution strategy is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`. It governs local-first execution, optional accelerator/cloud experiments, replaceable LLM backends, long-movie persistence, FFmpeg usage, benchmark-first runtime decisions, and monetization-oriented editing policy.

Future agents must read that decision before proposing changes in those areas. It complements this handoff; it does not constitute PC runtime validation or production-readiness evidence.

## 5. Hard constraints
- $0/month software/API budget.
- Local/free/open-source first.
- Windows 11 low-RAM target: approximately 7.65 GB usable RAM.
- Target approximately ≤2 GB additional RAM for the active AI workload.
- One heavy AI stage at a time; release resources between heavy stages.
- Human final QA is mandatory.
- Do not silently replace or rewrite established production orchestration.

## 6. Authoritative pipeline
Legal movie/source files → movie workspace/ingestion → existing subtitles/transcript timing when available + separate AD audio → whisper.cpp converts AD audio to timestamped SRT → canonical timeline → bounded evidence packets → evidence-first local LLM intelligence → original recap script → local TTS → FFmpeg assembly → automated/deterministic media QA → human approval → upload preparation.

The AD asset is separate audio (typically MP3). It is not assumed to be embedded in the movie and is not assumed to already be an SRT.

## 7. Evidence-first intelligence
The LLM must receive bounded evidence packets rather than an unrestricted movie. Preserve scene ID, timestamps, source (`subtitle` vs `ad`), dialogue, visual/action evidence, and evidence limits. Every claim must be traceable to supplied evidence. Unsupported facts must remain unknown/unsupported.

## 8. What the repository establishes
The repository contains foundations/boundaries for runtime/config, movie workspace, subtitle + AD ingestion, AD transcription, canonical timeline, bounded evidence packets, intelligence, script, TTS, video assembly, QA, ordered/resumable stage state, atomic checkpoints, artifact SHA-256 verification, and thin adapters.

An adapter/boundary is not the same thing as a validated production engine. Do not claim real runtime validation merely because a mock/injected implementation passes CI.

## 9. Stage order and checkpoints
Stages are ordered:
1. ingestion
2. transcription
3. timeline
4. intelligence
5. script
6. tts
7. video
8. qa

Later stages require completed prerequisites. A stage is complete only when its required artifact succeeds and is checkpointed/verified according to the current implementation. Failed stages must propagate failure. Resume must safely skip only intact, verified completed work.

## 10. CI truth
Never call CI green without checking the GitHub Actions result for the current commit/tree. Historical runs are not current proof. Repository tests prove portable code contracts; they do not prove Windows runtime behavior.

## 11. Still unverified until Windows testing
- actual Whisper.cpp execution/performance and AD → SRT quality
- actual Ollama/Qwen runtime and structured-output behavior under resource limits
- actual TTS engine selection, quality, speed, and memory use
- actual FFmpeg production rendering and media inspection
- RAM target (≤2 GB additional AI workload)
- interrupted-run recovery on real media
- complete processing of a real 2–3 hour movie
- Stage A end-to-end reliability

## 12. Concrete milestones
Do not use vague “production-ready” status labels. Use:
- Stage A: 1 real finished video reliably
- Stage B: 1 real video/day reliably
- Stage C: 2 real videos/day reliably
- Stage D: 3 different movies/day reliably

## 13. Safe multi-agent modification procedure
Before editing: complete `Project_Control/AI_COLLABORATION_PROTOCOL.md`, fetch current `master`, read `AGENTS.md`, this file, `docs/PROJECT_STATUS.md`, current project-control records, inspect affected code/tests, check relevant recent commits, and verify CI for the current commit.

After editing: make the smallest safe change, add/update focused tests when behavior changes, verify current-commit CI, synchronize documentation, and record significant project changes in `Project_Control/CHANGELOG.md` and architectural changes in `Project_Control/DECISIONS.md`. Never weaken tests or erase useful history to make a result look successful. Never revert another agent's work based only on old chat context.

## 14. Copyright discipline
Generated recap narration must be original prose derived from structured intelligence. Do not build a workflow that reproduces movie subtitles/dialogue as the narration. Keep source evidence separate from generated narration.

## 15. Current status language
Use:
- 🟢 Implemented/repository-tested
- 🟡 Requires current-commit CI or real-environment verification
- 🔵 Next
- 🔴 Known defect

Current project state: **GitHub architecture substantially established; real-machine Stage A validation has not been completed.**
