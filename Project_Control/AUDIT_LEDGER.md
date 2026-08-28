# ARK X CINEMA — FORENSIC AUDIT LEDGER

**Audit type:** Controlled forensic audit & repair
**Audit branch:** `master`
**Audit baseline:** `b431fe1ac4036aec85fc3dc51f534a22e4fc4126`
**Audit started:** 2026-08-28
**Status:** IN PROGRESS — discovery and controlled repair pass

**Purpose:** Permanent mechanism for tracking coverage and uncertainty during full repository audits.

**Authority:** This ledger supplements `AGENTS.md` and the existing Project_Control system. It does not replace or weaken any existing project rule.

## Status values

- `INSPECTED` — contents/behavior reviewed sufficiently for the audit scope.
- `PARTIALLY INSPECTED` — some relevant material reviewed, but meaningful coverage remains.
- `NOT APPLICABLE` — category does not apply to this repository/component, with a recorded reason.
- `UNVERIFIED` — evidence is insufficient to establish the required fact.
- `BLOCKED` — inspection could not be completed because of an access/tool/environment limitation.

## Repository census

| Path / area | Type | Status | Purpose / role | Key references / consumers | Tests / evidence | Findings / risk | Fixed? | Verification notes |
|---|---|---|---|---|---|---|---|---|
| `.github/` | GitHub configuration | INSPECTED | Workflow configuration | `tests.yml` | Current master run #108 succeeded | CI is portable/Ubuntu-only; no Windows/runtime validation | No | Workflow and latest run inspected |
| `.gitignore` | Configuration | INSPECTED | Source/runtime hygiene | Git | File inspected | Media exclusion rules present; project artifact policy documented | No | No destructive change justified |
| `AGENTS.md` | AI control | INSPECTED | Authoritative AI engineering contract | Claude/Grok/future agents | File inspected | Forensic protocol integrated; preserved | Yes | Verified as current authoritative rules |
| `CLAUDE.md` | AI control | INSPECTED | Claude entry-point instructions | `AGENTS.md` | File inspected | Consistent with shared rules | No | No conflict found |
| `README.md` | Documentation | INSPECTED | User/system documentation | Human/agents | File inspected | Video-selection wording is stale vs current exact-one-video code; status/structure text also needs reconciliation | Pending | Confirmed contradiction |
| `ARK_X_Cinema_Current_State.txt` | Historical/runtime evidence | INSPECTED | Recorded workstation snapshot | Human/history | File inspected | Contains historical absolute local paths and old runtime snapshot; must not be treated as current repository configuration | No | Correctly classified as historical evidence |
| `RUN_ARK_X_CINEMA.bat` | Launcher | INSPECTED | Windows CLI launcher | `Engine/orchestrator.py` | File inspected | Repository-relative launcher is correct; current README/old status claims about Desktop assumption are stale | No | Actual launcher uses `%~dp0` |
| `Analysis/` | Runtime/output directory | INSPECTED | Analysis outputs | Production stages | Tree/metadata inspected | Empty/structure-only on GitHub | No | No code present to repair |
| `Backups/` | Historical archive | INSPECTED | Historical source backups | History only | Directory + backup inventory inspected | Large historical orchestrator copies; preserve, do not execute as production | No | Classified as historical |
| `Config/` | Runtime configuration | INSPECTED | Canonical runtime settings | `runtime_config.py` | File + consumer inspected | Relative paths and local Ollama endpoint are intentional; PC dependency availability remains unverified | No | Consistent with runtime code |
| `Control/` | User control | INSPECTED | Tkinter production control center + VBS launcher | `orchestrator.py` | Files inspected | GUI launches conservative orchestrator and infers displayed stages from logs, not canonical state | Pending | Real integration not production-proven |
| `Engine/` | Core engine | INSPECTED | Production primitives/adapters | `Control/`, tests | Recursive tree + key source files inspected | Current master production runner stops after script; downstream engines absent from master | No | Core active files inspected; legacy files classified |
| `Engine/Tests/` | Tests | INSPECTED | Unit/contract regression suite | CI | Recursive tree + representative/full inventory inspected | Tests are contract-level; several local/manual tests are skipped | No | CI workflow runs this directory |
| `Finished/` | Output directory | INSPECTED | Final media output | Video pipeline | Tree/metadata | Empty on GitHub | No | No source code |
| `Logs/` | Runtime output | INSPECTED | Logs | Orchestrator/control | Tree/metadata | Runtime output intentionally not committed | No | `.gitignore` covers logs |
| `Movies/` | Source media | INSPECTED | Local legally obtained movie sources | Ingestion | Tree/metadata + `.gitignore` inspected | Source media excluded from Git; no current source media on GitHub | No | Correct design |
| `Music/` | Asset directory | INSPECTED | Optional music assets | Future video stage | Structure inspected | Empty on GitHub | No | Not yet production-connected |
| `Narration/` | Output directory | INSPECTED | Narration output | TTS stage | Structure inspected | No production TTS engine on master | No | Downstream work remains |
| `Project_Control/` | Project governance | INSPECTED | Persistent project state/history | AI agents/human | All control records inspected | Historical status references needed reconciliation | Partially | This audit is the fresh forensic operation |
| `Research/` | Research material | INSPECTED | Research inputs | Future workflow | Structure inspected | Empty/structure-only | No | No code |
| `Scenes/` | Scene data/output | INSPECTED | Scene/timeline data | Timeline/editing | Structure inspected | Current master timeline artifact is project-scoped under `Projects/.../scenes`; global directory is not canonical | No | Architecture preserved |
| `Scripts/` | Script output | INSPECTED | Script outputs | Script stage | Structure inspected | Current master script adapter writes project-local `script/recap.txt` | No | Global folder not canonical |
| `SFX/` | Asset directory | INSPECTED | Sound effects | Future video stage | Structure inspected | Empty/structure-only | No | Not yet production-connected |
| `Subtitles/` | Subtitle assets | INSPECTED | Subtitle outputs | Subtitle pipeline | Structure inspected | Current pipeline is project-scoped; global folder is auxiliary | No | No contradiction in code |
| `Thumbnails/` | Media asset directory | INSPECTED | Future thumbnail outputs | Publishing | Structure inspected | Not part of Stage-A execution | No | Out of immediate scope |
| `Transcripts/` | Transcript outputs | INSPECTED | Historical/global transcription artifacts | Whisper tests/history | Structure/README/status evidence inspected | Must not be confused with canonical per-project transcript paths | No | Historical/auxiliary role |
| `Upload/` | Publishing output | INSPECTED | Upload-ready package | Future publishing | Structure inspected | Upload preparation not implemented as production stage | No | Future stage |
| `Visuals/` | Media asset directory | INSPECTED | Visual assets | Future workflow | Structure inspected | Empty/structure-only | No | No source code |

## Important active engine inventory

| Path / area | Status | Finding |
|---|---|---|
| `Engine/orchestrator.py` | INSPECTED | Conservative current entrypoint; initializes runtime, discovers/inspects source, creates workspace, ingests subtitles/AD, then exits at foundation runtime pass. |
| `Engine/stage_a_runner.py` | INSPECTED | Current master core runner reaches ingestion → transcription → timeline → intelligence → script; it is not the full final-media runner. |
| `Engine/runtime_config.py` | INSPECTED | Centralizes Whisper/Ollama/runtime settings; `validate_runtime` validates configured Whisper paths but not all external executables/services. |
| `Engine/project_workspace.py` | INSPECTED | Canonical per-movie workspace and source manifest implementation. |
| `Engine/subtitle_pipeline.py` | INSPECTED | SRT validation/normalization and AD audio → whisper.cpp → SRT primitive. |
| `Engine/timeline_engine.py` | INSPECTED | Deterministic cue-based timeline; not semantic CV scene detection. |
| `Engine/movie_intelligence.py` | INSPECTED | Bounded evidence packet construction with provenance and size limits. |
| `Engine/intelligence_pipeline.py` | INSPECTED | Ollama packet analysis function; partial results stay in memory and packet-level resume is not implemented. |
| `Engine/intelligence_stage_adapter.py` | INSPECTED | Resumable intelligence stage boundary; failed packet causes stage failure. |
| `Engine/ollama_intelligence.py` | INSPECTED | Real Ollama HTTP adapter and schema validation; actual model behavior remains PC-unverified. |
| `Engine/structured_output.py` | INSPECTED | Strict fail-closed JSON extraction; regression-tested. |
| `Engine/recap_script_engine.py` | INSPECTED | Evidence-grounded local Ollama recap generation with timestamp/scene validation. |
| `Engine/script_stage_adapter.py` | INSPECTED | Resumable script boundary; compatible with text and segment metadata results. |
| `Engine/checkpoint.py` | INSPECTED | Atomic checkpoints and SHA-256 artifact integrity. |
| `Engine/stage_state.py` | INSPECTED | Ordered stages and prerequisite enforcement. |
| `Engine/resumable_orchestrator.py` | INSPECTED | Stage execution/resume boundary. |
| `Engine/orchestrator_stage_adapter.py` | INSPECTED | Bridge from established functions to resumable stage contracts. |
| `Engine/transcription_stage_adapter.py` | INSPECTED | AD transcription stage boundary. |
| `Engine/timeline_stage_adapter.py` | INSPECTED | Timeline stage boundary. |
| `Engine/tts_stage_adapter.py` | INSPECTED | TTS boundary only on current master. |
| `Engine/video_stage_adapter.py` | INSPECTED | Video boundary only on current master. |
| `Engine/qa_stage_adapter.py` | INSPECTED | QA boundary only on current master. |
| `Engine/apply_scene_editing_patch.py` | INSPECTED | Historical text-patching mechanism; not canonical production execution. |
| `Engine/fix_duplicates.py` | INSPECTED | Historical repair script; not canonical production execution. |
| `Engine/orchestrator_before_*` | INSPECTED | Historical snapshots; not active entrypoints. |

## Test inventory

Current `Engine/Tests` inventory includes:

- `test_checkpoint.py`
- `test_ingestion_adapter.py`
- `test_ingestion_integration.py`
- `test_intelligence_pipeline.py`
- `test_intelligence_stage_adapter.py`
- `test_movie_intelligence.py`
- `test_ollama_intelligence.py`
- `test_orchestrator_runtime.py`
- `test_orchestrator_stage_adapter.py`
- `test_project_workspace.py`
- `test_qa_stage_adapter.py`
- `test_recap_script_engine.py`
- `test_resumable_orchestrator.py`
- `test_run_intelligence_stage.py`
- `test_runtime_config.py`
- `test_script_stage_adapter.py`
- `test_stage_a_runner.py`
- `test_stage_state.py`
- `test_structured_output.py`
- `test_subtitle_pipeline.py`
- `test_timeline_engine.py`
- `test_timeline_stage_adapter.py`
- `test_transcription_stage_adapter.py`
- `test_tts_stage_adapter.py`
- `test_video_stage_adapter.py`

Additional historical/manual material:

- `Engine/Tests/Recap/test_recap_json.py`
- `Engine/Tests/Recap/test_recap_json_raw.txt`
- `Engine/Tests/Recap/test_recap_json_result.json`
- `Engine/Tests/Whisper/test_whisper.py`
- `Engine/Tests/Whisper/Legacy/benchmark.srt`
- `Engine/Tests/Whisper/Legacy/benchmark.txt`
- `Engine/Tests/Whisper/Legacy/speech.srt`
- `Engine/Tests/Whisper/Legacy/test.txt`

The manual Whisper test is explicitly module-skipped in CI and uses `faster-whisper` plus a historical hard-coded local path. It is classified as legacy/manual evidence, not the authoritative whisper.cpp production test.

## System reconstruction record

- **Primary launcher:** `RUN_ARK_X_CINEMA.bat` → `Engine/orchestrator.py`.
- **GUI launcher:** `Control/Launch_ARK_X_Cinema.vbs` → `Control/ark_cinema.py` → subprocess `Engine/orchestrator.py`.
- **Current core composition:** `Engine/stage_a_runner.py` calls existing stage adapters through checkpoint/resume boundaries through the script stage.
- **Data flow:** source package → source manifest → subtitle/AD ingestion → AD SRT → timeline → bounded evidence → Ollama intelligence → recap script.
- **Configuration flow:** `Config/config.json` → `Engine/runtime_config.py` → orchestrator/stage runner/LLM path.
- **State flow:** `Engine/checkpoint.py` + `Engine/stage_state.py` + `Engine/resumable_orchestrator.py`.
- **External integrations:** FFmpeg/FFprobe subprocesses, whisper.cpp subprocess, Ollama local HTTP API; real external execution is PC-unverified.
- **Persistence:** per-movie `Projects/<movie>/` artifacts plus legacy/global directories and historical artifacts.
- **Error propagation:** stage wrappers persist failure checkpoints and return/raise explicit stage errors.
- **Build/test path:** `.github/workflows/tests.yml` runs Python 3.11 + pytest on Ubuntu.
- **Deployment path:** no production cloud deployment is defined; Windows launchers are local.
- **Security boundaries:** local filesystem/process execution and local HTTP Ollama boundary; no authentication subsystem/database is present in the repository.

## Defect propagation record

| Defect pattern | Initial location | Repository-wide search performed? | Related occurrences | Fixes applied | Regression checks | Final status |
|---|---|---|---|---|---|---|
| Stale audit/status references | Project_Control docs | Yes — control docs, README, issue references reviewed | Missing `docs/AI_HANDOFF.md` / `docs/PROJECT_STATUS.md` references; stale status wording | Pending documentation reconciliation | Pending | CONFIRMED |
| Video-selection documentation mismatch | `README.md` | Yes — compared README claims to active workspace/orchestrator selection code | README claims largest valid video generally preferred; current code rejects multiple videos | Pending | Pending | CONFIRMED |
| Historical/manual tool mismatch | `Engine/Tests/Whisper/test_whisper.py` | Yes — test tree + architecture docs | Manual test uses faster-whisper while production decision is whisper.cpp | No — historical evidence should be preserved | Existing CI skip verified | OBSERVATION / LEGACY |
| GUI status derived from console keywords | `Control/ark_cinema.py` | Yes — control center + orchestrator inspected | GUI stage display can diverge from canonical stage checkpoints | Not yet — requires integration decision | None | CONFIRMED DESIGN RISK |
| Fine-grained intelligence packet resume absent | `Engine/intelligence_stage_adapter.py` | Yes — intelligence/stage/checkpoint path inspected | Entire intelligence stage is checkpointed as a unit | No — not yet proven necessary for Stage A | Existing stage tests | ENGINEERING GAP |
| Runtime dependency validation incomplete | `Engine/runtime_config.py` | Yes — config/runtime consumers inspected | Whisper paths validated; FFmpeg/FFprobe/Ollama/TTS not all validated here | Not yet — production dependency policy needs confirmation | Existing runtime tests | ENGINEERING GAP |

## Branch / collaboration audit

- `master` — current default branch; audited baseline above.
- `github-only/structured-output-and-ci` — exists; previously reported structured-output work is not independently present as a distinct branch state from master in the earlier audit; branch should continue to be treated as historical collaboration evidence unless it diverges.
- `stage-a/final-ci-validation` — historical validation branch; not current master.
- `stage-a/pre-pc-integration` — currently diverges from master and contains 25 commits / downstream Stage-A pre-PC work; it is an unmerged development branch and is not part of the current master baseline.
- PR #4 — merged into master; core intelligence/recap changes.
- PR #5 — closed, validation-only, not merged.
- PR #6 — open; contains later TTS/edit/FFmpeg/QA integration. It is not counted as master-complete work.

## CI evidence

Latest `master` workflow run inspected:

- Workflow: `ARK X Cinema Tests`
- Run: #108
- Commit: `3138ebf8e9cc9394a9cb8dc552bcc486f30ac2b3`
- Event: push
- Status: completed
- Conclusion: success
- Job: `tests` — success
- `Run engine tests` step — success

The workflow definition uses Python 3.11 and runs `python -m pytest Engine/Tests -q`. CI passing is repository-contract evidence only; it is not Windows/runtime validation.

## Security audit

### Reviewed surfaces

- Secrets/API keys in tracked configuration: no confirmed secret value found in the reviewed configuration/control files.
- Subprocess calls: production code uses argument lists rather than shell command strings in the inspected current runtime paths; no `shell=True` occurrence was found by repository code search.
- Local HTTP Ollama integration: endpoint is localhost by configuration; no remote auth boundary is defined.
- File operations: project workspace writes are path-based; archive/historical files are not automatically executed.
- Source-media handling: large media is ignored by Git and local-source use is explicitly constrained to legal acquisition.
- Authentication/authorization/database/CSRF/CORS: not applicable to the current local desktop engine architecture based on inspected repository contents.

### Security status

No critical security defect was confirmed in the inspected current master paths.
This is **not** a declaration that the repository is universally secure.

## Completion gate

The audit remains **IN PROGRESS** until documentation/control repairs, final changed-file review, post-repair re-scan, and final regression verification are complete.

Current remaining `UNVERIFIED` / `BLOCKED` items include:

- Real Windows execution of Whisper.cpp.
- Real Ollama/Qwen behavior and RAM measurement.
- Real TTS execution/performance.
- Real FFmpeg rendering/performance.
- Full 2–3 hour movie run.
- Final Stage-A end-to-end reliability.
- Exact behavioral quality of generated recap content.
- Any machine-local files that are excluded from Git, including the actual local movie/media inputs.
