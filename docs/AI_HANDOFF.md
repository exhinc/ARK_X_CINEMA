# ARK X Cinema — AI Handoff

> **Read this file before modifying the repository.** This is the persistent project handoff for future AI assistants and collaborators.

## 1. Mission

ARK X Cinema is a $0/month, highly automated YouTube movie-recap production system. The target is **3 recap videos per day covering 3 different movies**, with final human QA/approval.

Movies/source material must be legally obtained. The system must not implement piracy, DRM bypass, or unauthorized acquisition.

The system is designed to run remotely from Jamaica using a Windows 11 laptop and free/open-source software wherever practical.

## 2. Hard constraints

- $0/month software/API budget.
- Local-first processing; no paid cloud AI, transcription, TTS, or editing services.
- Low-RAM hardware is a primary design constraint. Target approximately **<=2 GB additional RAM for the AI workload** and never assume a model fits based only on download size.
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
Local Ollama model (configured Qwen3 1.7B candidate)
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

Each packet should preserve provenance such as:

- scene ID
- exact start/end timestamps
- source (`subtitle` or `ad`)
- dialogue
- visual/action description
- evidence limits

Every generated claim must be traceable to supplied evidence. Unsupported facts must be marked unknown rather than invented.

## 5. Current implementation

Implemented on `master`:

- runtime/config foundation
- movie workspace foundation
- subtitle + AD ingestion foundation
- scene/timeline foundation
- movie intelligence evidence-packet foundation
- Ollama intelligence adapter
- evidence → Ollama intelligence pipeline
- standalone intelligence-stage runner
- atomic checkpoint primitive
- ordered/resumable stage-state policy
- CI workflow with manual dispatch

The intelligence stage is deliberately decoupled from Whisper. Whisper is an upstream dependency; intelligence should be testable independently when given a valid canonical timeline.

## 6. Stage order

The stage-state policy currently defines:

1. ingestion
2. transcription
3. timeline
4. intelligence
5. script
6. tts
7. video
8. qa

A later stage must not run before its prerequisite stage is complete.

## 7. Checkpointing

`Engine/checkpoint.py` provides atomic JSON checkpoint persistence.

`Engine/stage_state.py` provides ordered stage-state policy.

Checkpoint states are `running`, `complete`, or `failed`, with schema versioning and optional artifact/error information.

Do not mark a stage complete unless its required work and artifact have actually succeeded.

## 8. CI / known issue

GitHub Actions workflow: `.github/workflows/tests.yml`.

A CI regression was observed because legacy/local experimental tests attempted to use Windows-only paths and optional local dependencies such as Whisper/Ollama. Those tests were classified as local/manual checkpoints rather than portable CI tests.

**Issue #1 is the deferred CI investigation record.** Do not close it until an actual successful regression run has been verified.

GitHub issue: https://github.com/exhinc/ARK_X_CINEMA/issues/1

Important: a green CI suite does not replace real Windows hardware validation. The real machine must still be tested with Ollama, Qwen3, whisper.cpp, actual movie/AD inputs, RAM measurement, and FFmpeg.

## 9. PC-only validation still required

The following cannot be honestly marked production-ready until tested on the user's Windows 11 laptop:

- Ollama installation/connectivity
- configured Qwen3 1.7B model availability
- actual LLM structured output
- RAM usage under the <=2 GB AI-workload target
- whisper.cpp executable/model configuration
- real AD MP3 → timestamped SRT
- real movie + subtitle/AD timeline creation
- real first-movie end-to-end run
- TTS runtime/resource behavior
- FFmpeg rendering/resource behavior
- resume behavior after an interrupted real run
- final QA workflow

Do not fabricate these results.

## 10. Safe modification rules

Before modifying code:

1. Fetch the current `master` version of every affected file.
2. Check the current commit SHA.
3. Understand existing behavior and tests.
4. Prefer additive changes.
5. Never replace an orchestrator wholesale unless the existing behavior has been fully reconciled and preserved.
6. Add or update focused tests for every behavioral change.
7. Keep PC-only dependencies out of portable unit tests.
8. Keep heavy AI stages isolated.
9. Preserve artifact provenance and timestamps.
10. Record significant defects as GitHub Issues rather than relying only on chat history.

## 11. Current next priorities

### Immediate GitHub work

- Finish the safe orchestration wrapper around checkpoint/stage-state primitives.
- Add tests proving resumability, idempotence, failure recovery, and artifact integrity.
- Audit the current repository for accidental overrides/regressions.
- Improve CI separation between portable tests and local/manual tests.
- Keep documentation synchronized with architectural changes.

### Later on Windows PC

- Execute controlled Ollama smoke test.
- Measure actual RAM usage.
- Validate whisper.cpp and AD transcription.
- Process the first real, legally obtained movie.
- Measure each stage before enabling automation at scale.

## 12. Scaling target

Do not jump directly to 3 movies/day.

```text
Stage A: 1 finished video reliably
Stage B: 1 video/day reliably
Stage C: 2 videos/day reliably
Stage D: 3 different movies/day reliably
```

Reliability comes before throughput.

## 13. What future AI must NOT assume

- Do not assume AD is already an SRT.
- Do not assume movie subtitles contain visual descriptions.
- Do not assume Ollama is installed or running in GitHub CI.
- Do not assume the Qwen model fits the laptop's RAM without measurement.
- Do not assume a successful unit test means the real movie pipeline works.
- Do not assume a file's existence means its stage completed successfully.
- Do not delete or overwrite existing functionality without first inspecting it.
- Do not mark deferred PC validation as complete.

## 14. Source of truth hierarchy

When information conflicts, use this order:

1. Current code on `master`
2. Current tests and CI configuration
3. This `AI_HANDOFF.md`
4. GitHub Issues for known unresolved defects
5. Git history/commit messages
6. Older chat messages

If this document becomes stale, update it as part of the repository change that makes it stale.

## 15. Current status

**Overall:** active development; not production-ready.

**GitHub architecture:** substantially established.

**Real-machine integration:** pending.

**CI regression issue:** documented as Issue #1 and must remain visible until resolved.

**Next safe build:** checkpoint-aware orchestration wrapper + tests.
