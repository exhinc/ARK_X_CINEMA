# ARK X CINEMA — EXECUTION ARCHITECTURE DECISION

**Status:** ACTIVE DECISION RECORD  
**Date:** 2026-09-03  
**Scope:** Runtime architecture, model execution, cloud/offload experiments, long-movie processing, and monetization-oriented editing policy

---

## 1. Decision Summary

ARK X Cinema will remain **local-first and accelerator-optional**.

The current GitHub architecture is not being replaced by a Colab-first, Kaggle-first, MoviePy-first, or llama.cpp-only design.

The working principle is:

```text
ARK X CINEMA
      |
      +--> LOCAL WINDOWS EXECUTOR
      |
      +--> OPTIONAL CLOUD/ACCELERATOR EXECUTOR
      |
      +--> REPLACEABLE LLM BACKEND
             |
             +--> Ollama (current local backend)
             |
             +--> llama.cpp/server (future optional backend)
```

The project will make runtime decisions from **measured workload results on the actual target machine**, not from generic claims about RAM, speed, model size, or cloud quotas.

---

## 2. Current Architecture Remains Locked

The following current-master design remains authoritative unless a later explicit decision supersedes it:

```text
AD AUDIO
   -> whisper.cpp
   -> TIMESTAMPED AD SRT
   -> CANONICAL TIMELINE
   -> BOUNDED EVIDENCE PACKETS
   -> LOCAL MOVIE INTELLIGENCE
   -> RECAP SCRIPT
   -> PIPER TTS
   -> SCRIPT-TO-SCENE EDIT MANIFEST
   -> FFMPEG ASSEMBLY
   -> FFPROBE / QA
```

The Audio Description track remains a primary movie-understanding source. The project must not assume that an AD SRT already exists and must not replace AD transcription with an unrelated subtitle source.

The existing FFmpeg-based video path remains preferred over replacing it with MoviePy. FFmpeg provides the direct subprocess-based media processing architecture already integrated into the repository and avoids requiring the entire source movie to exist as a Python-level in-memory object.

---

## 3. LLM Runtime Decision: Do Not Rip Out Ollama

### Current decision

Keep **Ollama + Qwen 3 1.7B** as the current local LLM path because it is already integrated into the repository and fits the project's local-runtime objective.

Do **not** declare Ollama universally superior to llama.cpp, and do **not** declare llama.cpp universally faster or lower-memory without benchmarking the actual workload.

### Architectural improvement

The intelligence layer should remain backend-replaceable so that a future llama.cpp/server adapter can be added without redesigning the rest of the pipeline.

The interface boundary should remain conceptually:

```text
MOVIE INTELLIGENCE
       |
       +--> Ollama adapter
       |
       +--> future llama.cpp/server adapter
```

The rest of the pipeline should depend on the structured intelligence contract, not on one inference runtime.

### Reason

Ollama is a higher-level local model/runtime-management layer. llama.cpp is a lower-level inference engine/server ecosystem. They overlap in capability but are not interchangeable architectural concepts. Performance and RAM behavior depend on the exact model, quantization, context, prompt size, backend settings, hardware, and workload.

Therefore the project will **benchmark before switching**.

---

## 4. Cloud Execution Decision: Optional Experiment, Not Production Dependency

### Google Colab

Google officially describes Colab as free of charge, but its free resources are dynamic and not guaranteed. GPU availability, hardware type, usage limits, idle behavior, and maximum runtime can vary.

Therefore:

- Colab may be used as an optional benchmark/experimentation environment.
- Colab must not become a required production dependency for Stage A.
- The system must not depend on a specific free GPU model, fixed RAM amount, fixed disk allowance, or guaranteed runtime duration.
- A cloud session must be assumed capable of disappearing or changing resource allocation.
- Long-running production should remain checkpointed and resumable regardless of execution environment.

Reference: Google Colab FAQ  
https://research.google.com/colaboratory/faq.html

### Kaggle

Kaggle notebooks may also be evaluated as an optional free accelerator environment. Any resource figures observed during experiments are treated as **currently observed/eligible resources**, not permanent guarantees for this project.

Kaggle is therefore an optional benchmark target, not a required service dependency.

---

## 5. Storage Decision

Cloud storage is not assumed to be a practical permanent home for large source movies under a $0/month constraint.

For example, a standard personal Google Account currently includes up to 15 GB shared across Google Drive, Gmail, and Google Photos. That is small relative to many multi-hour movie source files.

Therefore the project remains **local-disk-first for source media and durable production artifacts**.

Reference: Google Account storage  
https://support.google.com/accounts/answer/6374270

---

## 6. RAM Decision

The project's approximate **<=2 GB additional active AI-workload RAM target remains a measured validation target, not an assumption**.

The project must continue to enforce:

```text
ONE HEAVY AI STAGE AT A TIME
```

Default sequencing remains:

```text
TRANSCRIPTION
   -> release transcription resources
INTELLIGENCE
   -> release LLM resources
SCRIPT
TTS
   -> release TTS resources
VIDEO / FFMPEG
QA
```

Long movie source media must not be loaded into Python memory as one giant object merely because the source file is several hours long.

### Important implementation note

`Engine/intelligence_pipeline.py` currently accumulates successful intelligence results in an in-memory list. This is functional but is not the preferred long-movie persistence strategy.

A future surgical improvement should persist each completed intelligence result to disk incrementally and retain only bounded working state in RAM. This should be treated as a **long-movie robustness improvement**, not evidence that the current design is fundamentally broken.

---

## 7. Benchmark-First Runtime Decisions

No architecture change should be justified solely by claims such as:

- "this model only needs X GB because the file is X GB"
- "llama.cpp is always faster"
- "Ollama is always best"
- "Colab always gives a T4/P100"
- "FFmpeg must use a fixed thread count"
- "a particular flag is required" without checking the installed binary

Instead, the PC validation ladder should record real measurements for:

| Stage | Measure |
|---|---|
| whisper.cpp | peak/observed RAM, elapsed time, AD->SRT quality |
| Ollama/Qwen | peak/observed RAM, generation speed, schema success, quality |
| Piper | peak/observed RAM, elapsed time, output quality |
| FFmpeg | elapsed render time, RAM behavior, playback validity |
| Full runner | peak RAM across stages, restart/resume behavior, total elapsed time |

The same workload can then be benchmarked optionally on a cloud accelerator to determine whether offloading produces a meaningful advantage.

---

## 8. Long-Movie Execution Decision

The project should scale by **persistence and bounded processing**, not by putting more of the movie into RAM.

Required design principles remain:

- movie-scoped workspace
- bounded evidence packets
- deterministic manifests
- checkpointed stage state
- artifact integrity verification
- disk-space preflight
- cleanup rules
- safe interruption/resume
- incremental artifact persistence where practical

The project will progress through:

```text
TINY TEST
   -> MEDIUM REAL-MEDIA TEST
   -> FIRST FULL MOVIE
   -> HUMAN QA
   -> STAGE-A RELIABILITY
   -> 1 VIDEO/DAY
   -> 2 VIDEOS/DAY
   -> 3 VIDEOS/DAY
```

No full movie is to be used as the first runtime test.

---

## 9. Video Editing Decision: Keep FFmpeg

The current FFmpeg engine remains the production media-processing path.

Do not replace it with MoviePy solely because a tutorial or external recommendation uses MoviePy.

The project will improve visual editing behavior through deterministic edit manifests and FFmpeg filters/operations where needed, while keeping the underlying media engine stable.

Any future visual enhancement such as crop/pan, motion, zoom, mirroring, transitions, or clip selection must be evaluated for:

1. editorial value,
2. processing cost,
3. reliability,
4. effect on originality/quality,
5. compatibility with the current deterministic pipeline.

These effects are **not** to be implemented as a mechanism for evading automated copyright or Content ID systems.

---

## 10. Monetization / Copyright-Safety Architecture Decision

The project will **not** implement a supposed "4-second rule", hflip tricks, micro-zoom tricks, audio masking, or other transformation techniques whose purpose is to defeat Content ID or make copyrighted footage harder to detect.

There is no project assumption that a particular clip duration or visual transform guarantees copyright safety or YouTube monetization.

The production goal is instead to make the recap substantively original through meaningful narration, analysis, editorial framing, cause/effect explanation, character reasoning, thematic interpretation, and substantive editing.

YouTube's monetization policy states that reused content may be eligible where there is meaningful original commentary or substantive modification, while also making clear that copyright remains a separate issue. YouTube also states that repetitive or mass-produced content may be ineligible for monetization.

Therefore:

```text
CONTENT-ID DETECTION
        !=
COPYRIGHT STATUS
        !=
YPP / REUSED-CONTENT ELIGIBILITY
```

The project must treat all three as separate considerations and retain final human QA/editorial judgment.

Reference: YouTube Channel Monetization Policies  
https://support.google.com/youtube/answer/1311392

---

## 11. What This Decision Does NOT Claim

This document does **not** claim that:

- the <=2 GB RAM target has been achieved;
- a full 2-4 hour movie has completed end-to-end successfully;
- local execution is faster than cloud execution;
- Colab or Kaggle will always provide a particular GPU or RAM profile;
- Ollama is faster than llama.cpp for this workload;
- llama.cpp would solve every performance problem;
- Stage A is production-ready before PC validation;
- YouTube monetization or copyright safety is guaranteed.

Those claims require evidence from actual testing, official policy review, or both.

---

## 12. Implementation Priority After This Decision

The immediate next work remains **PC validation**, not another large architecture rewrite.

Recommended surgical improvements after basic runtime validation:

1. Measure actual per-stage RAM and runtime.
2. Add incremental disk persistence for intelligence results.
3. Add/verify robust preflight checks for disk space and external binaries.
4. Benchmark local LLM execution versus an optional llama.cpp backend before changing the default.
5. Benchmark optional cloud execution only if local measurements show a real throughput problem.
6. Continue human QA of the first finished movie before scaling production volume.

---

## 13. Supersession Rule

Any future change to this architecture should be recorded as a new dated decision that explicitly identifies:

- the decision being superseded,
- the measured evidence supporting the change,
- the affected repository paths,
- the rollback/compatibility implications,
- the new validation required.

No single tutorial, benchmark, AI recommendation, or cloud-resource screenshot is sufficient by itself to supersede this record.

---

## FINAL DECISION

**KEEP THE CURRENT CORE. MEASURE THE REAL MACHINE. KEEP BACKENDS SWAPPABLE. USE CLOUD ONLY WHEN MEASURED USEFUL. PERSIST LONG-MOVIE STATE TO DISK. DO NOT BUILD COPYRIGHT-DETECTION EVASION INTO THE PIPELINE.**
