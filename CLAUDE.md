# ARK X Cinema — Claude Entry Point

Claude: read `AGENTS.md` first. It is the shared engineering contract for the AI agents working on this repository.

Then read `docs/PROJECT_STATUS.md` and `docs/AI_HANDOFF.md`, and inspect the actual current code/tests relevant to your task.

The primary AI development team is ChatGPT, Claude, and Grok. GitHub `master`, current code, tests, and verified GitHub Actions results are authoritative.

Do not assume a previous conversation, commit, API name, or status report is current. Inspect the current repository before making changes.

Preserve the existing production orchestrator, deterministic timeline engine, stage-state/checkpoint system, legal-source constraints, evidence-first intelligence design, and low-RAM/$0 operating goals unless a change is explicitly justified and tested.

Never claim CI, runtime, RAM, Whisper.cpp, Ollama, TTS, FFmpeg, or end-to-end success without direct verification. Use the shared stage/checkpoint architecture and propagate failures rather than silently converting them into success.

Repository tests prove portable code contracts; they do not prove real Windows runtime behavior. Use the concrete scaling milestones in `AGENTS.md` rather than the vague label “production-ready.”

For multi-agent work, inspect recent changes before editing and leave clear tests/documentation behind. Make the smallest safe change necessary.

@AGENTS.md
