# ARK X CINEMA — CHANGELOG

All significant project changes are recorded here in chronological order.

---

## 2026-08-27 — Phase 2 Runtime Foundation Started

### Added
- `Engine/runtime_config.py`
- `Engine/Tests/test_runtime_config.py`

### Changed
- Removed the user-specific repository root from `Config/config.json`.
- Added repository-relative Whisper configuration fields.
- Added explicit Ollama API configuration.
- Made the BAT launcher resolve the repository from `%~dp0`.
- Made the VBS launcher resolve the repository from its own script location.

### Important
The new runtime configuration layer is intentionally not yet declared the authoritative runtime for the production orchestrator. The orchestrator still contains legacy hard-coded Whisper constants and must be wired to the new configuration layer in the next Phase 2 step.

### Result
Phase 2 has begun. The first build target—portable runtime configuration foundation—is implemented; integration remains pending.

---

## 2026-08-27 — Phase 1 Implementation Audit Completed

### Added
- `Project_Control/IMPLEMENTATION_STATUS.md`
- Definitive repository/code implementation assessment.

### Audit conclusion
- Repository foundation is established.
- AD Audio -> whisper.cpp -> timestamped AD SRT is tested/successful.
- Complete first-movie production is not yet ready.
- Configuration portability, canonical project artifacts, movie intelligence, structured LLM output, TTS, scene synchronization, rendering, final subtitles, automated QA, and full recovery still require engineering/integration.

### Important findings
- `Config/config.json` contains machine-specific absolute paths.
- Active orchestrator contains hard-coded Whisper paths.
- Launch scripts contain machine-specific Desktop paths.
- Existing Whisper test script uses `faster-whisper` and should be treated as legacy/benchmark evidence rather than the authoritative whisper.cpp production test.
- Stored recap JSON checkpoint currently fails JSON parsing.
- Historical patch scripts and multiple orchestrator backups exist and should be treated as historical/transition artifacts.

### Result
Phase 1 is complete. The project moves to Phase 2 — Production Engine Foundation.

---

## 2026-08-27 — Project Control System Initialization

### Added
- Permanent project-state documentation system.
- Architecture decision log.
- Test-results log.
- Current-task handoff document.
- Git version-control initialization.

### Purpose
Prevent loss of project history across chats, sessions, developers,
and AI agents.

### Important
This change does NOT modify the production architecture.

---

## 2026-08-27 — AD Transcription Architecture Locked

### Decision
Separate Audio Description audio is converted to timestamped SRT
using whisper.cpp.

### Pipeline

AD Audio MP3
    ->
whisper.cpp
    ->
AD SRT with timestamps
    ->
Movie Intelligence

### Reason
The AD audio contains both spoken information and visual/action
descriptions that are valuable for movie understanding.

---

## 2026-08-26 — Full AD whisper.cpp Test

### Input
The Platform (2019) Audio Description (AD).mp3

### Result
SUCCESS

### Significance
Full AD audio transcription completed successfully using whisper.cpp.

---

## Historical project work

Existing project files and backups contain previous development history.
Git initialization creates the permanent version-control history from
the current state forward.
