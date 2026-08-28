# ARK X Cinema — Build History

This is the durable high-level development record. Git commits remain the authoritative code history.

## Build 1 — Foundation

Established repository/runtime configuration and project structure.

## Build 2 — Movie ingestion foundation

Established movie workspace and source/subtitle/AD ingestion direction.

## Build 3 — Timeline foundation

Established canonical timeline/scene processing direction.

## Build 4 — AD transcription / timeline integration

Established the rule that separate AD audio is converted to timestamped SRT using whisper.cpp before it becomes timeline evidence.

## Build 5 — Movie Intelligence Engine

Added evidence-first intelligence architecture. Bounded evidence packets preserve scene IDs, timestamps, source provenance, dialogue, visual/action descriptions, and evidence limits. Intelligence output requires confidence and unsupported-claim handling.

## Build 6 — Ollama intelligence integration

Added an optional Ollama adapter, structured JSON validation, evidence-to-intelligence pipeline, and standalone intelligence-stage runner. The stage is intentionally decoupled from Whisper because transcription is upstream.

## Build 7 — Checkpoint / stage-state foundation

Added atomic checkpoint persistence and ordered stage-state policy. Stages are explicitly ordered and failures are recorded for later resume/debugging.

## Documentation layer

Added persistent AI handoff and project-status documents so future AI assistants can recover project context from GitHub instead of depending on chat history.

## Deferred validation

Real Windows execution remains pending for Ollama/Qwen3, whisper.cpp, RAM measurement, actual movie processing, TTS, FFmpeg, and end-to-end QA.

GitHub CI regression is tracked in Issue #1 and must not be silently forgotten.
