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

## Checkpoint: airlock built, reviewed, and remediated

**Workstream A (publication airlock)** — built the deposit boundary that the
claim matrix previously carried with no evidence at all: a public release
schedule, a fixed-size batch padded with real committee cover, a shuffle chain
authenticated to the certified committee, and per-column threshold release.

An adversarial review under the evaluator-separation rule found **four Sev1 and
three Sev2 defects, each with a working exploit**, in code whose own tests were
green. All seven are now fixed with a regression each:

1. Shuffle rounds were unauthenticated — a party holding no committee share
   forged the entire "certified" chain and knew the whole ingress-to-egress
   map. The anytrust assumption inverted.
2. A chain that never re-randomised verified; the map was readable off the
   bytes.
3. Wire padding identified every cover column before any decryption. The
   existing tests missed it by slicing comparisons to `[:DepositSize]`.
4. `Seal` ran in time linear in the number of *empty* slots, reading out
   publication volume at 190x, remotely observable by a concurrent depositor.
5. Nothing bound a chain to an epoch, committee or batch; whole chains replayed.
6. One malformed or poisoned deposit destroyed the epoch for every publisher.
7. `ErrEpochFull` was an exact occupancy oracle, and the deposit-ID namespace
   was unauthenticated (membership oracle plus targeted squatting).

**Two claims were retracted, not amended**, because the review invalidated
them: "a partial or reordered chain is refused" and "one operator cannot link
ingress to release". The second is the sharper lesson — the unlinkability
*measurement* passed against a chain with zero anonymity, because a
byte-similarity matcher scores chance whenever re-randomisation happens
regardless of whether the permutation hides anything. It was rebuilt to
measure permutation uniformity instead.

**Workstream E** — the preregistered two-world rule is now executable with
both-direction self-tests in CI, plus a wire-level campaign against the
production node. Two defects found while building it, both of which made the
tooling agree that two worlds matched when they did not: a KS walk that charged
tied values as ECDF gaps (a sample against itself scored p=9e-35 on exactly the
quantized inter-arrivals a fixed-cadence capture produces), and a capture regex
that silently skipped VLAN-tagged packets, shared with a live CI gate.

**Workstream G** — amplification measured at 0.0003–0.0008 under floods of up
to 396 MB, with cadence unaffected, and a check that the flood is not a
private-state oracle.

**Workstream F** — the missing F-07 negative test, plus two non-exploitable
defects it surfaced: the renderer URL gate and the local adapter disagreed on
what a resource path may be, and the gate admitted scriptable `data:` URLs.

**Process finding:** `components/nomad-anytrust-mix-sim` inside nomad-testnet
has diverged from its standalone repository in both directions. A security fix
made in the standalone repo would not reach what ships. Fixes landed in both;
reconciling the vendoring is outstanding.

Still **0 of 30 PROD gates MET**. Three adversarial reviews have now each found
exploitable defects in finished-looking code, which is the strongest available
argument against promoting any gate on internal confidence.

## Checkpoint 2026-08-21: multi-region WAN campaign

Six campaigns on real hosts in fr-par-1 (FR), nl-ams-1 (NL) and pl-waw-1 (PL),
1200-byte cells at 50 ms in a signed ring. All six deployments verified
destroyed by direct API query; the campaign buckets keep results only, staged
key material removed.

**The measurement.** Runs 5 and 6 are controlled (two idle series plus one
active, order rotated so exactly one host is active per position) and
synchronised on shared absolute world boundaries. Across those two runs, 18
comparisons at a registered alpha of 0.01, no treatment pair was rejected. Cell
counts were exactly equal within every pair on every host, and mean
inter-arrival drift stayed at 1e-6 to 1e-7 of the cadence against a 2e-2
tolerance. The single rejection landed on a *control* pair -- two idle worlds,
where a leak is impossible by construction.

**Four instrument defects, found in order, each hiding the next.**

1. The analysis pooled every packet in a capture into one series, when the
   preregistration extracts features per direction and per peer. A capture
   holds the host's emissions and its peers' arrivals, and restarting the node
   re-randomises their relative phase, so pooled it rejects whatever the node
   does. It rejected all three hosts. PREREGISTRATION v2 writes the sample
   definition down and voids that run; no threshold changed.
2. The in-process campaign wrote one file per series spanning four rounds, with
   multi-second pauses inside it where the other worlds ran. The rule compares
   equal-length windows of a continuous stream. Captures are now per round, and
   with that fixed the campaign's own controls pass (KS p=0.62, 0.95, 0.95)
   while the treatment is still rejected in two of three evaluable rounds --
   the E-08 finding survives a correct instrument and a passing control.
3. The CI gate accumulated each comparison's exit status and then ended the
   step without consulting it. It had been reporting green while the rule
   rejected its own idle-versus-idle control. It now fails on a finding, fails
   when nothing was compared, and keeps "could not run" distinct from a
   verdict.
4. The WAN campaign had no negative control at all, so its first verdict --
   one host rejected at KS p=0.00988 -- could not be interpreted. Adding the
   control is what made run 5's operator-a result readable as noise floor
   rather than as a leak.

**A fifth defect was the node being right.** The first run captured zero
packets on all three hosts because `curl` wrote the operator secret at the
inherited umask and `nomad-node` refuses a group-readable secret. The check was
correct; the payload was wrong.

**Boundary.** One administrator, one provider, one account. Three geographic
failure domains, one administrative. This is not evidence of independent
operation and does not support PROD-05 or PROD-21. One run per host against a
registered screening design of 30 captures per world is a single screening
sample, not the screening.

E-01 moves BLOCKED to PARTIAL; E-02, E-06 and E-11 stay PARTIAL with WAN
evidence attached. Still **0 of 30 PROD gates MET**. Nothing here promotes a
gate, and PROD-28's 30-day soak is untouched.

## Checkpoint 2026-08-21b: defects, gates, and what a freeze needs

**Three defects found and fixed, each of which had passing tests around it.**

1. *A silent wrong-decode on the production path.* A flaky RLNC round-trip
   test (~1 run in 14) was a real defect: `Decoder.Add` inserted a symbol
   without reducing it against pivots discovered at later columns, after which
   the basis reported full rank and `Decode` returned a mixture of source
   symbols as one symbol, with a nil error. The materializer uses this decoder.
2. *A duplicate JSON key accepted in a signed topology.* Go keeps the last
   occurrence; other parsers keep the first. A signature cannot catch it, since
   each implementation verifies against whatever it parsed, so one accepts a
   document another refuses. Refused outright now.
3. *A replayable stale topology.* A signature and an unexpired window do not
   make a topology current, and nothing remembered which epoch had been
   served. A persisted watermark now refuses to move backwards.

**The structural defect was worse than any of them.** `components/*` in
nomad-testnet and the pinned snapshots in Nomad-browser are separate modules
behind replace directives, invisible to `go test ./...`, and none of the nine
carried a single test file. What ships was untested by the repository that
ships it. All nine now carry their standalone suites and are gated in CI.

**A control that did nothing.** `debug.SetTraceback("none")` reads like it
turns off crash dumps and does not: measured on two Go versions, a process
calling it still prints goroutine stacks with frame arguments as raw machine
words. Only `GOTRACEBACK=none` works, and the runtime reads it at startup, so
it is a deployment control the program can verify but not impose. Setting it on
the compose anchor was not enough either -- a YAML merge key replaces a mapping
rather than deep-merging it, so the three DKG services silently dropped it.

**Gates: 0/30 to 2/30, with five more moved off NOT_MET.** PROD-08 and PROD-12
are MET. PROD-01, PROD-16, PROD-19, PROD-20 and PROD-27 moved to PARTIAL with
specific blockers rather than general ones. The promotions rest on external
test reports, which the evidence rule permits in the same clause as Actions --
an earlier reading that the outage capped every promotion was wrong.

**What a freeze still needs.** The formats are published and enforced: nine
golden vectors identical on 32-bit and 64-bit, a compatibility matrix covering
57 frozen labels that a test keeps honest, and the downgrade rule written down.
What is missing is a signature over it (EB-7, a custody problem), one normative
document for state transitions and timeouts, and a schema a second
implementation could validate against.

**Not promoted, deliberately.** PROD-02 and PROD-27 both need a review, and I
wrote the artifacts under review in each case. A maintainer who did not write
them can close either with no external dependency; the implementer must not be
the only judge of its own change.

## Checkpoint 2026-08-21c: what is left, and why

Gates: **2 MET, 22 PARTIAL, 5 NOT_MET, 1 BLOCKED**, from 0/30 with 18 PARTIAL
and 11 NOT_MET at the start of the day. Six criteria moved off NOT_MET
(PROD-01, 07, 15, 16, 20, 27), two were promoted (PROD-08, PROD-12).

Work landed since the previous checkpoint:

- **Fault attribution** (PROD-07). A mixer's receipt already signed context,
  input, output and proof digests together; nothing used it. `AttributeFault`
  names the signer of an unsound round and `VerifyFaultReport` re-derives the
  fault so a third party confirms it rather than trusting the reporter. Three
  of the four fault kinds are deliberately *not* attributable, because
  attributing them would let one mixer frame another.
- **Site recovery drill** (PROD-15), and SITE_IDENTITY promoted to normative
  v1. Writing the drill corrected a wrong expectation: recovery invalidates
  the compromised key's back catalogue by design, which rotation does not, and
  the specification says so.
- **Compatibility matrix** (PROD-01), 57 frozen labels, enforced by a test
  that fails naming any version constant the matrix omits. Writing it settled
  the downgrade rule, which had been implicit in the code.
- **Crash-output control** (PROD-27), after finding the obvious in-process fix
  measurably does nothing.

**The five NOT_MET, and what each actually needs.** PROD-03 needs a second
implementer (EB-5). PROD-30 needs a second release approver and a monitored
beta (EB-6). PROD-28 needs thirty days to pass. PROD-17 and PROD-18 need the
distributed deposit path, which is the one substantial piece of engineering
left in this list; PROD-07's live fault-injection blocker and PROD-18's
multi-publisher capture both sit behind it.

**Two gates are held by a second party rather than an external one.** PROD-02
and PROD-27 each need a review, and in both cases this session wrote the
artifact under review. A maintainer who did not write them can close either
with no external dependency at all. Recording that distinction matters,
because it is the difference between "waiting on the world" and "waiting on a
second pair of eyes in this project".

**30/30 is not reachable from here.** PROD-28 alone puts it at least thirty
days out, and four more gates need people this session cannot be. What is
reachable is that every gate is honestly marked with a specific blocker rather
than a general one, and that is now true of all thirty.

## Checkpoint 2026-08-21d: the deposit path, and the end of achievable NOT_MET

**Publication had no distributed form.** The queue held encrypted fragments,
the uplink could seal work and cover indistinguishably, the airlock could
accept deposits and seal a batch — and nothing called `Queue.Next` or
`Airlock.Deposit`. The sizes had been designed to fit and had never met: a
fragment is 504 bytes, exactly one uplink payload and one mix plaintext; the
uplink's inner layer is 1152 bytes, exactly one airlock deposit.

`live/deposit` joins them. The design point is what the drain does *not* do:
call the queue on the cadence tick. An empty queue costs one directory read
and a non-empty one costs a read, a decrypt, an unlink and a sync, and that
difference is publication timing. A filling goroutine holds a one-slot buffer;
the tick does a non-blocking receive and touches no disk.

**Two instrument defects caught before they became evidence.**

The correlation experiment's first positive control was an unshuffled airlock
batch, and it scored chance — which looked exactly like the unlinkability
measurement this project withdrew earlier, and was in fact the airlock
working: `Seal` orders by deposit ID and randomises placement, destroying
arrival order before any mixer touches the batch. The control was rebuilt with
no defence at all, where the matcher recovers the mapping at 1.00.

The publication campaign's first version synthesised each packet's timestamp
as base plus tick times interval. Every capture was then perfectly regular by
construction and the preregistered rule reported KS p=1.0 on all five pairs —
a fabricated agreement that would have been filed as evidence of timing
indistinguishability.

**A refusal worth recording.** With real timestamps the campaign's own control
fails: two idle publishers differ in mean inter-arrival by 0.003 to 0.520 of
the nominal interval across five runs, against a 0.02 tolerance. The campaign
therefore judges cell count, size and destination — which are exact — and
explicitly declines to judge timing, while still measuring the floor every run
so the refusal stays a finding rather than an assumption.

**Gates: 2 MET, 24 PARTIAL, 3 NOT_MET, 1 BLOCKED.** The three NOT_MET are
PROD-03 (a second implementer), PROD-28 (thirty days) and PROD-30 (a monitored
beta and a second approver); PROD-29 is BLOCKED on an external assessor. No
gate whose remaining work this project could do is still NOT_MET.

That is a statement about NOT_MET, not about readiness. Twenty-four criteria
are PARTIAL and their blockers are now specific rather than general: no
independent review anywhere, no distributed correlation experiment, no
descriptor distribution, no economic analysis, no availability claim under
sustained flood, and no measurement of long-horizon correlation at all.
