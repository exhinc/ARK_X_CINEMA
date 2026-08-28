# ARK X Cinema — Multi-Agent Handoff

> **Read this file before modifying the repository.** This is the persistent project handoff for future AI assistants and collaborators.

## 1. Mission
ARK X Cinema is a $0/month, highly automated YouTube movie-recap production system. The target is 3 recap videos per day covering 3 different movies, with final human QA/approval.

Movies/source material must be legally obtained. The system must not implement piracy, DRM bypass, or unauthorized acquisition.

The system is designed to run from Jamaica using a Windows 11 laptop and free/open-source software wherever practical.

## 2. Hard constraints
- $0/month software/API budget.
- Local-first processing; no paid cloud AI, transcription, TTS, or editing services.
- Low-RAM hardware is a primary design constraint. Target approximately <=2 GB additional RAM for the active AI workload. Never assume a model fits based only on download size.
- One heavy AI stage at a time. Release each heavy model from memory before starting the next heavy AI stage.
- Human final QA remains mandatory.
- Do not silently replace or rewrite existing production orchestration.
- Prefer small, testable, deterministic components with explicit contracts.

## 3. Authoritative pipeline

```text
Legal movie/source files
        |
        v
Movie workspace / ingestion
        |
        +--> Existing subtitles/transcript timing when available
        |
        +--> Separate AD audio (typically MP3)
                    |
                    v
               whisper.cpp
                    |
                    v
                  AD SRT
        |
        v
Canonical movie timeline
        |
        v
Bounded evidence packets
        |
        v
Local Ollama model (Qwen3 1.7B is a candidate/configured local model)
        |
        v
Validated movie intelligence
        |
        v
Original recap script
        |
        v
Local TTS
        |
        v
FFmpeg video assembly
        |
        v
QA / human approval
```

The AD track is separate audio and must be converted to timestamped SRT. It is not assumed to be an existing SRT.

## 4. Evidence-first intelligence rule
The LLM must not be asked to infer a movie's plot from the movie alone. Intelligence is generated from bounded evidence packets derived from the canonical timeline.

Each packet preserves provenance such as scene ID, exact start/end timestamps, source (`subtitle` or `ad`), dialogue, visual/action description, and evidence limits.

Every generated claim must be traceable to supplied evidence. Unsupported facts must be marked unknown/unsupported rather than invented.

## 5. Current implementation boundary
The repository currently contains stage/adaptor foundations for:

- runtime/config and movie workspace
- subtitle + separate AD ingestion
- AD transcription boundary (AD audio → whisper.cpp → timestamped SRT)
- deterministic canonical timeline
- bounded evidence packets
- Ollama/evidence-first intelligence
- original recap-script boundary
- TTS boundary
- final-video assembly boundary
- QA boundary
- ordered/resumable stage state
- atomic checkpoints with artifact SHA-256 verification
- thin orchestration adapters

Important: several of these are intentionally **boundaries**, not claims that the real production engine has been validated. In particular, actual Whisper.cpp execution, Ollama/Qwen runtime, TTS engine selection/runtime, production FFmpeg assembly, real media inspection, RAM behavior, and end-to-end movie processing still require Windows validation.

## 6. Stage order
The stage-state policy defines:

1. ingestion
2. transcription
3. timeline
4. intelligence
5. script
6. tts
7. video
8. qa

A later stage must not run before its prerequisite stage is complete.

## 7. Checkpointing and failure semantics
`Engine/checkpoint.py` provides atomic JSON checkpoint persistence.

`Engine/stage_state.py` provides ordered stage-state policy, artifact verification, resume/skip behavior, and failure recording.

A stage is complete only when its required work and artifact have actually succeeded and the artifact is checkpointed/verified according to the current implementation.

Failed stages must propagate failure to callers. Do not read a missing or invalid artifact after a failed stage and accidentally turn failure into success.

## 8. CI truth
GitHub Actions is the repository test authority for portable tests.

A previously inspected failing run (`33139700610`) must not be described as green. A later corrected run (`33140883220`) completed successfully; its job result was verified as success. Continue to verify CI against the current commit after meaningful changes. Never infer green status from an old run or from local/mock tests.

A green repository test suite does not replace real Windows hardware validation.

## 9. PC-only validation still required
The following remain unproven until tested on the Windows 11 laptop:

- Ollama installation/connectivity
- configured local Qwen model availability
- actual structured LLM output under resource constraints
- RAM usage against the <=2 GB AI-workload target
- whisper.cpp executable/model configuration
- real AD audio → timestamped SRT
- real movie + subtitle/AD timeline creation
- actual TTS engine/runtime behavior
- actual FFmpeg rendering command and resource behavior
- media inspection/QA against real output
- resume behavior after an interrupted real run
- first real legally obtained movie
- full end-to-end production run

Do not fabricate these results.

## 10. Safe modification rules
Before modifying code:
1. Fetch the current `master` version of every affected file.
2. Check the current commit/CI state when relevant.
3. Understand existing behavior and tests.
4. Prefer additive, minimal changes.
5. Never replace an orchestrator wholesale unless existing behavior has been fully reconciled and preserved.
6. Add/update focused tests for every behavioral change.
7. Keep PC-only dependencies out of portable unit tests.
8. Keep heavy AI stages isolated.
9. Preserve artifact provenance and timestamps.
10. Record significant defects as GitHub Issues rather than relying only on chat history.

## 11. Multi-agent coordination
Claude, Grok, ChatGPT, Copilot, and other agents may work on this repository. GitHub is the shared state.

Before editing, read `AGENTS.md`, this handoff, and `docs/PROJECT_STATUS.md`; inspect the current source/tests and recent changes relevant to the task.

Do not revert another agent's work merely because it differs from an older chat plan. Verify the current code and tests first. If a defect is found, make the smallest corrective change and document why.

After editing, leave tests and documentation synchronized with the change. Never claim an unverified runtime result.

## 12. Script/copyright discipline
The recap script must be original prose generated from structured intelligence. Do not design a workflow that simply reproduces movie subtitles or dialogue. Keep source evidence separate from generated narration.

## 13. Scaling target
Do not jump directly to 3 movies/day.

```text
Stage A: 1 finished video reliably
Stage B: 1 video/day reliably
Stage C: 2 videos/day reliably
Stage D: 3 different movies/day reliably
```

Reliability comes before throughput.

## 14. Source-of-truth hierarchy
When information conflicts, use this order:

1. Current code on `master`
2. Current tests and verified GitHub Actions results
3. `docs/PROJECT_STATUS.md`
4. `docs/AI_HANDOFF.md`
5. `AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md`
6. GitHub Issues and commit history
7. Older chat messages

If this document becomes stale, update it as part of the repository change that makes it stale.

## 15. Current status
**Overall:** active development; not production-ready.

**GitHub architecture:** substantially established and repository-tested.

**Real-machine integration:** pending.

**Immediate next milestone:** preserve the verified GitHub baseline, then validate the real Windows environment component-by-component before processing the first movie.
