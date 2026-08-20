# Evidence index

Immutable evidence references for production criteria. Statuses live in
[`readiness.json`](readiness.json). This index annotates what each artifact
actually demonstrates and, equally, what it does not.

## Existing evidence (pre-2026-08-20 baseline)

### Live testnet with distributed DKG (single-admin Docker fixture)

- Commit: `Jtensetti/nomad-testnet@80b9f5c83e30114f6f749a39b89a6d77638abe4c`
- CI: run `32301972409`; release `nomad-live-testnet-80b9f5c83e30`
- Demonstrates: three authenticated fixed-cadence UDP operators on a dedicated
  bridge (exact 1200-byte cells, strict pcap), signed topology consensus,
  Kyber v4 Pedersen DKG in three TLS processes with full-QUAL + unanimous
  activation certificate, distinct private shares in isolated share services,
  descriptor v2 certificate binding, live threshold decryption, networkless
  materializer, bounded immutable caches.
- Does NOT demonstrate: independent administration, WAN behavior, epoch
  rotation/retirement, key erasure, publication anonymity, browser engine
  isolation, independent review.
- Supports (PARTIAL): PROD-05, PROD-06, PROD-09..14, PROD-16, PROD-19
  (admission part), PROD-21, PROD-25.

### Prior testnet evidence chain

- `9b246eff` + run `32288962907`: live-fabric evidence, capture digest
  `630286a8...bb6e` (102 cells/sender, ~50ms cadence). PROD-11 PARTIAL.
- `2f3da0c4` + run `32293112716`: independent operator ceremony + local
  hop-key derivation; artifacts `9380245643`, `9380298465`.
- `d8b10887` + run `32300901150`: distributed DKG certified live path.

### Mix / crypto

- `Jtensetti/nomad-anytrust-mix-sim@35aa0f84`: verified Neff sequence shuffle
  composition (PROD-04, PROD-06 PARTIAL).
- `Jtensetti/nomad-anytrust-mix-sim@1f75bfb7`: authenticated Pedersen DKG
  ceremony (PROD-05 PARTIAL).

### Components

- `Jtensetti/nomad-constant-rate-fabric@872686c3`: fixed-cadence transport +
  wire observer (PROD-11 PARTIAL).
- `Jtensetti/nomad-rlnc@b395aa0b`: RLNC coding (PROD-12 PARTIAL; pollution
  resistance explicitly missing).
- `Jtensetti/nomad-semantic-basins@644bff28`: bounded loopback-only local
  embedding (PROD-14, PROD-24 PARTIAL).
- `Jtensetti/nomad-local-reconstruction@032f6f1a`: manifest-bound
  reconstruction (PROD-16 PARTIAL).

### Browser

- `Jtensetti/Nomad-browser@f5d1d6aa` + run `32287433817` + release
  `nomad-browser-macos-f5d1d6aa`: sandboxed networkless alpha (ad-hoc signed).
- `Jtensetti/Nomad-browser@b19710be` + runs `32303046813`, `32303046809`:
  protected fail-closed Developer ID/notarization workflow (uncredentialed),
  universal DMG verification. PROD-09, PROD-16, PROD-22, PROD-23, PROD-25,
  PROD-26 PARTIAL.

## New evidence (2026-08-20 onward)

### Baseline 2026-08-20

- All eight Go repos pass `go build`, `go vet`, `go test -race` at branch
  heads (local run, recorded in claude-progress.md).
- `scripts/check_docs.py` passes in nomad-protocol.

### Epoch lifecycle core (Workstream C, sprint C1)

- Implementation: `Jtensetti/nomad-testnet@2f2e3a6` (`live/epoch`).
- Security fixes after independent review: `@318845a`, `@0ad1e35`.
- Specification: `nomad-protocol/docs/EPOCH_LIFECYCLE.md`.
- Demonstrates: canonical binary encoding with published vectors that pin
  preimages, digests and real signatures from a published test key;
  descriptor chaining and approval quorum; activation by every operator;
  envelope-vs-active window validation; persisted fail-closed chain store
  with rollback rejection against a high-water mark, equivocation halt,
  emergency retirement and cross-process locking; enforced operator
  signature journal; 3-of-5 threshold profile negative tests.
- Does NOT demonstrate: automatic rotation (C-04), retired-share refusal
  at the share service (C-06), key erasure (C-08), revocation and recovery
  flows (C-09..C-11), forward-secrecy experiment (C-15), recovery drill
  (C-16), CI wiring (C-17), or any live/WAN integration.
- Review record: an internal evaluator confirmed five must-fix defects
  with working exploits, including an approval quorum satisfiable by a
  single previous-epoch operator on the 3-of-5 profile. All are fixed and
  carry regressions. This is internal QA, not an independent external
  audit, and does not satisfy PROD-04 or PROD-29.

### Publication ingress spike (Workstream A, DEC-008)

- Implementation: `Jtensetti/nomad-testnet@4dcefd7` (`live/publish`,
  `live/uplink`).
- Report: `nomad-protocol/docs/PUBLICATION_INGRESS.md`.
- Demonstrates, by measurement: the operator-to-operator cell profile
  separates work from cover perfectly under two independent passive
  classifiers (32/32 each), so it cannot carry publisher traffic; the
  uplink profile defeats both; the publication queue is bounded,
  crash-safe, idempotent, encrypted at rest, drains in content-derived
  order, and has no network capability (architectural test).
- Does NOT demonstrate: any wire capture of a running publisher, the
  deposit/mix/release path, retry or restart behavior, or cadence
  parameters. Cell indistinguishability is not publication anonymity.

### SiteID and publisher identity (Workstream D, sprint D1)

- Implementation: `Jtensetti/nomad-local-reconstruction@d572673` (`site`).
- Specification: `nomad-protocol/docs/SITE_IDENTITY.md`.
- Demonstrates: self-certifying SiteID derivation with published vectors;
  rotation by previous signing majority; recovery by offline threshold
  with mandatory revocation of the compromised set; absorbing revocation;
  rollback rejection; equivocation with an independently verifiable proof;
  four distinct identity states; strict parsing that rejects duplicate
  JSON keys, unknown fields, trailing data, non-canonical hex and non-UTC
  times.
- Does NOT demonstrate: browser integration (D-09), capture evidence for
  query-independent resolution (D-10), or a second independent
  implementation (EB-5). Not yet independently reviewed.
