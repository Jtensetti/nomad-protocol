# Nomad production status

Last updated: 2026-08-20. Authoritative gate statuses live in
[`production/readiness.json`](production/readiness.json); this document
explains them in prose. Where the two disagree, the registry wins.

**Nomad is not production ready.** 0 of 30 production gates are MET. This
document says what exists, what it is evidenced to do, and what it does not
do.

## What is Nomad now?

A research-grade anonymity network with a substantially complete protocol
core and no production deployment. Concretely:

- **A working reader path.** Fixed-cadence 1200-byte UDP cells whose
  emission schedule is a pure function of public inputs, an anytrust mix
  with verified Neff sequence shuffles, threshold decryption by a committee
  created through authenticated Pedersen DKG, bounded immutable caches, and
  a networkless materializer that hands verified objects to a sandboxed
  macOS browser with no network entitlement.
- **A complete epoch and key lifecycle** (Workstream C): canonical
  descriptors with published vectors, chained membership transitions
  authorized by a quorum of the previous committee, automatic rotation on a
  public schedule, retirement, key erasure with a forward-secrecy
  experiment, revocation, and a recovery drill that runs in CI.
- **A publisher identity system** (Workstream D): self-certifying SiteIDs,
  rotation, offline recovery authority, rollback and equivocation handling,
  and four explicit client identity states.
- **The local half of a publication airlock** (Workstream A): a bounded,
  encrypted, crash-safe publication queue with no network capability, and an
  uplink cell format in which work and cover are indistinguishable to both a
  network observer and the entry operator.
- **Bounded network coding** (Workstream G): enforced per-generation CPU,
  memory, byte, symbol and lifetime budgets, with pre-admission verification
  of systematic symbols.

## What privacy claims are evidenced?

Only these, and only at the level stated:

| Claim | Level reached |
|---|---|
| The public emission plan takes no private input | structural (API shape + CI dependency gates) |
| Cells are exactly 1200 bytes at fixed cadence | boundary, single host (Compose pcap) |
| Objects are accepted only on exact hash and signature | unit + integration |
| One operator cannot decrypt alone | integration, single host |
| Epoch lifecycle fails closed on split-brain, rollback, replay | unit + adversarial, protocol level |
| Publisher identity survives rotation; theft of a signing key does not confer recovery authority | unit + adversarial, protocol level |
| Publish cannot reach a socket, transport or scheduler | structural (transitive CI gate) |
| Uplink work and cover are byte-indistinguishable | measured, cell level |
| A malicious symbol cannot cost more than the generation budget | measured, Byzantine campaign |

## Against which threat model?

[`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md). The adversary may observe
links globally, run many intermediate nodes, correlate over time, and drop,
delay, replay or inject around an honest mixing boundary. It cannot break
standard primitives. **Participation is visible**: the model protects which
object an endpoint is reading or publishing, not whether it uses Nomad.

## What assumptions remain?

- **Anytrust.** At least one relevant mixer permutes and re-randomizes
  honestly. Nothing detects a fully colluding committee.
- **Threshold custody.** Fewer than `t` operators are compromised at once.
- **Out-of-band SiteID distribution.** A user given the wrong SiteID
  verifies the wrong site correctly.
- **Endpoint security.** A compromised OS, malware in the browser domain, or
  seizure of plaintext is outside the claim.
- **Erasure substrate.** Key erasure guarantees file destruction within an
  encrypted volume, not physical media destruction.

## What is NOT protected?

- **Publication anonymity.** The airlock is incomplete. The deposit,
  distributed mixing, threshold release and time separation are not built.
  Cell indistinguishability is one necessary piece, not the property.
- **Availability against a sustained polluter.** Bounds stop resource
  exhaustion; at 50% or more malicious symbols a generation still fails to
  complete.
- **Sybil, eclipse and amplification.** No admission or rate-control model
  exists (G-05..G-09).
- **Anything at WAN scale.** All network evidence is single-host. There are
  no multi-region, loss, congestion, NAT, IPv6, suspend/resume or
  clock-drift results, and no blind two-world classification.
- **Browser egress at the binary level.** The release binary has never been
  packet- or DNS-captured, and the engine forks carry integration contracts
  only.
- **Anything about the shipped artifact.** No notarized build, no
  reproducibility, no SBOM, no provenance, no updater.
- **Long-horizon correlation.** No intersection analysis, no 72-hour
  captures, no soak.

## Which PROD criteria are MET?

**None.** 0/30. The registry currently holds 18 PARTIAL, 11 NOT_MET and 1
BLOCKED. Substantial protocol work has moved several criteria forward
internally, but none has the boundary-level evidence its own rule demands,
so none has been promoted. Two reviews during this work each found
exploitable defects in code that looked finished — a single-operator
approval-quorum forgery in the epoch lifecycle, and a remote site-bricking
denial of service in publisher identity — which is the strongest available
argument for not promoting gates on internal confidence.

## Which remain blocked, and on what?

Six external dependencies, detailed in
[`production/EXTERNAL_BLOCKERS.md`](production/EXTERNAL_BLOCKERS.md):

| ID | Blocked on | Gates |
|---|---|---|
| EB-1 | Apple Developer credentials | PROD-26 |
| EB-2 | 3–5 independent operator administrators | PROD-05, PROD-21 |
| EB-3 | Multi-region WAN infrastructure | PROD-10, PROD-11, PROD-13, PROD-21 |
| EB-4 | Independent assessors and red team | PROD-04, PROD-29, PROD-30 |
| EB-5 | A second implementation by another author | PROD-03 |
| EB-6 | A second human release approver | PROD-30 |

## What exact external action is most urgent?

**EB-2 and EB-4 are the long poles**, because they are measured in weeks to
months of other people's time, and nothing engineering-side can shorten
them. Recruiting operator administrators and booking assessors should start
now, in parallel with the remaining implementation, not after it. EB-1 and
EB-3 are smaller and can follow.

Everything up to each boundary is being completed so that when the external
party arrives, their action is the only one left.
