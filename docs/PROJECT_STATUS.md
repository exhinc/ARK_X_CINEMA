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
| Checkpoints | 🟢 | Atomic JSON persistence |
| Stage state | 🟢 | Ordered pipeline state policy |
| Checkpoint-aware orchestration | 🔵 | Next GitHub build |
| GitHub CI | 🟡 | Workflow exists; regression investigation remains open |
| Real Ollama/Qwen test | 🟡 | Requires Windows PC |
| Real whisper.cpp test | 🟡 | Requires Windows PC |
| First real movie | 🟡 | Deliberately not started |
| TTS/video/QA production path | 🟡 | Requires later implementation and PC validation |

## Deferred GitHub issue

Issue #1 tracks the CI regression. Do not close until a successful real CI run has been verified.

## Current development rule

Do not treat architecture-only implementation as production validation. Real dependencies, RAM, movie inputs, and rendering must be tested on the Windows machine before production use.

## Next build

Implement a checkpoint-aware orchestration wrapper without replacing the existing orchestrator. Add tests for ordering, idempotence, resume, failure recovery, and artifact integrity.
