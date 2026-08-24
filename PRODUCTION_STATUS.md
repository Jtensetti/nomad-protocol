# Nomad production status

Last updated: 2026-08-21. Authoritative gate statuses live in
[`production/readiness.json`](production/readiness.json); this document
explains them in prose. Where the two disagree, the registry wins.

**Nomad is not production ready.** 2 of 30 production gates are MET. This
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
- **A publication airlock** (Workstream A): a bounded, encrypted, crash-safe
  publication queue with no network capability; an uplink cell format in
  which work and cover are indistinguishable to both a network observer and
  the entry operator; and a deposit boundary whose release timing and cost
  are pure functions of public parameters, whose batch size does not vary
  with how many people published, and which requires a full shuffle chain
  authenticated to the certified committee before per-column threshold
  release. The distributed form of that chain does not exist, and two
  deposit-ID findings from the review are still open.
- **Bounded network coding** (Workstream G): enforced per-generation CPU,
  memory, byte, symbol and lifetime budgets, with pre-admission verification
  of systematic symbols.
- **An executable traffic-analysis rule** (Workstream E): the preregistered
  two-world decision rule as code, with its thresholds fixed as constants
  rather than options, self-tests that assert it still detects each
  difference it claims to, and a wire-level campaign against the production
  node. It runs on loopback, which is its main limitation.

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
| Cell size and destination do not depend on private activity | adversarial at a real socket, loopback; mutation-verified |
| Cell timing does not depend on private activity | **CONTRADICTED — a reproducible difference is measured on loopback; see EVIDENCE_INDEX.md** |
| Publication release timing and batch size take no private input | unit + adversarial, protocol level |
| A partial or reordered shuffle chain is refused | adversarial, ten deviations |
| One operator cannot link ingress to release | measured at chance against a positive control, in-process |
| A failed browser load never falls back to ordinary networking | adversarial, thirteen failure modes |

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

- **Publication anonymity.** The airlock now has a deposit boundary, a
  fixed-size batch, a required full shuffle chain and threshold release, and
  an unlinkability result measured at chance against a positive control --
  but all of it runs in one process. The distributed form, with per-operator
  shuffle and decryption services over authenticated sessions, does not
  exist, and there is no wire capture of a publisher. Cell
  indistinguishability and an in-process chain are necessary pieces, not the
  property.
- **Availability against a sustained polluter.** Bounds stop resource
  exhaustion; at 50% or more malicious symbols a generation still fails to
  complete.
- **Sybil, eclipse and amplification.** No admission or rate-control model
  exists (G-05..G-09).
- **Timing independence from private activity.** The campaign now measures a
  reproducible difference: private-side work perturbs the inter-arrival
  distribution, most likely by contending for CPU and disk with an emitter in
  the same process. A dedicated shaper process is the structural fix and has
  not yet been measured. This is an open defect, not a gap in testing.
- **Anything at WAN scale.** All network evidence is single-host. The
  two-world campaign runs on loopback with userspace receive timestamps over
  seconds, and it reports honestly that a shared host cannot resolve
  packet-count effects at all. There are no multi-region, loss, congestion,
  NAT, IPv6, suspend/resume or clock-drift results, and no blind two-world
  classification by an independent analyst.
- **Browser egress at the binary level.** The release binary has never been
  packet- or DNS-captured, and the engine forks carry integration contracts
  only.
- **Anything about the shipped artifact.** SBOM and provenance generators
  exist and a dependency-vulnerability gate runs in CI, but there is no
  notarized build, no second builder to establish reproducibility, no signed
  provenance outside CI, and no updater.
- **Long-horizon correlation.** No intersection analysis, no 72-hour
  captures, no soak.

## Which PROD criteria are MET?

**Two.** 2/30: PROD-08 and PROD-12. The registry holds 21 PARTIAL, 6 NOT_MET
and 1 BLOCKED besides them.

- **PROD-08** (committee membership, rotation, forward secrecy, key erasure,
  compromise recovery): on the production path, with a normative spec,
  published descriptor vectors whose digest matches the registry byte for
  byte, and all thirteen named boundary tests passing race-enabled inside a
  53-test package — including a five-operator three-of-five recovery drill.
- **PROD-12** (generation-bound, pollution-resistant network coding): source
  commitments under the authority signature, a decoder that refuses polluted
  systematic symbols before admission and enforces per-generation budgets, two
  fuzz targets, and a Byzantine campaign of 72 trials from 0 to 100 per cent
  pollution producing zero accepted corruptions.

Both were promoted on external test reports rather than GitHub Actions, which
the evidence rule permits in the same clause ("GitHub Actions **or** external
test report"). An earlier reading of the Actions outage as capping every
promotion was wrong, and the triage document is corrected.

Neither promotion claims more than its criterion names. PROD-12 in particular
does **not** claim pollution cannot deny a generation: a dense coded symbol
cannot be verified before admission over GF(2^8), a third of the campaign's
trials were denied, and the first version of the budget fuzzer asserted
correctness under hostile input and was refuted within seconds.

Defects found and fixed during this cycle, rather than assumed absent: a
silent wrong-decode in the RLNC decoder that returned a mixture of source
symbols as one symbol with a nil error, on the production materializer path;
a signed topology carrying one key twice being accepted, where Go's last-wins
rule differs from parsers that keep the first; and a stale topology being
replayable because nothing remembered which epoch the node had already served.
Each has a regression that fails against the pre-fix code.

The structural defect behind the first was worse than the defect: the six
vendored component modules in nomad-testnet, and the three pinned snapshots in
Nomad-browser, carried no tests at all and were invisible to `go test ./...`.
What shipped was untested by the repository that ships it. All nine now carry
their standalone repositories' suites and are gated in CI.

Three adversarial reviews during this work each found exploitable defects in
code that looked finished, and had passing tests: a single-operator
approval-quorum forgery in the epoch lifecycle; a remote site-bricking denial
of service in publisher identity; and, in the publication airlock, four Sev1
defects including one that let a party holding no committee share forge the
entire "certified" shuffle chain and read the whole ingress-to-egress map.

The airlock review is the sharpest argument against promoting gates on
internal confidence, because two of its findings invalidated claims this
project had already written down and one of them showed a *measurement* to be
worthless: the unlinkability matcher scored chance against a chain with zero
anonymity. Those claims were retracted rather than amended. An internal
review is QA, not independent assessment (PROD-04, PROD-29), and each of
these found real exploits — which says more about what a genuinely
independent assessment would find than about what has been fixed.

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
