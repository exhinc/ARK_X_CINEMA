# ARK X Cinema — Shared AI Agent Instructions

## Authority and team
GitHub `master` is the shared engineering source of truth. The primary AI collaborators are ChatGPT, Claude, and Grok. Do not assume another AI tool or agent is part of the workflow unless the owner explicitly adds it.

Before changing code, inspect the current repository, relevant tests, project status, and recent commits. Do not rely on historical chat claims when the repository can answer the question.

## Project objective
ARK X Cinema is a $0/month, highly automated YouTube movie-recap production system. The ultimate target is 3 distinct recap videos/day, with human final QA/approval. Movie/source files must be legally obtained; no piracy or DRM bypass.

## Core architecture
Canonical flow:

1. Legal movie/source files
2. Subtitle/transcript ingestion when available
3. Separate Audio Description (AD) audio ingestion
4. AD audio → timestamped SRT using whisper.cpp
5. Canonical scene/timeline construction from subtitle + AD evidence
6. Bounded evidence packets
7. Evidence-first movie intelligence
8. Original recap script
9. Local TTS narration
10. FFmpeg-based video assembly
11. Automated/deterministic media QA
12. Human QA/approval
13. Upload preparation

AD is a separate audio asset. It is not assumed to be embedded in the movie and is not assumed to already be an SRT.

## Intelligence rules
The LLM must receive bounded evidence packets, not an unconstrained movie and a request to infer its plot. Claims must be traceable to supplied evidence. Unsupported facts must be marked unknown/unsupported. Preserve provenance: scene ID, timestamps, source, dialogue, visual/action evidence, and evidence limits.

## Resource constraints
The design target is a low-RAM Windows 11 laptop with approximately 7.65 GB usable physical RAM. Target additional RAM for an AI workload is approximately ≤2 GB. One heavy AI stage at a time is the default policy. Do not assume a model is suitable because its download size is small; real runtime RAM must be measured on the PC.

Preferred/free-first candidates include whisper.cpp, Ollama with a small local model, Piper/Kokoro for TTS, and FFmpeg. Do not lock a candidate into production until it is validated on the actual machine.

## Stage/checkpoint rules
Stages must be ordered and resumable. Preserve existing checkpoint/hash/state infrastructure. A stage must not be marked complete unless its required artifact exists and passes integrity validation. Failures must propagate clearly. Resume behavior must not silently rerun completed expensive work.

Do not replace or rewrite the existing production orchestrator, deterministic timeline engine, or other established architecture merely to make a new adapter fit. Reconcile against the actual current interfaces first.

## Testing truthfulness
Passing unit/CI tests prove code contracts only. They do NOT prove real Whisper.cpp, Ollama, TTS, FFmpeg, RAM limits, or end-to-end movie processing.

Never claim the project is end-to-end validated until a real movie has successfully passed the pipeline on the target Windows machine and the resource constraints have been measured.

Use concrete validation milestones instead of vague “production-ready” claims:

- Stage A: 1 real finished video reliably
- Stage B: 1 video/day reliably
- Stage C: 2 videos/day reliably
- Stage D: 3 different movies/day reliably

## Verified vs unverified
Always distinguish:

VERIFIED IN REPOSITORY/CI:
- source architecture and code present
- automated test behavior that CI actually executed
- checkpoint/state behavior covered by tests

NOT VERIFIED UNTIL PC TESTING:
- actual whisper.cpp execution/performance
- actual Ollama/model inference/performance
- actual TTS engine performance/quality
- actual FFmpeg production rendering
- full 2–3 hour movie processing
- ≤2 GB additional AI RAM target
- end-to-end Stage A reliability

## Multi-agent coordination
Before modifying anything, inspect current `master` and recent commits. Prefer small, reviewable changes. Add/update tests with behavior changes. Record unresolved issues in GitHub issues or project documentation when appropriate. Never hide failures by weakening tests or deleting evidence of a regression.

When another agent has already changed a component, reconcile with its current code rather than recreating or overwriting it.

## Completion discipline
Do not add new architecture merely because a stage exists as an adapter. An adapter is not the same as a production implementation. The actual external/runtime integration must be explicitly verified before it is described as complete.

When reporting progress, give the repository-backed state, what was actually tested, what remains, and what must be tested on the Windows machine.
