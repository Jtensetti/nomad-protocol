# Decision log

Engineering decisions with rationale. Newest first.

## DEC-003 (2026-08-20): Epoch lifecycle extends the existing ceremony stack

Workstream C will generalize nomad-testnet's signed topology + DKG certificate
into a canonical EpochDescriptor and lifecycle state machine rather than
replacing the ceremony code. Rationale: DKG-01..12 are proven fail-closed at
fixture level with immutable evidence; rewriting would discard evidence and
risk regressions. New wire objects get new versioned domain strings; existing
domains keep their meaning.

## DEC-002 (2026-08-20): Execution artifacts live in nomad-protocol/production

workstreams.json is the requirement registry for GOAL.md; readiness.json
remains the sole authority for PROD gate status (CI-enforced against the DoD
table). workstreams.json never duplicates PROD statuses, only ownership
mapping, to avoid dual-source drift.

## DEC-001 (2026-08-20): Full goal text committed as production/GOAL.md

The complete production goal is versioned in-repo and referenced by the
session goal condition, so any future session recovers the full requirement
set from the repository alone.
