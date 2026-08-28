# ARK X CINEMA — MULTI-AI STATUS

**Repository:** https://github.com/exhinc/ARK_X_CINEMA  
**Purpose:** Shared, evidence-based status document for all AI agents and the human operator.

**Rule:** No single AI may declare final truth. Claims move from “Open Disagreement” to “Agreed” only when participating assessments accept the cited repository evidence. Unresolved disagreements remain visible. The human is the final arbiter when AIs cannot reach consensus after evidence review.

**Last updated:** 2026-08-28

---

## 0. FORENSIC AUDIT DISTINCTION

The existing Phase 1 implementation/status audit is **historical evidence only**.

`Project_Control/IMPLEMENTATION_STATUS.md` records the scope and conclusions of the historical implementation audit and the establishment of the permanent forensic-audit protocol. It does **not** count as execution or completion of the new exhaustive forensic audit.

The current exhaustive forensic audit is a separate operation tracked in:

`Project_Control/AUDIT_LEDGER.md`

The ledger must be populated with fresh repository evidence for the current audit. Its existence, and the existence of prior audits, must never be used to claim that the current forensic audit has already been completed.

---

## 1. Agreed Facts

These points are supported by current repository evidence:

- Project-control system exists and is active.
- `AGENTS.md` is the authoritative AI engineering contract.
- `CLAUDE.md` is the Claude entry point and defers to `AGENTS.md`.
- `docs/AI_HANDOFF.md` exists and defines the persistent multi-agent handoff.
- `docs/PROJECT_STATUS.md` exists and records current architecture/status boundaries.
- Architecture decision DECISION-001 is locked: separate AD audio → whisper.cpp → timestamped AD SRT → movie intelligence.
- A historical full AD transcription test for *The Platform (2019)* AD audio (~135.8 MB) is recorded as successful.
- Current master contains repository-relative runtime configuration, canonical workspace/source-manifest support, subtitle/AD ingestion, deterministic timeline processing, bounded evidence packets, local Ollama integration, structured-output handling, recap-script core, and ordered/resumable checkpoint infrastructure.
- `Engine/orchestrator.py` remains the conservative foundation entrypoint.
- `Engine/stage_a_runner.py` currently composes the core path through script generation but does not yet complete TTS/video/final-QA production on master.
- The current master has a successful GitHub Actions run (#108) for commit `3138ebf8e9cc9394a9cb8dc552bcc486f30ac2b3`; the workflow runs `python -m pytest Engine/Tests -q` on Ubuntu/Python 3.11.
- CI success does not prove real Windows execution, model behavior, TTS, FFmpeg rendering, RAM limits, or full-movie reliability.
- Real Windows validation remains required before Stage A can be declared complete.

---

## 2. Historical / Open Disagreements

These older assessments remain visible as historical evidence and are not automatically current truth:

| Topic | Historical positions | Status |
|---|---|---|
| Overall percentage complete | Grok ~38%; second AI ~55–65% | Replaced by current evidence-based working estimate outside this historical record |
| Time to Stage A | Grok 2–4 focused weeks; second AI 1–3 focused weeks | Provisional until real runtime evidence exists |
| Time to 3/day | Grok 2.5–4 months; second AI 6–14 weeks | Provisional |
| Adapter vs production weighting | Lower vs higher weighting | Architectural distinction is agreed; numeric weighting remains contextual |

Do not use these historical estimates as evidence that current completion has been established.

---

## 3. Evidence Required for Production Claims

To resolve remaining production uncertainty, the repository/PC must establish:

1. A short real-media end-to-end run producing a valid final video and passing automated QA.
2. Real structured-output behavior from the production local model.
3. Measured peak RAM for Whisper.cpp, Ollama/model, and TTS on the target Windows machine.
4. Real FFmpeg rendering and output inspection.
5. Safe interrupted-run/resume behavior on real media.
6. A full first-movie run followed by human QA.

Until those exist, Stage-A production claims remain provisional.

---

## 4. Current Shared View of Remaining Work

### GitHub / engineering

- Complete the remaining Stage-A production implementations on `master`.
- Preserve one authoritative architecture and avoid unnecessary rewrites.
- Ensure stage outputs and interfaces remain compatible.
- Finish TTS, scene/edit mapping, FFmpeg assembly, final recap subtitles, deterministic media QA, and the complete end-to-end runner on master.
- Maintain CI and regression coverage.

### Windows / runtime

- Real whisper.cpp execution/performance and AD → SRT quality.
- Real Ollama/Qwen structured-output behavior and RAM.
- Real TTS generation/quality/RAM.
- Real FFmpeg rendering/media inspection.
- Real end-to-end short, medium, then full movie runs.
- Real interruption/resume testing.
- Final human quality judgment.

### Scaling

Only after Stage A is proven:

- 1 video/day
- 2 videos/day
- 3 different movies/day

---

## 5. Shared Target Pipeline

```text
LEGAL MOVIE PACKAGE
        │
        ▼
   INGESTION / SOURCE MANIFEST
        │
        ├──────────────┐
        ▼              ▼
   MOVIE SUBTITLES   AD AUDIO
                       │
                       ▼
                  whisper.cpp
                       │
                       ▼
                    AD SRT
        │              │
        └──────┬───────┘
               ▼
      CANONICAL TIMELINE
               │
               ▼
       BOUNDED EVIDENCE
               │
               ▼
       LOCAL LLM INTELLIGENCE
               │
               ▼
       ORIGINAL RECAP SCRIPT
               │
               ▼
           LOCAL TTS
               │
               ▼
       SCRIPT / SCENE MAPPING
               │
               ▼
           FFmpeg
               │
               ▼
        AUTOMATED QA
               │
               ▼
          HUMAN QA
```

Underlying the stages: checkpointing, artifact integrity, resumability, provenance, and one-heavy-AI-stage-at-a-time policy.

---

## 6. Multi-Agent Rules

1. Read `AGENTS.md` and current Project_Control records before making status claims or changes.
2. Use current repository evidence, not old chat statements.
3. Keep disagreements visible until resolved.
4. Do not silently overwrite another agent's recorded position.
5. Treat historical audits as historical evidence.
6. Treat the current forensic audit ledger as the evidence record for the new audit.
7. Never use a percentage or time estimate as proof of production readiness.

---

## 7. Current Working Summary

- Current master is a substantial production-engineering foundation, not a finished end-to-end movie producer.
- The permanent forensic-audit protocol is established.
- The current exhaustive forensic audit is a separate operation and must be evidenced in `AUDIT_LEDGER.md`.
- CI is currently green for the latest master documentation commit, but CI is only repository-contract evidence.
- Real Windows validation remains outstanding.
