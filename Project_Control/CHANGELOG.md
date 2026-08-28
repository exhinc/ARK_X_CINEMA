# ARK X CINEMA — CHANGELOG

Significant project changes are recorded here so AI agents can reconstruct project history without relying on chat memory.

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
