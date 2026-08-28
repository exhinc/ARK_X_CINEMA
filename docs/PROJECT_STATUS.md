# ARK X Cinema — Project Status

**Last repository update:** 2026-08-27

## Status legend

- 🟢 Implemented / documented
- 🟡 Needs verification
- 🔵 Next
- 🔴 Known defect

## Current state

| Area | Status | Notes |
|---|---|---|
| Runtime/config | 🟢 | Repository-relative configuration and strict single-heavy-stage policy |
| Movie workspace | 🟢 | Canonical isolated per-movie workspace foundation |
| Subtitle + AD ingestion | 🟢 | AD remains separate audio; conversion to SRT is required |
| AD transcription adapter | 🟢 | Resumable boundary around AD audio → whisper.cpp → SRT |
| Scene/timeline engine | 🟢 | Deterministic cue-based timeline preserving subtitle/AD provenance |
| Timeline adapter | 🟢 | Resumable timeline artifact boundary; existing timeline engine unchanged |
| Evidence packets | 🟢 | Bounded, provenance-preserving intelligence input |
| Ollama adapter | 🟢 | Structured JSON contract + failure handling |
| Intelligence pipeline | 🟢 | Evidence → Ollama → validated intelligence |
| Intelligence runner | 🟢 | Standalone intelligence-stage runner; Whisper is upstream |
| Checkpoints | 🟢 | Atomic persistence with artifact SHA-256 verification |
| Stage state | 🟢 | Ordered pipeline state policy with per-stage checkpoints |
| Resumable execution | 🟢 | Safe skip, failure recording, retry, and artifact validation |
| Orchestrator adapter | 🟢 | Thin integration boundary; existing orchestrator remains unchanged |
| Ingestion adapter tests | 🟢 | Existing identify→ingest flow verified through resumable boundary |
| GitHub CI | 🟡 | Workflow exists; latest result still needs verified run data |
| Real Ollama/Qwen test | 🟡 | Requires Windows PC |
| Real whisper.cpp test | 🟡 | Requires Windows PC |
| First real movie | 🟡 | Deliberately not started |
| TTS/video/QA production path | 🟡 | Requires later implementation and PC validation |

## Deferred GitHub issue

Issue #1 tracks the CI regression. Do not close until a successful real CI run has been verified.

## Current development rule

Do not treat architecture-only implementation as production validation. Real dependencies, RAM, movie inputs, and rendering must be tested on the Windows machine before production use.

## Current integration boundary

The adapter layer bridges existing stage implementations into resumable execution without replacing the production orchestrator. Current adapters cover ingestion, AD transcription, and canonical timeline generation.

The canonical timeline consumes timed subtitle cues and the generated AD SRT, preserving source labels and timestamps for the evidence-first intelligence stage.

## Next build

Integrate the **intelligence stage** through the same resumable boundary. The integration must write a verified intelligence artifact, preserve partial-failure information, and never invoke Ollama concurrently with another heavy AI stage.
