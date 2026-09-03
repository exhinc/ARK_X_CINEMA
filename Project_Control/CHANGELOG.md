# ARK X CINEMA — CHANGELOG

Significant project changes are recorded here so AI agents can reconstruct project history without relying on chat memory.

---

## 2026-09-03 — Multi-AI collaboration protocol hardening

- Added `Project_Control/AI_COLLABORATION_PROTOCOL.md` as the mandatory shared procedure for ChatGPT, Claude, Grok, and future owner-authorized AI agents.
- Added `GROK.md` as a dedicated Grok entry point into the shared repository rules.
- Hardened `AGENTS.md` to require the shared collaboration protocol before significant changes.
- Wired the protocol into `CLAUDE.md` and `docs/AI_HANDOFF.md` so dedicated agent entry points converge on the same rules.
- Wired the protocol into `Project_Control/CURRENT_TASK.md` and the existing active architecture/status documentation chain.
- Added explicit conflict-resolution authority: current master/verified artifacts > current-commit CI/test evidence > active architecture decisions > current project status/handoff records > individual AI recommendations > old chat history.
- Established a current-commit-only CI verification rule for claims of CI status.
- Formalized significant-change recording through Git commits, this changelog, and `DECISIONS.md` for architectural decisions.
- Added `DECISION-004` to `Project_Control/DECISIONS.md` to lock the collaboration authority/handoff rules.

This hardening changes coordination/documentation only. It does not replace the production architecture or alter PC runtime validation requirements.

---

## 2026-08-28 — Permanent forensic audit protocol upgrade

- Expanded `AGENTS.md` with a repository-wide forensic audit protocol.
- Added `Project_Control/AUDIT_LEDGER.md` for formal repository coverage and uncertainty tracking.
- Updated `CURRENT_TASK.md` to require the audit ledger during future full audits.
- Reconciled `IMPLEMENTATION_STATUS.md` with the current modular master implementation and clearly separated repository verification from PC-only runtime validation.
- Preserved existing ARK X Cinema architecture constraints, multi-agent rules, evidence-first intelligence rules, checkpoint/state requirements, low-RAM policy, and legal-source constraints.

The new permanent repair sequence is:

`AUDIT → DISCOVER → ROOT-CAUSE ANALYSIS → FIX → TEST → RE-SCAN → CROSS-FILE REGRESSION AUDIT → TEST AGAIN → FINAL VERIFICATION`

---

## 2026-08-28 — Stage-A core engineering baseline

- Runtime/configuration foundation integrated into the active engine.
- Canonical per-movie workspace/source-manifest implementation established.
- Evidence packet and structured-output pipeline established.
- Recap script engine and script-stage boundary established.
- Resumable stage/checkpoint infrastructure established.

Real TTS, FFmpeg production rendering, final narration subtitles, full end-to-end execution, and PC runtime/performance validation remain explicit later gates unless proven by current master evidence.

---

## 2026-08-27 — Architecture and agent-control consolidation

- Locked AD architecture: separate AD audio → whisper.cpp → timestamped AD SRT.
- Established Project_Control source-of-truth records.
- Established multi-agent coordination rules.
- Established runtime/configuration foundation.

Historical patch scripts and backups are retained as development evidence and are not the primary production modification mechanism.
