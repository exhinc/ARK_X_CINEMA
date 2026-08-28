# ARK X Cinema — Shared AI Agent Instructions

## 1. Purpose
ARK X Cinema is a $0/month, automation-first YouTube movie-recap production system. It is designed to run on a Windows 11 laptop with limited RAM and to automate as much of the workflow as practical while retaining final human QA/approval.

Movies/source files must be legally obtained. Do not add piracy, DRM bypass, or unauthorized acquisition workflows.

## 2. Source of truth
GitHub is the shared engineering source of truth. The repository is private and the default branch is `master`.

Before changing architecture, inspect the current files on `master`. Do not rely on old chat messages, stale documentation, or assumptions about function names/APIs.

The authoritative current status is `docs/PROJECT_STATUS.md` plus the actual code and current GitHub Actions results. If documentation conflicts with code or CI, investigate and reconcile it; do not silently assume.

## 3. Hardware and operating constraints
- Target runtime: Windows 11 laptop.
- Approximately 7.65 GB usable physical RAM.
- Production goal: no more than about 2 GB additional RAM for the active AI workload.
- $0/month: prefer local/open-source/free software and models.
- One heavy AI stage at a time. Release resources before starting the next heavy AI stage.
- Real hardware performance is not proven by repository tests. Whisper.cpp, Ollama/Qwen, TTS, FFmpeg rendering, RAM usage, and end-to-end processing require Windows-machine validation.

## 4. Canonical movie pipeline
Legal movie/source files
→ subtitle + separate AD audio ingestion
→ AD audio converted to timestamped SRT using whisper.cpp
→ canonical scene/timeline with subtitle and AD provenance
→ bounded evidence packets
→ evidence-first local LLM intelligence
→ original recap script
→ local TTS
→ FFmpeg video assembly
→ deterministic/media QA
→ human approval

The AD track is separate audio. It is NOT assumed to be an existing SRT. The AD audio may contain visual/action descriptions and spoken movie/dialogue information. The pipeline must convert it to timestamped SRT before the canonical timeline uses it.

## 5. Evidence-first intelligence rule
Never give a small local LLM an unrestricted movie and ask it to invent the plot.

Use:
Movie subtitles + AD SRT → canonical timeline → bounded evidence packets → LLM.

Claims must be traceable to supplied evidence. Unsupported facts must remain unknown or be explicitly listed as unsupported. Preserve scene IDs, timestamps, and source labels (`subtitle` vs `ad`) through the evidence pipeline.

## 6. Stage/checkpoint rules
The project uses ordered, resumable stages with artifact checkpoints and SHA-256 verification. Do not bypass stage prerequisites, checkpoint validation, or artifact integrity checks.

A stage must not be considered complete merely because a function returned. Its required artifact must exist, be valid, and be checkpointed according to the current stage-state implementation.

Failed stages must propagate failure to their callers. Do not read a supposedly completed artifact after a failed stage and accidentally convert failure into success.

Resume behavior must be safe: an intact, verified completed artifact may be skipped; missing, modified, or invalid artifacts must not be trusted.

## 7. Existing architecture protection
Do NOT replace or rewrite the existing production orchestrator, deterministic timeline engine, or stage-state implementation merely to simplify a new feature.

The adapter layer exists to bridge existing implementations into resumable execution. Prefer thin adapters and dependency injection for external/heavy engines so CI can test orchestration without requiring local models or a movie.

Before changing an existing public/internal API, search the repository for all callers and tests. Reconcile the actual current API first.

## 8. Testing and CI rules
Never claim CI is green without verifying the actual GitHub Actions run for the current code/commit.

Repository tests prove code contracts and orchestration. They do NOT prove real Whisper.cpp, Ollama, TTS, FFmpeg, RAM behavior, or a complete movie run.

When changing code:
1. Inspect the current implementation.
2. Make the smallest safe change.
3. Update/add focused tests.
4. Run/verify GitHub Actions.
5. Report the exact result honestly.
6. If CI fails, diagnose and fix before declaring the change complete.

Do not report guessed test counts, guessed SHAs, or guessed runtime behavior.

## 9. Current validation boundary
The repository contains stage boundaries for ingestion, AD transcription, timeline, intelligence, script, TTS, video, and QA. Some boundaries intentionally inject the actual heavy/external implementation for CI testing.

Do not describe an injected boundary as a fully implemented production engine. Actual Whisper.cpp execution, Ollama/Qwen runtime, TTS engine selection/runtime, production FFmpeg assembly, real media inspection, RAM behavior, and end-to-end movie processing require Windows validation unless the current code and evidence prove otherwise.

Use concrete milestones instead of the vague label “production-ready”:
- Stage A: one real finished video processed reliably.
- Stage B: one real video/day reliably.
- Stage C: two real videos/day reliably.
- Stage D: three different movies/day reliably.

## 10. Script/copyright discipline
The recap script must be original prose generated from structured intelligence. Do not design a workflow that simply reproduces movie subtitles, dialogue, or copyrighted source text. Keep source evidence separate from generated narration.

## 11. Collaboration with the user's AI team
The primary AI development team is ChatGPT, Claude, and Grok. Other agents may participate if explicitly added later.

GitHub is the shared state. Before modifying anything:
- inspect the latest `master`;
- read `docs/PROJECT_STATUS.md` and `docs/AI_HANDOFF.md`;
- inspect relevant tests and current APIs;
- check recent commits/CI when relevant;
- avoid duplicating or reverting another agent's work.

After modifying anything:
- document what changed;
- add/update tests when appropriate;
- do not erase useful history or logs;
- leave the repository in a state another agent can understand.

If another agent's change appears wrong, do not silently overwrite it. Verify the problem, make the smallest corrective change, and document why.

## 12. Status honesty
Use these meanings:
- 🟢 Implemented / repository-tested
- 🟡 Needs real-environment or current-commit CI verification
- 🔵 Next
- 🔴 Known defect

Never upgrade 🟡 to 🟢 based only on an adapter/mock test.

## 13. Current next milestone
Do not start the first real movie until the current repository CI baseline is verified on the current tree and the Windows machine is available for real dependency validation.

The next PC validation sequence is:
Whisper.cpp → Ollama/Qwen → TTS → FFmpeg → RAM measurement → one real movie → full end-to-end QA.
