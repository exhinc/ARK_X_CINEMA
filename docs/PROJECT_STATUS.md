# ARK X Cinema — Project Status

**Last repository update:** 2026-09-03

## Status legend
- 🟢 Implemented / repository-tested
- 🟡 Needs Windows or current-commit validation
- 🔵 Next
- 🔴 Known defect

## Active execution architecture

The broader runtime/execution strategy is recorded in `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`.

**Core completion criterion:** one reliable real 3–4 hour movie completed end-to-end on the target Windows PC with the required automated and human QA. There is no fixed daily production quota.

The architecture record does not constitute Windows runtime validation.

## Active multi-AI coordination

The mandatory shared procedure is recorded in `Project_Control/AI_COLLABORATION_PROTOCOL.md`.

## Current state

| Area | Status | Notes |
|---|---|---|
| Runtime/config | 🟢 | Repository-relative configuration and one-heavy-stage policy |
| Movie workspace | 🟢 | Deterministic per-movie workspace and source manifest |
| Subtitle + AD ingestion | 🟢 | AD remains separate audio; conversion to SRT is required |
| AD transcription boundary | 🟢 | whisper.cpp adapter for AD audio -> timestamped SRT; real execution still needs Windows validation |
| Scene/timeline engine | 🟢 | Deterministic cue-based timeline preserving subtitle/AD provenance |
| Evidence packets | 🟢 | Bounded, provenance-preserving intelligence input |
| Ollama adapter | 🟢 | Local endpoint + strict structured-output validation |
| Intelligence pipeline | 🟢 | Evidence -> Ollama -> intelligence contract; real model execution still needs Windows validation |
| Script adapter | 🟢 | Evidence-grounded original recap script generation contract |
| TTS engine + adapter | 🟢 | Piper engine with segment timing metadata; real runtime still needs Windows validation |
| Edit mapping | 🟢 | Deterministic script-to-source edit manifest with clip-length safeguards |
| Recap subtitles | 🟢 | Deterministic narration-aligned recap SRT |
| Video adapter + renderer | 🟢 | Deterministic FFmpeg assembly contract; real encoding still needs Windows validation |
| QA adapter + inspector | 🟢 | Required-artifact and media-stream validation; real media still needs Windows validation |
| Checkpoints | 🟢 | Atomic persistence with artifact integrity verification |
| Stage state | 🟢 | Ordered pipeline state with prerequisite enforcement |
| Resumable execution | 🟢 | Safe skip, failure recording, retry, and artifact validation |
| Stage-A runner | 🟢 | Repository-side composition from ingestion through QA |
| GitHub CI | 🟢 | Current master commit has a successful applicable GitHub Actions run |
| Real Ollama/Qwen test | 🟡 | Requires Windows PC |
| Real whisper.cpp test | 🟡 | Requires Windows PC |
| Real TTS test | 🟡 | Requires Windows PC |
| Real FFmpeg render | 🟡 | Requires Windows PC and real media |
| Full end-to-end movie | 🟡 | Requires controlled short -> medium -> full validation |

## Verification rule

Repository implementation and CI are evidence of code behavior only. They do not prove the target Windows environment.

## Current integration boundary

The canonical Stage-A path is composed by `Engine/stage_a_runner.py` and uses the existing stage adapters plus the checkpoint/state system. The conservative `Engine/orchestrator.py` remains preserved as the foundation entrypoint.

The locked AD path remains:

```text
AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT -> MOVIE INTELLIGENCE
```

## Long-movie policy

Long-movie safeguards and validation sequencing are recorded in `Project_Control/LONG_MOVIE_READINESS.md`. The design requires movie-scoped artifacts, bounded evidence, explicit stage checkpoints, artifact validation, disk-space preflight, controlled cleanup, and short -> medium -> full validation.

## Multi-agent coordination

Shared instructions are in `AGENTS.md`; Claude's entry point is `CLAUDE.md`; Grok's entry point is `GROK.md`; the persistent cross-agent handoff is `docs/AI_HANDOFF.md`; and the mandatory coordination procedure is `Project_Control/AI_COLLABORATION_PROTOCOL.md`.

The old `ARK_X_Cinema_Current_State.txt` is a dated historical audit snapshot and is not current project state.

## Immediate next step

Complete the Issue #3 acceptance record: two independent AI reviews followed by human project-owner acceptance. Then freeze the coordination architecture and move to controlled Windows validation for the one-movie completion criterion.
