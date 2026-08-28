# ARK X Cinema — Project Status

**Last repository update:** 2026-08-28

## Status legend

- 🟢 Implemented / repository-tested
- 🟡 Needs real-environment or CI verification
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
| Ollama adapter | 🟢 | Local endpoint + structured JSON validation and failure handling |
| Intelligence pipeline | 🟢 | Evidence → Ollama → validated intelligence contract |
| Intelligence adapter | 🟢 | Resumable artifact boundary with explicit failure propagation |
| Script adapter | 🟢 | Evidence-grounded script boundary with explicit failure propagation |
| TTS adapter | 🟢 | Resumable audio boundary; actual engine still needs PC validation |
| Video adapter | 🟢 | Resumable final-video boundary; actual FFmpeg assembly still needs implementation/PC validation |
| QA adapter | 🟢 | Required-artifact checks and final-video inspection boundary; media inspector still needs real implementation/PC validation |
| Checkpoints | 🟢 | Atomic persistence with artifact SHA-256 verification |
| Stage state | 🟢 | Ordered pipeline state policy with per-stage checkpoints |
| Resumable execution | 🟢 | Safe skip, failure recording, retry, and artifact validation |
| Orchestrator adapter | 🟢 | Thin integration boundary; existing production orchestrator remains unchanged |
| GitHub CI | 🟡 | Prior Actions run 33139700610 failed; a fresh run on the corrected tree must pass before this is called green |
| Real Ollama/Qwen test | 🟡 | Requires Windows PC |
| Real whisper.cpp test | 🟡 | Requires Windows PC |
| Real TTS test | 🟡 | Requires Windows PC |
| Real FFmpeg render | 🟡 | Requires Windows PC and production assembly command |
| First real movie | 🟡 | Deliberately not started |

## Verification rule

Architecture-only implementation is not production validation. Real dependencies, RAM, movie inputs, rendering, and end-to-end behavior must be tested on the Windows machine before production use.

GitHub CI is considered green only when an actual Actions run on the current code completes successfully. The previously verified run `33139700610` failed, so it must not be described as green.

## Current integration boundary

The adapter layer bridges existing stage implementations into resumable execution without replacing the production orchestrator. Adapters currently cover ingestion, AD transcription, timeline, intelligence, script, TTS, video, and QA boundaries.

The canonical timeline consumes timed subtitle cues and the generated AD SRT, preserving source labels and timestamps for the evidence-first intelligence stage.

## Immediate next step

Run and verify GitHub CI on the corrected integration tree. If CI passes, lock that commit as the GitHub baseline. Do not begin the first real movie until the Windows machine validates Whisper.cpp, Ollama/Qwen, TTS, FFmpeg, RAM behavior, and the end-to-end pipeline.

## Deferred GitHub issue

Issue #1 tracks the CI regression. Do not close it until a successful real CI run has been verified.
