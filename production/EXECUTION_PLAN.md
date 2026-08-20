# Execution plan: Nomad production readiness

Derived from [`GOAL.md`](GOAL.md). Requirement registry:
[`workstreams.json`](workstreams.json). Progress journal:
[`claude-progress.md`](claude-progress.md).

## Baseline (2026-08-20)

All eight Go repositories pass `go build ./...`, `go vet ./...` and
`go test -race ./...` at their current branch heads.
`python3 scripts/check_docs.py` passes in nomad-protocol. Registry state:
0/30 MET, 17 PARTIAL, 12 NOT_MET, 1 BLOCKED (PROD-29).

Existing hard-won assets to preserve, not rewrite:

- nomad-testnet `live/`: signed topology ceremony, Kyber v4 Pedersen DKG over
  TLS with journaled fail-closed semantics (DKG-01..12 MET at fixture level),
  isolated share services, networkless materializer, strict pcap gate.
- nomad-anytrust-mix-sim: ElGamal batches + verified Neff sequence shuffles.
- Nomad-browser: sandboxed networkless SwiftUI client, egress gates, protected
  fail-closed notarization workflow (uncredentialed).
- Selection Firewall dependency gates in CI.

## Phase plan

### Phase 1 — Protocol foundations (C -> D -> A)

**C. Epoch/key lifecycle** (largest structural change, everything depends on
it). Introduce a canonical `EpochDescriptor` v1 that generalizes today's
signed topology + DKG certificate into a lifecycle: PREPARING -> READY ->
ACTIVE -> RETIRED, with public activation boundaries, previous-epoch chaining,
retired-share rejection, key erasure, operator replacement/revocation flows
and forward-secrecy evidence. Extend, do not replace, the existing ceremony
code. New domain strings are versioned; existing evidence stays valid for the
fixture claims it made.

**D. SiteID/publisher identity.** New canonical SiteDescriptor chain with
domain-separated SiteID derivation, rotation/recovery/revocation, rollback
prevention and equivocation handling; integrate verification into
nomad-local-reconstruction and Nomad-browser identity display states.

**A. Publication airlock.** Local-only Publish -> bounded persistent queue ->
constant-rate injection through existing cells -> anytrust mix -> threshold
deposit mailbox -> public release epochs -> replication. Capability split
enforced architecturally (package graph + process boundary), covered by
Selection Firewall CI gates, verified by two-world captures with preregistered
tolerances.

### Phase 2 — Hostile network (B + G in parallel)

**B.** Operator lifecycle tooling (init/enroll/verify/join/rotate/recover),
five-operator 3-of-5 profile, governance-as-protocol transitions, WAN-ready
deployment package, external operator onboarding package. Real administrative
independence is BLOCKED externally; everything up to that boundary ships.

**G.** Pollution-resistant symbol admission (established homomorphic-hash
style construction), hard per-generation resource bounds, Byzantine
campaigns, admission/rate model, eclipse/amplification/disk-full/OOM tests,
backpressure non-interference.

### Phase 3 — Prove the network (E)

netem loss/latency/jitter/congestion matrix, suspend/clock/stall campaigns,
NAT/IPv6 profiles, blind two-world classification with a separate evaluator
and preregistered thresholds, validated 72-hour harness, intersection
analysis. Real multi-region WAN runs are BLOCKED on infrastructure; the
harness, local campaigns and exact deployment procedure ship.

### Phase 4 — Shippable client (F + H)

**F.** Atomic handoff hardening (symlink/traversal/partial-write/oversize
negative tests), query-isolation proofs, DNS/packet negative captures of the
built browser binary in CI, engine-fork contract status honestly documented.

**H.** Reproducible dual builds, SBOM, SLSA-style provenance, vulnerability
gate + policy, updater design (authenticated, anti-rollback, fail-closed),
Keychain-backed key storage, uninstall tests, allowlisted logging. Apple
signing/notarization remains a credentialed external step with an exact
handoff.

### Phase 5 — Stabilize

Protocol freeze + conformance vectors (PROD-01), claim-to-test matrix
completion (PROD-02), accountability (PROD-07), telemetry privacy (PROD-27),
SLO/soak/incident scaffolding (PROD-28), wire-format change freeze.

### Phase 6 — Independent validation (I)

Complete audit package; external crypto/systems/browser/privacy assessments,
red team, beta, two-person release decision. All externally independent items
remain BLOCKED until real external parties act; the package makes their work
immediately executable.

## Working rules

- Sprint contract before each substantial security-sensitive unit; separate
  evaluator agent challenges contracts touching privacy/crypto claims.
- Negative/adversarial tests written before implementation where the threat
  is clear.
- Every completed unit updates workstreams.json, EVIDENCE_INDEX.md and, when
  a PROD gate status changes, readiness.json + the DoD table together (CI
  enforces consistency).
- No parallel conflicting protocol definitions: epoch/SiteID/airlock wire
  formats are defined in nomad-protocol docs first, then implemented.
