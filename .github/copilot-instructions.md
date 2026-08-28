# ARK X Cinema — Repository Instructions

This repository contains ARK X Cinema, a $0/month, automation-first YouTube movie-recap system intended for a low-RAM Windows 11 laptop with final human QA.

**Read `AGENTS.md` before making changes.** It is the shared engineering contract and is intended to keep ChatGPT, Claude, Grok, Copilot, and other agents aligned.

## Required behavior
- Treat GitHub `master`, current source, tests, and verified GitHub Actions results as authoritative.
- Inspect the current API before changing callers; never rely on stale function names or previous chat context.
- Preserve the existing production orchestrator, deterministic timeline engine, and stage-state/checkpoint architecture unless a justified, tested change requires otherwise.
- Keep stages ordered and resumable. Do not bypass artifact SHA-256 verification or prerequisites.
- Propagate failures. Never mark a stage complete when its required artifact is missing, invalid, or unverified.
- Keep heavy AI work one stage at a time and preserve the approximately 2 GB additional-RAM target.
- Prefer free/local/open-source tooling. No piracy or DRM bypass.
- AD is separate audio and must be converted to timestamped SRT with whisper.cpp before canonical timeline/evidence processing.
- Intelligence is evidence-first: subtitle + AD SRT → timeline → bounded evidence packets → local LLM. Unsupported claims must remain explicitly unsupported/unknown.
- Recap narration must be original prose, not copied movie dialogue/subtitles.
- Use dependency injection for heavy/external engines where practical so CI can test orchestration without requiring local models/media.
- Add or update focused tests for code changes.
- Never claim CI or real-machine success without direct verification. Repository tests do not prove real Whisper.cpp/Ollama/TTS/FFmpeg/RAM/end-to-end behavior.

## Validation
After changes, verify the relevant tests and GitHub Actions run. Report exact outcomes. If CI fails, fix the failure before declaring the work complete.

For the complete cross-agent contract and current project rules, see `AGENTS.md` and `docs/PROJECT_STATUS.md`.
