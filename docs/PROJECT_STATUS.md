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
| Runtime/config | 🟢 | Repository foundation exists |
| Movie workspace | 🟢 | Workspace foundation exists |
| Subtitle + AD ingestion | 🟢 | AD remains separate audio; conversion to SRT is required |
| Scene/timeline | 🟢 | Canonical timeline foundation exists |
| Evidence packets | 🟢 | Bounded, provenance-preserving intelligence input |
| Ollama adapter | 🟢 | Structured JSON contract + failure handling |
| Intelligence pipeline | 🟢 | Evidence → Ollama → validated intelligence |
| Intelligence runner | 🟢 | Standalone stage runner; Whisper is upstream, not required here |
| Checkpoints | 🟢 | Atomic persistence with artifact SHA-256 verification |
| Stage state | 🟢 | Ordered pipeline state policy |
| Resumable execution | 🟢 | Safe skip, failure recording, and retry boundary |
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

`Engine/orchestrator_stage_adapter.py` bridges existing orchestrator stage functions into the resumable execution layer. The existing `Engine/orchestrator.py` has not been replaced or rewritten for this integration.

The ingestion adapter specifically preserves the existing `identify → ingest` call sequence while requiring the expected ingestion artifact for checkpoint completion.

## Next build

Extend the same adapter pattern to the next canonical stage only after its existing inputs/outputs and tests have been inspected. Do not bulk-wire every stage at once.
