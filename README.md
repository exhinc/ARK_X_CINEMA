# ARK X Cinema

### Stories Beyond the Screen

**A local-first, low-resource movie-recap production engine for Windows.**

ARK X Cinema is an automated YouTube movie-recap production system designed to transform a legally obtained movie/source package into the structured assets required for an original recap video.

The system is being engineered around three principles:

- **Maximum practical automation**
- **$0/month software and infrastructure**
- **Human final QA and approval**

The core production goal is to **reliably process one real 3–4 hour movie end-to-end** on the target Windows PC and produce a finished recap video that passes the required automated and human QA. There is no fixed daily movie quota. After the first full-length movie is reliable, additional throughput is measured and optimized empirically based on actual processing time, hardware, storage, and workload conditions.

> **Project status:** Active development  
> **Current architecture:** Locked  
> **Current milestone:** Production-engineering buildout  
> **Default branch:** `master`

---

## What ARK X Cinema Does

The system is designed to automate the production chain from source ingestion through final-video preparation:

```text
LEGAL MOVIE SOURCE PACKAGE
          │
          ▼
    SOURCE INSPECTION
          │
          ▼
  SUBTITLE / AUDIO DISCOVERY
          │
          ├───────────────┐
          ▼               ▼
   MOVIE SUBTITLES     AD AUDIO
                          │
                          ▼
                     whisper.cpp
                          │
                          ▼
                       AD SRT
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
    SPOKEN CONTENT                 VISUAL / ACTION
          │                               │
          └───────────────┬───────────────┘
                          ▼
                 MOVIE INTELLIGENCE
                          │
                          ▼
                  RECAP GENERATION
                          │
                          ▼
                    NARRATION
                          │
                          ▼
                  SCENE SELECTION
                          │
                          ▼
                       FFmpeg
                          │
                          ▼
                    FINAL VIDEO
                          │
                          ▼
                    HUMAN QA
                          │
                          ▼
                    UPLOAD READY
```

The architecture is intentionally staged so heavy AI workloads can be processed sequentially rather than simultaneously.

---

# Core Architecture

## 1. Source Package Inspection

ARK X Cinema accepts a movie as either:

```text
Movies/
└── Movie Name/
    ├── movie.mkv
    ├── subtitles.srt
    └── audio_description.mp3
```

or a standalone movie file for source inspection/manifests.

**Full Stage-A production requires the separate Audio Description audio asset.** A standalone movie file by itself is not sufficient for the locked production path, because Stage A must run `AD AUDIO -> whisper.cpp -> TIMESTAMPED AD SRT -> MOVIE INTELLIGENCE`.

The engine discovers available video, subtitle, and audio assets and uses FFprobe to inspect media properties.

The current canonical source-manifest implementation requires **exactly one usable movie video** in a source package and rejects ambiguous multi-video packages rather than silently selecting one. `project_workspace.py` is the authoritative implementation for that rule.

---

## 2. Subtitle Handling

The engine can work with:

- External subtitle files
- Embedded subtitle streams
- SRT and other supported subtitle formats

Subtitle data is normalized toward SRT for downstream processing.

English subtitle streams are preferred when multiple embedded streams are available.

---

# 3. Audio Description Pipeline

### This is a locked architectural decision.
