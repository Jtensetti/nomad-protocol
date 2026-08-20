# Progress journal

Newest first. Each checkpoint: completed work, commits, evidence, risks, next
priority, blockers.

## 2026-08-20 — C1 implemented and hardened; D1 implemented; A spike done

**Completed**

- **Workstream C sprint C1** (`nomad-testnet/live/epoch`): EpochDescriptor
  v1 wrapping the unchanged topology v3 and DKG certificate, canonical
  binary encoding with published vectors, chained approval quorum,
  activation signatures, envelope-vs-active windows, persisted fail-closed
  chain store, enforced signature journal, 3-of-5 profile tests.
- **Independent review of C1 found five must-fix defects, each with a
  working exploit.** The most serious: `Approval.Index` was narrowed to
  uint16 for lookup but deduplicated on the full uint32, and the approval
  message bound nothing about the approver, so ONE previous-epoch operator
  could mint a full 3-of-5 quorum and force a membership change alone.
  Also: the equivocation halt failed open on any persistence error; the
  signature journal was implemented but unreachable; revocation was applied
  retroactively and bricked the store exactly when recovery was needed; and
  `Append` returned success for bytes `Verify` rejects. All fixed with
  regressions (`318845a`), plus cross-process locking (`0ad1e35`).
- **Workstream D sprint D1** (`nomad-local-reconstruction/site`):
  self-certifying SiteID, rotation/recovery/revocation with offline
  recovery authority, rollback and equivocation handling, four identity
  states, strict parsing. Spec in `docs/SITE_IDENTITY.md`. Not yet
  independently reviewed.
- **Workstream A ingress spike** (`live/publish`, `live/uplink`): measured
  that the current operator cell profile leaks work-vs-cover perfectly
  under two independent classifiers, so it cannot carry publisher traffic;
  built and tested an uplink profile that defeats both, where cover is a
  real committee encryption on the identical code path so the entry
  operator cannot distinguish it either. Report in
  `docs/PUBLICATION_INGRESS.md`.

**Risks discovered**

- The cleartext hop header (work flag, stream ID, batch coordinates) is a
  publisher-traffic blocker and should be reviewed for what it reveals
  about operator relay patterns over long horizons, even though it does
  not break the reader claim.
- Publication cover cells must be mixed and threshold decrypted like real
  ones; that cost is accepted but affects capacity planning.

**Next priority** Workstream C sprint C2: revocation statements, key
erasure with the forward-secrecy experiment, retired-share refusal, and
automatic rotation; then re-review C before any MET claim.

**External blockers** unchanged (EB-1..EB-6).

## 2026-08-20 — Evaluator critique incorporated; C1 ready

**Completed**

- Independent evaluator agent reviewed the execution plan against the actual
  code (17 findings). All must-fix findings incorporated:
  - envelope-vs-active-window semantics resolve prepare-while-active without
    a topology v3 schema break (DEC-004);
  - canonical binary encoding for all new signed objects; existing objects
    frozen and embedded by exact bytes, so no digest cascade (DEC-005);
  - membership transition defined once, in C (DEC-006);
  - public rotation-failure policy incl. Pedersen abort/bias note (DEC-007);
  - publication ingress spike scheduled before descriptor freeze; client
    uplink + online distributed mix registered as new protocol surface
    (A-14, A-15; DEC-008);
  - single two-world harness rule (DEC-009);
  - registry corrections: baseline count fixed (18 PARTIAL/11 NOT_MET),
    C-01/C-07 notes corrected, A-11 downgraded to NOT_STARTED, G-13 evidence
    cited, workstream M added (PROD-01/02/03/28), B-13 accountability,
    E-12 durability, F-12 semantic-service rows added. 118 requirements now
    tracked.
- Spec revised: `docs/EPOCH_LIFECYCLE.md` (draft v1) and sprint contract
  `production/sprints/C1.md`.
- Deep code audit of topology/DKG/committee/threshold/hop/rawcache stack:
  epoch/context binding at the crypto layer is strong (recorded in C-03).

**Next priority** Implement sprint C1 (epoch descriptor, canonical binary
encoding, chain store, state machine core, vectors, negative tests) in
nomad-testnet `live/epoch`.

**External blockers** unchanged (EB-1..EB-6); user should initiate EB-1,
EB-2, EB-4 now — they are wall-clock bound and independent of engineering.

## 2026-08-20 — Session start: artifacts + baseline

**Completed**

- Committed authoritative goal as `production/GOAL.md`.
- Created persistent artifacts: `CLAUDE.md`, `production/EXECUTION_PLAN.md`,
  `production/workstreams.json` (all GOAL requirements + PROD ownership map,
  honest initial states), `production/CLAIM_TEST_MATRIX.md`,
  `production/EVIDENCE_INDEX.md`, `production/DECISIONS.md`,
  `production/EXTERNAL_BLOCKERS.md` (EB-1..EB-6).
- Baseline: all eight Go repos green on `go build`, `go vet`,
  `go test -race`; `scripts/check_docs.py` passes. No pre-existing failures
  to record.

**Registry state** 0/30 MET, 18 PARTIAL, 11 NOT_MET, 1 BLOCKED (PROD-29).

**Risks discovered**

- Mix proofs bind key+batch digests but epoch/committee binding of the mix
  layer needs audit (C-03).
- Fixture threshold semantics: DKG requires full QUAL of all three operators;
  production 3-of-5 profile with t<n rotation is unbuilt.
- RLNC pollution is a known unmitigated resource-exhaustion vector (G).

**Next priority** Evaluator critique of the execution plan, then Workstream C
(epoch/key lifecycle) sprint 1: canonical EpochDescriptor + lifecycle state
machine spec and vectors.

**External blockers** EB-1 (Apple credentials), EB-2 (independent operators),
EB-3 (WAN infra), EB-4 (assessors/red team), EB-5 (second implementation),
EB-6 (second release approver). Details in EXTERNAL_BLOCKERS.md.
