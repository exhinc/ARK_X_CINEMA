# ARK X Cinema — Claude Entry Point

Claude must read `AGENTS.md` first. It is the shared engineering contract for this repository.

Claude must then follow `Project_Control/AI_COLLABORATION_PROTOCOL.md` before significant changes.

Then read `docs/PROJECT_STATUS.md` and `docs/AI_HANDOFF.md`, and inspect the actual current code/tests relevant to the task.

The primary AI development team explicitly identified by the owner is ChatGPT, Claude, and Grok. Do not assume additional AI tools are part of the workflow.

GitHub `master`, current code, tests, and verified GitHub Actions results are authoritative. Never treat an old conversation or stale status statement as evidence.

Preserve the existing production orchestrator, deterministic timeline engine, stage-state/checkpoint system, legal-source constraints, evidence-first intelligence design, and low-RAM/$0 operating goals unless a change is explicitly justified and tested.

Never claim CI, runtime, RAM, Whisper.cpp, Ollama, TTS, FFmpeg, or end-to-end success without direct verification. Use the concrete Stage A–D milestones in `AGENTS.md`; do not use vague “production-ready” claims.

For multi-agent work, inspect recent changes before editing, avoid reverting another agent's work, and leave clear tests/documentation behind. Make the smallest safe change necessary.

@AGENTS.md
