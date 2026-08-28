# ARK X CINEMA — FORENSIC AUDIT LEDGER

**Audit type:** Controlled forensic audit & repair  
**Audit branch:** `master`  
**Audit baseline:** `b431fe1ac4036aec85fc3dc51f534a22e4fc4126`  
**Final audited master:** `e13366f82a8ef8f57eac632e1eeacdf14e37260e`  
**Audit started:** 2026-08-28  
**Audit status:** COMPLETE — controlled discovery, repair, re-scan, and final verification completed

**Purpose:** Evidence ledger for the new exhaustive forensic audit. Historical implementation/status audits are evidence only and do not count as execution of this audit.

## Status values

- `INSPECTED` — contents/behavior reviewed sufficiently for the audit scope.
- `PARTIALLY INSPECTED` — some relevant material reviewed, but meaningful coverage remains.
- `NOT APPLICABLE` — category does not apply, with reason recorded.
- `UNVERIFIED` — evidence is insufficient to establish the required fact.
- `BLOCKED` — inspection could not be completed because of an access/tool/environment limitation.

## Repository census

| Path / area | Status | Role / finding |
|---|---|---|
| `.github/` | INSPECTED | GitHub Actions configuration; portable Ubuntu/Python 3.11 test gate only. |
| `.gitignore` | INSPECTED | Protects source media/runtime outputs from Git; no destructive change justified. |
| `AGENTS.md` | INSPECTED | Authoritative AI engineering contract; forensic protocol integrated and preserved. |
| `CLAUDE.md` | INSPECTED | Claude entry-point; consistent with shared rules. |
| `README.md` | INSPECTED | Reconciled source-selection/status wording with current master implementation. |
| `ARK_X_Cinema_Current_State.txt` | INSPECTED | Historical workstation snapshot; not current configuration. |
| `RUN_ARK_X_CINEMA.bat` | INSPECTED | Repository-relative CLI launcher to `Engine/orchestrator.py`. |
| `Control/` | INSPECTED | Tkinter control center + VBS launcher; GUI stage display is not canonical checkpoint state. |
| `Config/` | INSPECTED | Central runtime configuration; local endpoint/path assumptions require PC validation. |
| `Engine/` | INSPECTED | Active engine, adapters, runners, historical snapshots, patch scripts, and tests inspected/classified. |
| `Engine/Tests/` | INSPECTED | Full test inventory reviewed; portable contract tests plus manual/legacy fixtures identified. |
| `Backups/` | INSPECTED | Historical archive; preserved, not treated as production execution. |
| `Project_Control/` | INSPECTED | All control records reviewed and reconciled where evidence required. |
| `docs/` | INSPECTED | AI handoff, build history, CI checkpoint, project status all reviewed. |
| `Projects/` | INSPECTED | Current example project artifacts reviewed; state is not evidence of full end-to-end completion. |
| `Movies/` | INSPECTED | Source-media directory; media intentionally excluded from Git. |
| `Analysis/`, `Finished/`, `Logs/`, `Music/`, `Narration/`, `Research/`, `Scenes/`, `Scripts/`, `SFX/`, `Subtitles/`, `Thumbnails/`, `Transcripts/`, `Upload/`, `Visuals/` | INSPECTED | Runtime/output/asset directories accounted for; empty or auxiliary where not currently connected to production. |

No repository directory was silently ignored. Large/binary/generated/history material was classified by metadata, references, consumers, or role rather than blindly treated as active code.

## System reconstruction

**Primary CLI path:** `RUN_ARK_X_CINEMA.bat` → `Engine/orchestrator.py`.  
**GUI path:** `Control/Launch_ARK_X_Cinema.vbs` → `Control/ark_cinema.py` → subprocess `Engine/orchestrator.py`.  
**Core modular path:** `Engine/stage_a_runner.py` → existing resumable stage adapters through the script stage on current master.  
**Canonical state:** `checkpoint.py` + `stage_state.py` + `resumable_orchestrator.py`.  
**Configuration:** `Config/config.json` → `runtime_config.py` → runtime/stage consumers.  
**External integrations:** FFmpeg/FFprobe subprocesses, whisper.cpp subprocess boundary, Ollama localhost HTTP boundary.  
**Data flow:** source package → workspace/source manifest → subtitle/AD ingestion → AD SRT → timeline → bounded evidence → Ollama intelligence → recap script.  
**Persistence:** per-movie `Projects/<movie>/` artifacts plus historical/global auxiliary areas.  
**Error handling:** stage adapters/checkpoints explicitly propagate failure and verify artifacts.  
**CI/build:** `.github/workflows/tests.yml` runs Python 3.11 + `python -m pytest Engine/Tests -q` on Ubuntu.  
**Deployment:** no production cloud deployment; local Windows launchers only.  
**Security boundaries:** local filesystem/process execution and localhost Ollama; no database/authentication/authorization subsystem exists in the current desktop architecture.

## Active engine findings

| Component | Status | Verified finding |
|---|---|---|
| Runtime configuration | INSPECTED | Centralized and repository-relative; `validate_runtime` does not fully prove every external dependency is runnable. |
| Workspace/source manifest | INSPECTED | Canonical per-movie workspace; exactly-one-usable-video rule is enforced. |
| Subtitle/AD pipeline | INSPECTED | Separate AD audio is converted to timestamped SRT through whisper.cpp boundary. |
| Timeline | INSPECTED | Deterministic cue-based timeline with subtitle/AD provenance; not computer-vision scene detection. |
| Evidence packets | INSPECTED | Bounded, provenance-preserving packets. |
| Ollama intelligence | INSPECTED | Real HTTP adapter + schema validation; actual model behavior remains PC-unverified. |
| Structured output | INSPECTED | Strict fail-closed extraction with regression coverage. |
| Recap script | INSPECTED | Evidence-grounded local-model script generation with timestamp/scene validation; real model quality unverified. |
| Stage runner | INSPECTED | Current master composes core stages only through script; full TTS/video/final-QA path is not on master. |
| TTS/video/QA adapters | INSPECTED | Boundaries exist; real production implementations from PR #6 are not merged to master. |
| Checkpoint/resume | INSPECTED | Atomic artifact checkpointing and ordered prerequisites; real-media interruption/recovery unverified. |
| GUI | INSPECTED | Functional control foundation; displayed stage progress is inferred from logs rather than authoritative checkpoint state. |

## Tests

The active `Engine/Tests` suite contains checkpoint, ingestion, intelligence, Ollama, runtime, workspace, script, resumability, structured-output, subtitle, timeline, transcription-adapter, TTS-adapter, video-adapter, QA-adapter, and Stage-A runner tests. Historical/manual recap and Whisper material is also present.

`Engine/Tests/Whisper/test_whisper.py` is explicitly skipped in CI and uses `faster-whisper` with a historical local path; it is classified as manual/legacy evidence, not the authoritative whisper.cpp production test.

## CI evidence

Latest audited master CI:

- Workflow: `ARK X Cinema Tests`
- Run: #113
- Commit: `e13366f82a8ef8f57eac632e1eeacdf14e37260e`
- Status: completed
- Conclusion: success
- Job: `tests` — success
- Engine test step — success

CI success proves the repository test contract for the current commit. It does not prove Windows runtime behavior, model output quality, RAM, TTS, FFmpeg production rendering, or a full movie run. fileciteturn276file0L2-L2

## Findings and repairs

### Confirmed defect — README source-selection contradiction

**Finding:** README described the largest valid video as generally preferred, while the current workspace implementation requires exactly one usable video and rejects ambiguous multi-video packages.

**Repair:** README updated to match the authoritative current implementation.

**Evidence:** commit `d71e684cba082a5b9c0ee1307744c07216583df8` records the surgical documentation correction. fileciteturn282file0L3-L7

**Final status:** FIXED / RE-SCANNED.

### Confirmed control-document ambiguity

**Finding:** Historical implementation/status records could be misread as completion of the new forensic audit.

**Repair:** `CURRENT_TASK.md`, `IMPLEMENTATION_STATUS.md`, and `MULTI_AI_STATUS.md` were clarified so the historical Phase-1 audit is evidence only and the new forensic audit is a separate operation tracked by this ledger.

**Final status:** FIXED / RE-SCANNED.

### False positive closed — supposedly missing docs

The fresh audit verified that `docs/AI_HANDOFF.md` and `docs/PROJECT_STATUS.md` do exist on current master. The earlier “missing file” concern was stale evidence, not a current repository defect. No duplicate replacement was created.

**Final status:** CLOSED AS FALSE POSITIVE.

### Historical technical debt — patch scripts

`Engine/apply_scene_editing_patch.py` and related historical scripts contain absolute local paths and text-replacement logic. They were inspected and classified as historical development mechanisms, not active production execution. They remain preserved per history rules.

**Final status:** OBSERVATION / HISTORICAL; no deletion justified.

## Security audit

Reviewed applicable current-master surfaces:

- tracked configuration/control files: no confirmed secret/API-key value identified;
- subprocess invocation: inspected current production paths; no confirmed `shell=True` usage in reviewed active paths;
- Ollama endpoint: configured to localhost;
- filesystem operations: path-based workspace operations reviewed;
- source media: excluded from Git and legally constrained;
- database/authentication/authorization/CSRF/CORS: not applicable to current local desktop architecture.

**Security result:** no critical security defect confirmed in the inspected current-master paths. This is not a universal security certification.

## Branch/collaboration audit

Current branch inventory:

- `master` — authoritative default branch.
- `github-only/structured-output-and-ci` — branch exists; current repository state does not show the reported structured-output work as a distinct merged branch state. Treat the original report as historical unless independently verified from a diverging branch.
- `stage-a/final-ci-validation` — validation branch, not master.
- `stage-a/pre-pc-integration` — unmerged development branch; PR #6 remains open, 25 commits, 20 changed files, base `master`, head `c5f9f235b53b3720a8f407c2ed7caf1685b55b78`. It contains later TTS/edit/FFmpeg/QA integration and is explicitly not counted as current-master completion. fileciteturn284file0L4-L13

The audited final master contains no wholesale replacement of `Engine/orchestrator.py` as part of the controlled forensic repair pass.

## Remaining UNVERIFIED items

These cannot be closed by GitHub-only evidence:

- actual Windows Whisper.cpp execution/performance and AD→SRT quality;
- actual Ollama/Qwen model behavior, grounding quality, and RAM;
- actual TTS engine execution, quality, speed, and RAM;
- actual FFmpeg production rendering and media inspection;
- real interrupted-run/resume behavior on production media;
- RAM target of approximately ≤2 GB additional active AI workload;
- complete 2–3 hour movie processing;
- final end-to-end Stage-A reliability;
- final human editorial/copyright/platform-policy judgment.

## Final audit determination

The new controlled forensic audit is **COMPLETE for the GitHub repository scope** represented by this ledger.

It does **not** mean the application is bug-free, secure in every possible respect, production-ready, or fully validated on Windows.

The repository is now in a verified state for the next controlled engineering decision, with confirmed defects repaired, historical material preserved, CI evidence current for the audited commit, and remaining environment-dependent questions explicitly recorded as `UNVERIFIED`.