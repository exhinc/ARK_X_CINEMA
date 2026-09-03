# ARK X Cinema — Project Status

**Last repository update:** 2026-09-03

## Status legend
- 🟢 Implemented / repository-tested
- 🟡 Needs real-environment validation
- 🔵 Next
- 🔴 Known defect

## Active execution architecture decision

The broader runtime/execution strategy is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`. It governs local-first execution, optional accelerator/cloud experiments, replaceable LLM backends, long-movie persistence, FFmpeg usage, benchmark-first decisions, and monetization-oriented editing policy.

This decision record does not constitute Windows runtime validation or production-readiness evidence.

## Current state

| Area | Status | Notes |
|---|---|---|
| Runtime/config | 🟢 | Repository-relative configuration and one-heavy-stage policy |
| Movie workspace | 🟢 | Deterministic per-movie workspace and source manifest |
| Subtitle + AD ingestion | 🟢 | AD remains separate audio; conversion to SRT is required |
| AD transcription boundary | 🟢 | Whisper.cpp adapter for AD audio -> timestamped SRT; real execution still needs PC validation |
| Scene/timeline engine | 🟢 | Deterministic cue-based timeline preserving subtitle/AD provenance |
| Evidence packets | 🟢 | Bounded, provenance-preserving intelligence input |
| Ollama adapter | 🟢 | Local endpoint + strict structured-output validation |
| Intelligence pipeline | 🟢 | Evidence -> Ollama -> intelligence contract; real model execution still needs PC validation |
| Script adapter | 🟢 | Evidence-grounded original recap script generation contract |
| TTS engine + adapter | 🟢 | Piper engine with segment timing metadata; real runtime still needs PC validation |
| Edit mapping | 🟢 | Deterministic script-to-source edit manifest with clip-length safeguards |
| Recap subtitles | 🟢 | Deterministic narration-aligned recap SRT |
| Video adapter + renderer | 🟢 | Deterministic FFmpeg assembly contract; real encoding still needs PC validation |
| QA adapter + inspector | 🟢 | Required-artifact and media-stream validation; real media still needs PC validation |
| Checkpoints | 🟢 | Atomic persistence with artifact integrity verification |
| Stage state | 🟢 | Ordered pipeline state with prerequisite enforcement |
| Resumable execution | 🟢 | Safe skip, failure recording, retry, and artifact validation |
| Stage-A runner | 🟢 | Complete repository-side composition from ingestion through QA |
| GitHub CI | 🟢 | Current documentation baseline was updated after the Stage-A merge; current-commit CI must be checked before using CI as fresh validation evidence |
| Real Ollama/Qwen test | 🟡 | Requires Windows PC |
| Real whisper.cpp test | 🟡 | Requires Windows PC |
| Real TTS test | 🟡 | Requires Windows PC |
| Real FFmpeg render | 🟡 | Requires Windows PC and real media |
| Full end-to-end movie | 🟡 | Requires controlled tiny -> medium -> full validation |

## Verification rule

Architecture-only implementation is not real-machine validation. Real dependencies, RAM, movie inputs, rendering, and end-to-end behavior must be tested on the Windows machine before production use.

## Current integration boundary

The canonical Stage-A path is composed by `Engine/stage_a_runner.py` and uses the existing stage adapters plus the existing checkpoint/state system. The conservative `Engine/orchestrator.py` remains preserved as the foundation entrypoint.

The locked AD path remains:

```text
AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT -> MOVIE INTELLIGENCE
```

## Long-movie policy

Long-movie safeguards and test sequencing are recorded in `Project_Control/LONG_MOVIE_READINESS.md`, while the broader runtime strategy is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`. The design requires movie-scoped artifacts, bounded evidence, explicit stage checkpoints, artifact validation, disk-space preflight, controlled cleanup, and tiny -> medium -> full validation.

## Multi-agent coordination

Shared instructions are in `AGENTS.md`; Claude's entry point is `CLAUDE.md`; the persistent cross-agent handoff is `docs/AI_HANDOFF.md`. Current code and current verified CI evidence override stale historical claims. Agents must also consult the active execution architecture decision before proposing changes in its covered areas.

## Immediate next step

Finish the GitHub-only gate with fresh CI for the current documentation baseline and obtain the required consensus/acceptance in Issue #3. Then freeze architecture and move to controlled Windows runtime validation.

## Resolved issue

Issue #1 (historical CI regression) is closed after the corrected regression suite passed. PR #7 is merged into `master`; PR #6 is a historical superseded branch and is not part of the current production baseline.
