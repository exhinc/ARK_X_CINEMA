# ARK X CINEMA — TEST RESULTS

---

## TEST-001 — Full AD Audio Transcription

**Date:** 2026-08-26

### Input

The Platform (2019) Audio Description (AD).mp3  
Size: approximately 135.8 MB

### Tool

whisper.cpp

### Expected

Timestamped SRT generated from the separate AD audio.

### Result

SUCCESS — historical full-AD transcription test.

### Significance

Supports the locked pipeline:

```text
AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT
```

---

## TEST-002 — Historical Whisper Fixtures

Historical outputs include:

- `Transcripts/whisper_cpp_test.srt`
- `Transcripts/whisper_cpp_test.txt`
- `Transcripts/deep_audit_whisper.srt`

These remain evidence only and are not substitutes for fresh PC validation.

---

## TEST-003 — GitHub Actions / Stage-A Integration

**Commit:** `3fd4a87c2a68df98eff3652fbc65c4f2f972267e`  
**Workflow:** `ARK X Cinema Tests`  
**Run:** #123  
**Job:** `tests`  
**Result:** SUCCESS

This run verified the complete portable `Engine/Tests` contract after the controlled Stage-A integration merge.

It does not prove Windows dependency execution, model quality, RAM usage, real FFmpeg rendering, or full-movie success.

---

## TEST-004 — Current Repository Baseline

As of 2026-08-31, the GitHub-side Stage-A implementation is treated as complete on `master` based on the merged Stage-A integration and successful CI evidence.

The remaining tests are intentionally environment-dependent:

- Whisper.cpp real execution and AD->SRT quality
- Ollama/Qwen real structured-output behavior and RAM
- Piper real execution, audio quality, and RAM
- FFmpeg real rendering
- real final-media inspection
- interrupted-run/resume on real media
- short -> medium -> full-movie end-to-end validation
- final human QA

---

## TEST RECORDING RULE

Future tests must record:

- unique test ID
- date/time
- input
- tool/version
- command/configuration when relevant
- expected result
- actual result
- PASS/FAIL
- important observations
- affected architecture decision, if any

A failed test is still preserved as history. A later success does not erase the historical failure.
