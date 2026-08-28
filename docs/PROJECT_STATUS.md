# ARK X Cinema — Project Status

**Last repository update:** 2026-08-28

## Status legend
- 🟢 Implemented / repository-tested
- 🟡 Needs real-environment or current-commit CI verification
- 🔵 Next
- 🔴 Known defect

## Current state

| Area | Status | Notes |
|---|---|---|
| Runtime/config | 🟢 | Repository-relative configuration and stage-policy foundation |
| Movie workspace | 🟢 | Isolated per-movie workspace foundation |
| Subtitle + AD ingestion | 🟢 | AD remains separate audio; conversion to SRT is required |
| AD transcription boundary | 🟢 | Resumable adapter for AD audio → whisper.cpp → timestamped SRT; real whisper.cpp still needs PC validation |
| Scene/timeline engine | 🟢 | Deterministic cue-based timeline preserving subtitle/AD provenance |
| Timeline adapter | 🟢 | Resumable timeline artifact boundary; existing timeline engine unchanged |
| Evidence packets | 🟢 | Bounded, provenance-preserving intelligence input |
| Ollama adapter | 🟢 | Local endpoint + structured JSON validation/failure handling foundation |
| Intelligence pipeline | 🟢 | Evidence → Ollama → intelligence contract; real model execution still needs PC validation |
| Intelligence adapter | 🟢 | Resumable artifact boundary with explicit failure propagation |
| Script adapter | 🟢 | Evidence-grounded original-script boundary with explicit failure propagation |
| TTS adapter | 🟢 | Resumable audio boundary; actual engine/runtime still needs PC validation |
| Video adapter | 🟢 | Resumable final-video boundary; production FFmpeg assembly still needs implementation/PC validation |
| QA adapter | 🟢 | Required-artifact checks and final-video inspection boundary; real media inspector still needs implementation/PC validation |
| Checkpoints | 🟢 | Atomic persistence with artifact SHA-256 verification |
| Stage state | 🟢 | Ordered pipeline state policy with per-stage checkpoints |
| Resumable execution | 🟢 | Safe skip, failure recording, retry, and artifact validation |
| Orchestrator adapter | 🟢 | Thin integration boundary; existing production orchestrator remains unchanged |
| GitHub CI | 🟢* | Corrected test run `33140883220` completed successfully; verify again after future code changes |
| Real Ollama/Qwen test | 🟡 | Requires Windows PC |
| Real whisper.cpp test | 🟡 | Requires Windows PC |
| Real TTS test | 🟡 | Requires Windows PC |
| Real FFmpeg render | 🟡 | Requires Windows PC and production assembly command |
| First real movie | 🟡 | Deliberately not started |

\* The green CI result proves the repository test suite for that verified run. It does not prove real Windows runtime behavior.

## Verification rule

Architecture-only implementation is not production validation. Real dependencies, RAM, movie inputs, rendering, and end-to-end behavior must be tested on the Windows machine before production use.

GitHub CI is considered green only when an actual Actions run on the relevant current code completes successfully. Run `33140883220` was verified successful after the integration fixes. Documentation-only commits after that run do not change runtime behavior; the next code change must receive its own CI verification.

## Current integration boundary

The adapter layer bridges existing stage implementations into resumable execution without replacing the production orchestrator. Adapters currently cover ingestion, AD transcription, timeline, intelligence, script, TTS, video, and QA boundaries.

The canonical timeline consumes timed subtitle cues and the generated AD SRT, preserving source labels and timestamps for the evidence-first intelligence stage.

## Multi-agent coordination

The repository contains shared AI-agent instructions in `AGENTS.md`, a Claude entry point in `CLAUDE.md`, repository-wide Copilot instructions in `.github/copilot-instructions.md`, and the persistent multi-agent handoff in `docs/AI_HANDOFF.md`.

All agents must treat current code, tests, and verified CI as authoritative and must not claim real-machine validation without evidence.

## Immediate next step

Freeze the GitHub architecture baseline. When the Windows machine is available, validate Whisper.cpp, Ollama/Qwen, TTS, FFmpeg, RAM behavior, and the full pipeline one heavy stage at a time. Do not begin the first production movie until those checks pass.

## Resolved issue

Issue #1 (CI regression) is closed after the corrected regression suite run `33140883220` completed successfully. Future regressions should be recorded as new issues rather than reopening historical context without a new failure.
