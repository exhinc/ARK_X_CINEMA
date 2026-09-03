# ARK X Cinema — Shared AI Agent Instructions

## Authority and team
GitHub `master` is the shared engineering source of truth. The primary AI collaborators are ChatGPT, Claude, and Grok. Do not assume another AI tool or agent is part of the workflow unless the owner explicitly adds it.

Before changing code, inspect the current repository, relevant tests, project status, and recent commits. Do not rely on historical chat claims when the repository can answer the question.

## Active architecture decision record
The current execution-architecture decision is maintained at `Project_Control/EXECUTION_ARCHITECTURE_DECISION.md`. It is the active decision record for runtime/model execution, optional cloud/accelerator experiments, replaceable LLM backends, long-movie persistence, FFmpeg usage, benchmark-first decisions, and monetization-oriented editing policy.

Agents must read this record before proposing changes in those areas. It supplements the project state and current-task records; it does not by itself prove PC runtime validation or production readiness.

## Multi-AI collaboration protocol
The mandatory multi-agent startup, authority/conflict-resolution, current-commit CI, and change-record procedure is maintained in `Project_Control/AI_COLLABORATION_PROTOCOL.md`.

Every agent must follow that protocol before making significant repository changes. `Project_Control/CHANGELOG.md` records project-significant history, and `Project_Control/DECISIONS.md` records architectural decisions.

Important distinction: `Project_Control/DECISIONS.md` governs architectural permission, while current-master code/tests govern what is actually implemented and observed. Code must not silently supersede a locked architecture decision.

Historical snapshot warning: `ARK_X_Cinema_Current_State.txt` is a dated audit snapshot from 2026-08-26. It is historical evidence only, not current project state. Agents must not use it to override the active Project_Control records or current master code/tests.

## Project objective
ARK X Cinema is a $0/month, highly automated YouTube movie-recap production system. The core completion criterion is reliable end-to-end processing of one real 3–4 hour movie on the target Windows PC, producing a finished recap video that passes the required automated and human QA. Movie/source files must be legally obtained; no piracy or DRM bypass.

A fixed daily movie quota is not a project requirement. After one full-length movie is proven reliable, practical throughput is measured and optimized empirically from actual processing time, hardware capacity, RAM behavior, storage, workload characteristics, and other real constraints.

## Core architecture
Canonical flow:

1. Legal movie/source files
2. Subtitle/transcript ingestion when available
3. Separate Audio Description (AD) audio ingestion
4. AD audio → timestamped SRT using whisper.cpp
5. Canonical scene/timeline construction from subtitle + AD evidence
6. Bounded evidence packets
7. Evidence-first movie intelligence
8. Original recap script
9. Local TTS narration
10. FFmpeg-based video assembly
11. Automated/deterministic media QA
12. Human QA/approval
13. Upload preparation

AD is a separate audio asset. It is not assumed to be embedded in the movie and is not assumed to already be an SRT.

## Intelligence rules
The LLM must receive bounded evidence packets, not an unconstrained movie and a request to infer its plot. Claims must be traceable to supplied evidence. Unsupported facts must be marked unknown/unsupported. Preserve provenance: scene ID, timestamps, source, dialogue, visual/action evidence, and evidence limits.

## Resource constraints
The design target is a low-RAM Windows 11 laptop with approximately 7.65 GB usable physical RAM. Target additional RAM for an AI workload is approximately ≤2 GB. One heavy AI stage at a time is the default policy. Do not assume a model is suitable because its download size is small; real runtime RAM must be measured on the PC.

Preferred/free-first candidates include whisper.cpp, Ollama with a small local model, Piper/Kokoro for TTS, and FFmpeg. Do not lock a candidate into production until it is validated on the actual machine.

## Stage/checkpoint rules
Stages must be ordered and resumable. Preserve existing checkpoint/hash/state infrastructure. A stage must not be marked complete unless its required artifact exists and passes integrity validation. Failures must propagate clearly. Resume behavior must not silently rerun completed expensive work.

Do not replace or rewrite the existing production orchestrator, deterministic timeline engine, or other established architecture merely to make a new adapter fit. Reconcile against the actual current interfaces first.

## Testing truthfulness
Passing unit/CI tests prove code contracts only. They do NOT prove real Whisper.cpp, Ollama, TTS, FFmpeg, RAM limits, or end-to-end movie processing.

Never claim the project is end-to-end validated until a real 3–4 hour movie has successfully passed the pipeline on the target Windows machine and the resource constraints have been measured.

The primary validation milestone is:

- **Core completion:** 1 real 3–4 hour movie finished reliably end-to-end with required QA

Throughput milestones are secondary performance measurements, not completion gates. Record actual throughput only after core completion is proven.

## Verified vs unverified
Always distinguish:

VERIFIED IN REPOSITORY/CI:
- source architecture and code present
- automated test behavior that CI actually executed
- checkpoint/state behavior covered by tests

NOT VERIFIED UNTIL PC TESTING:
- actual whisper.cpp execution/performance
- actual Ollama/model inference/performance
- actual TTS engine performance/quality
- actual FFmpeg production rendering
- full 3–4 hour movie processing
- ≤2 GB additional AI RAM target
- end-to-end reliability on the target PC

## Multi-agent coordination
Before modifying anything, inspect current `master` and recent commits. Prefer small, reviewable changes. Add/update tests with behavior changes. Record unresolved issues in GitHub issues or project documentation when appropriate. Never hide failures by weakening tests or deleting evidence of a regression.

When another agent has already changed a component, reconcile with its current code rather than recreating or overwriting it.

## Permanent forensic audit protocol
A full repository audit must account for the entire repository, not only obvious application code. The audit must include repository structure, source, tests, configuration, scripts, CI/CD, GitHub configuration, project-control records, documentation, generated/state artifacts, historical/legacy material, and external integrations. Database/schema/migration and deployment material must also be inspected when applicable.

Do not silently ignore an item because it appears unused, obsolete, duplicated, generated, hidden, old, unrelated, or outside the main source directory. Determine its type, purpose, references, consumers, and relevance before classifying it. For binary, generated, cached, or extremely large artifacts, inspect metadata, references, generation mechanisms, consumers, and relevance with appropriate tooling instead of blindly consuming the entire contents.

A full audit must maintain an inspection ledger at `Project_Control/AUDIT_LEDGER.md`. The ledger must account for every repository directory and every important repository item and classify each as `INSPECTED`, `PARTIALLY INSPECTED`, `NOT APPLICABLE`, `UNVERIFIED`, or `BLOCKED`. A full audit must not be declared complete while significant items remain unaccounted for or unverified.

A full audit must reconstruct the actual system, not review files in isolation. Trace entry points, imports, callers, consumers, dependencies, data flow, control flow, configuration flow, APIs, persistence, external integrations, authentication, authorization, error handling, testing, build, and deployment as applicable.

Whenever a significant defect is discovered, search the repository for other occurrences of the same underlying defect pattern. Fix confirmed related instances when appropriate rather than treating the first occurrence as necessarily isolated.

Configuration is part of the software system. Cross-check environment variables, `.env`/example configuration, package scripts, build/test configuration, CI/CD, Docker/container configuration, deployment configuration, database configuration, and runtime configuration against the actual implementation.

A full audit must explicitly consider applicable security areas including secrets, credentials, authentication, authorization, input validation, injection, XSS, CSRF, SSRF, path traversal, command execution, unsafe file operations, sensitive-information leakage, dependency risks, CORS, session/cookie security, and privilege boundaries. Report only what can actually be verified.

## Root-cause repair protocol
When a confirmed defect is discovered:

1. Identify the symptom.
2. Reproduce it when possible.
3. Trace the relevant execution path.
4. Identify the root cause.
5. Search for related occurrences.
6. Implement the correct fix.
7. Update tests where appropriate.
8. Validate the fix.
9. Check its blast radius.
10. Re-check related functionality.

Do not substitute recommendations for actual fixes when repository modification access is available and the fix is safe within the established architecture.

## Changed-file blast-radius check
After significant modifications, inspect the changed file, its imports, callers, consumers, types/interfaces, tests, configuration, related implementations, and build/deployment implications. Search for assumptions affected by the change.

## Second audit after repair
A repair cycle is not complete immediately after tests pass. Use this sequence:

AUDIT
→ DISCOVER
→ ROOT-CAUSE ANALYSIS
→ FIX
→ TEST
→ RE-SCAN
→ CROSS-FILE REGRESSION AUDIT
→ TEST AGAIN
→ FINAL VERIFICATION

The second audit must specifically search for additional occurrences of discovered defect patterns, regressions, stale references, broken imports, interface mismatches, configuration inconsistencies, related security issues, and unintended architectural consequences.

## Autonomous fixing with architectural safety
Agents should automatically fix confirmed defects that can be safely fixed within the existing architecture. Do not silently overturn ARK X Cinema established or locked architectural decisions. If a defect cannot be correctly fixed without changing a locked decision, identify and document the conflict and escalate the architectural decision instead of silently replacing the architecture.

## Completion discipline
Do not add new architecture merely because a stage exists as an adapter. An adapter is not the same thing as a validated production implementation. The actual external/runtime integration must be explicitly verified before it is described as complete.

A full audit cannot be declared complete merely because the application builds, tests pass, obvious files were inspected, or major bugs were fixed. Before declaring completion, establish repository coverage, system understanding, findings, fixes, validation performed, remaining unknowns, environmental limitations, and unresolved issues. Do not claim 100% correctness, security, or bug-free status.

When reporting progress or audit completion, give the repository-backed state, what was actually inspected/tested, what was fixed, what remains unknown, and what must be tested on the Windows machine.
