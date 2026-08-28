# ARK X CINEMA — FORENSIC AUDIT LEDGER

**Purpose:** Permanent mechanism for tracking coverage and uncertainty during full repository audits.

**Authority:** This ledger supplements `AGENTS.md` and the existing Project_Control system. It does not replace or weaken any existing project rule.

## Status values

- `INSPECTED` — contents/behavior reviewed sufficiently for the audit scope.
- `PARTIALLY INSPECTED` — some relevant material reviewed, but meaningful coverage remains.
- `NOT APPLICABLE` — category does not apply to this repository/component, with a recorded reason.
- `UNVERIFIED` — evidence is insufficient to establish the required fact.
- `BLOCKED` — inspection could not be completed because of an access/tool/environment limitation.

## Required audit coverage

A full audit must account for:

- every repository directory
- every important repository file
- source code and entry points
- tests and fixtures
- configuration and environment files
- dependency manifests and lockfiles
- scripts and launchers
- CI/CD and GitHub configuration
- deployment/container infrastructure
- Project_Control records
- documentation
- generated/state artifacts
- historical/backups/legacy artifacts
- external integrations
- database/schema/migration material when applicable
- security-sensitive surfaces

## Ledger record

For every directory or important item, record at minimum:

| Path / area | Type | Status | Purpose / role | Key references / consumers | Tests / evidence | Findings / risk | Fixed? | Verification notes |
|---|---|---|---|---|---|---|---|---|

## System reconstruction record

Every full audit should also record the verified paths for:

- Entry points:
- Control flow:
- Data flow:
- Configuration flow:
- External integrations:
- Persistence/state:
- Error propagation:
- Build/test path:
- Deployment/launcher path:
- Security boundaries:

## Defect propagation record

For every significant defect:

| Defect pattern | Initial location | Repository-wide search performed? | Related occurrences | Fixes applied | Regression checks | Final status |
|---|---|---|---|---|---|---|

## Repair cycle

Use and record this sequence for significant repair work:

`AUDIT → DISCOVER → ROOT-CAUSE ANALYSIS → FIX → TEST → RE-SCAN → CROSS-FILE REGRESSION AUDIT → TEST AGAIN → FINAL VERIFICATION`

## Completion gate

A full audit may be marked complete only when:

- repository coverage is accounted for;
- significant items are not silently skipped;
- important system relationships are reconstructed;
- confirmed defects have been repaired or explicitly documented as unresolved;
- significant defect patterns have been searched repository-wide;
- changed-file blast radius has been checked;
- configuration and security surfaces have been reviewed as applicable;
- post-repair re-scan and regression validation are complete;
- remaining `UNVERIFIED` and `BLOCKED` items are explicitly listed;
- no claim of universal correctness, security, or bug-free status is made.

## Use during every future full audit

The ledger is an audit instrument, not a project status substitute. Project status remains governed by `PROJECT_STATE.md`, `CURRENT_TASK.md`, `DECISIONS.md`, `IMPLEMENTATION_STATUS.md`, `MULTI_AI_STATUS.md`, and verified GitHub/PC evidence as applicable.
