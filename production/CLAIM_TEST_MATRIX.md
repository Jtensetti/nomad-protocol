# Claim-to-test matrix

Maps every security claim to the tests/evidence that exercise it at the
claimed boundary, and states the boundary explicitly. A claim without a
boundary-level test row is not evidenced. Feeds PROD-02.

Levels: `unit` (in-process), `integration` (composed processes, loopback or
Compose), `boundary` (real interface/process/release artifact), `independent`
(external assessor).

## Reader path

| Claim | Boundary required | Current tests/evidence | Level reached |
|---|---|---|---|
| Emission plan depends only on public inputs | planner API + package graph | selection-firewall unit tests; Selection Firewall CI dependency gates | integration |
| Wire cells are exactly 1200 bytes at fixed cadence | real interface | testnet Compose pcap gate (run 32301972409) | boundary (single-host) |
| Lost cells never cause catch-up bursts | real interface under loss/suspension | scheduler unit tests only | unit |
| Private reader activity does not change wire behavior | real interface, two worlds, blind | loopback two-world regression (not blind, not WAN) | integration |
| Cache maintenance independent of reads | wire trace comparison | design + code structure only | unit |

## Mix and committee

| Claim | Boundary required | Current tests/evidence | Level reached |
|---|---|---|---|
| Shuffle preserves payload multiset | crypto vectors | mix-sim tests | unit |
| Tampered shuffle output rejected | negative proof tests | mix-sim tests | unit |
| Proof bound to key + input/output batch digests | vectors + negative tests | mix-sim tests | unit |
| DKG fails closed (partial membership, equivocation, late, resume) | multi-process TLS ceremony | testnet DKG-01..12 evidence | integration |
| No machine holds a complete decryption key | process + host separation | Compose share isolation (single host) | integration |
| Epoch rotation/retirement/erasure | lifecycle tests + drills | none | none |
| Cross-epoch transplant rejected (proofs, shares, sessions, attestations) | negative tests per object | DKG packets only | unit |

## Objects and identity

| Claim | Boundary required | Current tests/evidence | Level reached |
|---|---|---|---|
| Object accepted only with exact length/root/signature chain | reconstruction tests | local-reconstruction tests | unit |
| Manifest self-authenticates to embedded key | vectors | local-reconstruction tests | unit |
| Publisher identity (SiteID) valid for intended site | full descriptor-chain verification | none (PROD-15) | none |
| Rollback to superseded descriptor rejected | negative tests | none | none |
| Equivocating site histories detected | split-view tests | none | none |

## Publication

| Claim | Boundary required | Current tests/evidence | Level reached |
|---|---|---|---|
| Publish is a purely local operation | package graph + process boundary | none (fixture publisher only) | none |
| Publish/no-publish wire equivalence | blind two-world capture | none | none |
| Failed publication adds no traffic | capture under failure | none | none |
| Single operator cannot link ingress to plaintext | threshold + mix composition tests | none | none |

## Browser and release

| Claim | Boundary required | Current tests/evidence | Level reached |
|---|---|---|---|
| Browser has no network entitlement | release binary inspection | CI entitlement gates (build) | integration |
| Zero browser egress incl. DNS | packet/DNS capture of release binary | none | none |
| Browser renders only verified materialized objects | filesystem boundary tests | unit tests + process gate | integration |
| Partial write/symlink/traversal rejected | adversarial filesystem tests | none explicit | none |
| Release reproducible | two independent builds | none | none |
| Update cannot roll back | updater tests | none (no updater) | none |

## RLNC and resources

| Claim | Boundary required | Current tests/evidence | Level reached |
|---|---|---|---|
| Inconsistent dependent symbol rejected | unit tests | rlnc tests | unit |
| Malicious innovative symbols bounded (CPU/mem) | Byzantine campaign | none (known gap) | none |
| Queues/caches bounded under attack | load/OOM/disk-full tests | bounded-cache unit tests | unit |
| Backpressure does not alter private-sensitive cadence | wire trace under load | none | none |
