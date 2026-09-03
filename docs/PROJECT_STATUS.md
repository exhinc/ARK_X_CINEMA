# ARK X Cinema — Project Status

**Last repository update:** 2026-09-03

## Status legend
- 🟢 Implemented / repository-tested
- 🟡 Needs current-commit or real-environment validation
- 🔵 Next
- 🔴 Known defect

## Active execution architecture decision

The broader runtime/execution strategy is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`. It governs local-first execution, optional accelerator/cloud experiments, replaceable LLM backends, long-movie persistence, FFmpeg usage, benchmark-first decisions, and monetization-oriented editing policy.

The core production-completion criterion is one reliable real 3–4 hour movie completed end-to-end on the target Windows PC with required automated and human QA. There is no fixed daily production quota.

This decision record does not constitute Windows runtime validation or production-readiness evidence.

## Active multi-AI coordination protocol

The mandatory shared coordination procedure is recorded in `Project_Control/AI_COLLABORATION_PROTOCOL.md`. It defines the agent startup sequence, architectural-governance rules, implementation-evidence hierarchy, current-commit CI verification, change-record requirements, and handoff procedure.

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
| GitHub CI | 🟢 | Current master commit `98625c2b5aa6ddb9cdb53f1318449e4feb7b8679` manually verified by successful GitHub Actions run #33721190514 |
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

Long-movie safeguards and test sequencing are recorded in `Project_Control/LONG_MOVIE_READINESS.md`, while the broader runtime strategy is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`. The design requires movie-scoped artifacts, bounded evidence, explicit stage checkpoints, artifact validation, disk-space preflight, controlled cleanup, and tiny -> medium -> full validation before the first full movie.

## Multi-agent coordination

Shared instructions are in `AGENTS.md`; Claude's entry point is `CLAUDE.md`; Grok's entry point is `GROK.md`; the persistent cross-agent handoff is `docs/AI_HANDOFF.md`; and the mandatory coordination procedure is `Project_Control/AI_COLLABORATION_PROTOCOL.md`.

The old `ARK_X_Cinema_Current_State.txt` is a dated historical audit snapshot and is not current project state.

## Immediate next step

Obtain the independent acceptance required by Issue #3, reconcile its stale historical body against current master evidence, and then close the GitHub-only coordination gate. After that, move to controlled Windows runtime validation for the one-movie completion criterion.

## Resolved issue

Issue #1 (historical CI regression) is closed after the corrected regression suite passed. PR #7 is merged into `master`; PR #6 is a historical superseded branch and is not part of the current production baseline.
