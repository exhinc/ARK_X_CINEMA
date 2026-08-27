# ARK X CINEMA — CHANGELOG

All significant project changes are recorded here in chronological order.

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

