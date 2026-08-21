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

### Two-world analysis rule and wire campaign (Workstream E, sprint E1)

- Analysis rule: `Jtensetti/nomad-testnet@9c0ac81` (`scripts/capture.py`,
  `scripts/two-world-analysis.py`, `scripts/test-two-world-analysis.py`).
- Campaign: `Jtensetti/nomad-testnet@cda072d` (`live/wire`,
  `live/node/campaign_test.go`).
- Preregistration: `production/PREREGISTRATION.md` v1.
- Demonstrates: the preregistered decision rule is executable, with its
  thresholds as constants rather than options; its self-tests assert both
  directions and run in CI; its capture parser fails closed on any line it
  cannot parse. Against the production node on a real socket, cell size and
  the ordered destination sequence are identical whether the work queue is
  empty or full (mutation-verified: a work-dependent destination fails the
  test on every cell), and median cadence under CPU and disk pressure is
  within 0.006 of an idle-vs-idle control against a 0.02 tolerance
  (mutation-verified: an injected work-dependent emission delay is caught at
  1.0004). The one-second burst ceiling holds on every captured world.
- Does NOT demonstrate: anything about a WAN. Loopback, single host,
  userspace receive timestamps, seconds rather than days, and the analyst is
  the party that wrote the system. Packet-count and early-termination
  effects are reported but explicitly undecidable at this sample size on a
  shared host, and are not claimed. E-01, E-02, E-06 and E-09 remain open,
  and no PROD gate changes.
- Two defects found and fixed while building this, both of which made the
  tooling report that two worlds matched when they did not: a two-sample KS
  walk that charged tied values as ECDF gaps (a sample against itself scored
  0.44, p=9e-35, on exactly the quantized inter-arrivals a fixed-cadence
  capture produces), and a capture regex that silently skipped VLAN-tagged
  packets, which the existing `verify-pcap.py` CI gate shared -- a tagged
  capture would have passed its 1200-byte cell check without inspecting a
  single packet.

### Publication airlock (Workstream A, sprint A2)

- Implementation: `Jtensetti/nomad-testnet@1df9113` (`live/airlock`).
- Specification: `docs/PUBLICATION_AIRLOCK.md`.
- Demonstrates: release timing is a pure function of four public schedule
  parameters and an epoch number, refused early at every occupancy from empty
  to full; sealed batches are identical in size and shape at 0, 1, n-1 and n
  real deposits, with every column including cover decrypting; deposits are
  idempotent by ID with conflicts refused rather than overwritten and
  capacity refusing rather than growing; a restart re-derives the same window
  and accepts the resend; sealed placement carries no stable information
  about arrival order; ten distinct deviations from the full certified
  shuffle chain each fail the epoch closed with no partial-chain path; and a
  byte-level nearest-neighbour matcher holding both the sealed batch and the
  chain output links ingress to release at chance (5 of 48 against 6.0
  expected), against a positive control where the same matcher is perfect
  once re-randomisation is removed. The package has no transitive path to a
  socket, scheduler or peer selection, enforced by an in-package
  architectural test verified by mutation and by a CI dependency gate.
- Does NOT demonstrate: unlinkability as a proof. The measurement is one
  concrete matcher over a small sample; the guarantee rests on re-randomised
  ElGamal being IND-CPA and on the anytrust assumption, and a test
  establishes neither. The anytrust assumption itself is untestable -- if
  every shuffler colludes the chain is linkable by construction -- so what is
  tested is that the code requires every member to participate. There is no
  wire capture (A-04, A-12), no online distributed mix path (A-15; the chain
  runs in-process and the fixture bootstrap holding every identity is not a
  production ceremony), and no analysis of selective dropping by a malicious
  entry operator (A-09). Deposits are held in memory and are lost on restart,
  which is the intended trade. Not yet independently reviewed. No PROD gate
  changes.

### Renderer URL and failed-load boundary (Workstream F, F-07)

- Implementation: `Jtensetti/Nomad-browser@0388b7e` (`egress`, `adapter`).
- Demonstrates: thirteen distinct failed loads -- unknown resource, an object
  missing from the verified store, traversal, backslash separators,
  non-canonical paths, URL syntax in the path, NUL, relative, empty and
  oversized paths, and write methods -- each end in a local 4xx with an empty
  body, no `Location`, `Refresh`, `Link` or `Content-Location` header, and an
  intact `default-src 'none'; connect-src 'none'` policy. The adapter's
  transitive package graph holds no socket, so the absence of a fallback is a
  property of its capability rather than of today's code. The renderer URL
  gate and the local adapter now share one resource-path rule, with a test
  that fails if their verdicts ever diverge, and `data:` URLs are limited to
  an allowlist of non-scriptable media types.
- Two defects found while writing the missing negative test, neither
  exploitable: the URL gate and the adapter each carried their own path rule
  and disagreed (the gate accepted `nomad:/../../etc/passwd`, which the
  adapter refused, so nothing reached the filesystem), and the gate admitted
  `data:text/html` carrying script, which does not inherit the adapter's CSP
  because a navigated `data:` URL is its own opaque-origin document. Egress
  was still blocked by the absent network entitlement in both cases.
- Does NOT demonstrate: anything about a running release binary. There is no
  packet or DNS capture (F-08), the binary is unsigned (F-09, EB-1), the
  engine forks carry integration contracts only (F-11), and no independent
  browser-security assessment has happened (F-10, EB-4). No PROD gate
  changes.

### RETRACTION: airlock unlinkability and chain-integrity claims (Workstream A, sprint A2)

An adversarial review of the airlock, run under the evaluator-separation rule
before any promotion, found four Sev1 defects with working exploits. Two of
them invalidate claims recorded in the sprint A2 entry above. Those claims are
retracted here rather than amended in place, so the record shows they were
made and withdrawn.

**"A partial or reordered shuffle chain is refused" is withdrawn.**
`Round.Member` is an unauthenticated `uint32` label, and a Neff shuffle proof
binds only to the public key and the input/output digests -- nothing ties a
proof to the member that produced it. An entry operator holding no committee
share at all can run every shuffle itself, label the rounds with the certified
member indices, and `VerifyChain` accepts. The ten deviation tests are real,
but they constrain only an adversary that volunteers the truth about who
shuffled. The anytrust assumption inverts: the adversary needs to corrupt no
shufflers rather than all of them.

**"One operator cannot link ingress to released plaintext" is withdrawn.**
The byte-level matcher scores chance whenever re-randomisation occurs,
independently of whether the permutation hides anything. The review
demonstrated the same measurement, at the same five-sigma bound, passing
against an output that is the same plaintexts in the same positions with
fresh randomness -- total linkage, zero anonymity. The positive control
removed only re-randomisation, so it never exercised the failure mode that
mattered. Under the project evidence rules this measurement must not be cited
as boundary evidence for A-05.

Two further Sev1 findings are recorded here because they contradict statements
in `docs/PUBLICATION_AIRLOCK.md` rather than in this index:

- Cover columns were distinguishable from real deposits **before any
  decryption**: a real deposit left wire bytes 1152..1200 zero while cover,
  produced through `MarshalWire`, filled them from `crypto/rand`. A one-line
  classifier recovered the exact real-deposit count, and which columns were
  real, at every occupancy. The specification's "indistinguishable from a real
  deposit until it has been decrypted" was false. The existing tests missed it
  by slicing comparisons to `[:DepositSize]`, exactly the region that cannot
  vary.
- `Seal` generated one ElGamal encryption per *empty* slot inside the lock, so
  its runtime was linear in how few people published: 2.59s at zero real
  deposits against 0.014s at a full batch, a 190x readout of publication
  volume, and a concurrent depositor could read the same signal remotely by
  measuring how long its own call blocked.

Remediation is tracked in the commits that follow. No claim above is restored
until it is re-evidenced against the fixed code, and no PROD gate was ever
promoted on any of them.

### Airlock remediation (Workstream A, sprint A2 follow-up)

- Implementation: `Jtensetti/nomad-testnet@42824f8` (`live/airlock`,
  `components/nomad-anytrust-mix-sim/mix`).
- Fixes, each with a regression, for six of the review's findings: shuffle
  rounds now carry receipts signed by certified identity keys with a proof
  domain bound to committee, committee epoch, batch and round; a round that
  does not re-randomise is refused; the sealed wire form is re-derived so
  padding cannot identify cover; cover is generated before the window so
  sealing costs the same at every occupancy; a sealed digest and release-epoch
  commitment stop whole-chain replay; and deposits are validated on arrival
  while release drops an undecryptable column instead of censoring the epoch.
  Also: committee keys, member shares and deposits reject identity and
  small-order points, epoch arithmetic refuses values that would overflow, the
  idempotency comparison is constant time, and sealing is bounded above.
- The A-05 measurement was rebuilt. The withdrawn byte-similarity matcher is
  replaced by recovering the ingress-to-egress permutation with threshold
  authority and checking it for uniformity across trials, which is the
  property that actually has to hold.
- Still NOT demonstrated: unlinkability as a proof (the measurement is a small
  number of trials at a small batch size; the guarantee rests on re-randomised
  ElGamal being IND-CPA and on the anytrust assumption, and a test establishes
  neither), the anytrust assumption itself, any wire capture, or the online
  distributed mix path (A-15).
- Both remaining findings were subsequently closed in
  `Jtensetti/nomad-testnet@845edff`: deposit IDs are derived from an opaque
  per-session value and a sequence number, so one depositor cannot name
  another's slot, and a full epoch drops the deposit silently rather than
  reporting occupancy, with the count surviving only in operator-local
  accounting. Per-session slot quotas bound one client's share of a batch.
  This does not give fair access under Sybil: an attacker holding many
  authenticated sessions still competes for slots, which needs the
  admission and rate-control model of G-05..G-09. All seven Sev1/Sev2
  findings from the review are now fixed, each with a regression.
- **Process finding:** `components/nomad-anytrust-mix-sim` is a vendored
  snapshot pinned by `COMPONENTS.sha256`, and it has diverged from the
  standalone repository in both directions -- the vendored copy carries
  `ValidateThresholdCommittee`, `ValidateMemberSecret` and
  `dkg_protocol.go` that the standalone lacks, while the standalone carries
  tests the vendored copy lacks. A security fix made in the standalone
  repository would not reach what ships. The fixes above are in the vendored
  copy, with digests regenerated. Reconciling the two is outstanding.
- No PROD gate changes.

### FINDING: private activity perturbs emission timing (Workstream E, E-08)

A measured, reproducible difference between the idle and active worlds at the
sender's socket. This contradicts the claim "cell timing does not depend on
private activity" at the level the campaign can currently test, and that row
is marked CONTRADICTED rather than downgraded.

**What was measured.** The wire campaign runs three idle series and one active
series, interleaved. The distance between two worlds is now also computed with
a two-sample Kolmogorov-Smirnov test over inter-arrivals, the same statistic
the published decision rule uses, expressed as 1 − p so that a larger number
means less alike.

| Stressor | idle vs active | control spread | verdict |
|---|---|---|---|
| baseline | 0.9983, then 0.9931 | 0.5168 | finding, reproduced |
| cpu-starvation | 0.0748 | 0.8606 | no finding |
| disk-pressure | 0.9974, then 0.9991 | 0.6453 | finding, reproduced |

**Two of the project's own instruments were wrong, and both are corrected.**

The campaign ran its three idle series and then the treatment, every round, so
the treatment was always last and any within-round drift landed systematically
on it. That is a confound, not a leak. The order is now rotated as a complete
Latin square, so every series occupies every position exactly once. The
finding survives the rotation.

The in-process gate compared only the median inter-arrival, and the median is
far less sensitive than KS: on the same captures it reported "no finding"
while the published rule rejected at p = 1.5e-06. Gating on a weaker statistic
than the one being published means the gate passes what the published rule
would reject, so KS was added to the in-process gate.

**A third instrument was silently broken.** The CI step that ran the published
rule over the campaign captures passed already-rendered text captures to a
reader that shells out to `tcpdump -r`. Every invocation crashed, and the
crash was recorded as a rejection — the rule reporting that two worlds
differed when it had never read them. `read_capture` now decides from the
file's own first four bytes whether it holds a pcap or rendered text, and the
rule exits 2 when it cannot run at all, distinct from exit 1 for a finding, so
a crash can no longer be recorded as a verdict.

**Most likely mechanism, not established.** The private-side work in the
active world (repeated hashing and small file writes) shares a process and a
host with the fixed-cadence emitter, so it competes for CPU and disk. That is
consistent with cpu-starvation showing no finding: when the whole host is
already saturated, the marginal contention from private work is lost in it.
This has not been isolated to a cause, and no claim is made that it has.

**Where the fix is.** `agent/operator-shaper-process` moves fixed-rate egress
into a dedicated process, which is the structural answer: private work cannot
contend with an emitter it does not share a runtime with. That branch is not
merged and this campaign has not been run against it, so nothing here yet
shows the fix works.

**Boundary.** Loopback, single host, userspace receive timestamps, seconds.
This is not WAN evidence and does not become a WAN claim. It blocks PROD-10
and PROD-11 rather than supporting them, and no gate is promoted on it.

### Multi-region WAN two-world campaign (Workstream E, E-01/E-02)

Five campaigns on 21 August 2026, on Scaleway DEV1-S instances in fr-par-1
(FR), nl-ams-1 (NL) and pl-waw-1 (PL), in a signed ring a to b to c to a, 1200
byte cells at a 50 ms cadence. Harness in `Jtensetti/nomad-testnet`
`scripts/wan/`, driven by `run-campaign.sh`; every resource carries a
deployment tag and teardown runs from an EXIT trap. All five deployments were
verified destroyed, servers and public addresses, by direct API query after
the run.

The first four are reported because the instrument changed under them, and a
campaign whose earlier attempts are not shown is a campaign whose method was
chosen after seeing the answer.

| Run | Deployment | Worlds | Outcome |
|---|---|---|---|
| 1 | `nomad-wan-20260821-122122` | idle, active | no data: 0 packets on all 3 hosts |
| 2 | `nomad-wan-20260821-123801` | idle, active | VOID under PREREGISTRATION v2 |
| 3 | `nomad-wan-20260821-125932` | idle, active | uninterpretable: no control pair |
| 4 | `nomad-wan-20260821-131659` | idle1, idle2, active | PASS on 3/3, degraded fabric |
| 5 | `nomad-wan-20260821-134230` | idle1, idle2, active | b and c PASS, a INCONCLUSIVE |

**Run 1 captured nothing, and the node was right.** `curl` honours the
inherited umask, so the fetched operator secret landed 0644, and `nomad-node`
refused to load a group-readable secret. The check was correct and the payload
was wrong. Reproduced locally at both modes before the fix, and the payload now
sets `umask 077`, chmods the secret, and preflights the node so a refusal shows
in seconds instead of after two empty captures.

**Run 2 is void, not a finding.** It was rejected on all three hosts. The cause
was the analysis script, which pooled each capture's packets into one series
when PREREGISTRATION v1 registered extraction "per capture, per direction, per
peer". A capture taken with `-i any` holds the host's own emissions and its
peers' arrivals, the node restarts between worlds, and the restart
re-randomises the peers' phase; pooled, the inter-arrival distribution shifts
on its own. PREREGISTRATION v2 writes the sample definition down and voids this
run under the amendment rule. Recomputing it with a corrected instrument is
diagnosis and is reported as diagnosis; it is not a result.

**Run 3 rejected one host and could not be interpreted.** operator-a failed the
inter-arrival KS at p=0.00988 against a registered alpha of 0.01, with exactly
equal cell counts (5994/5994) and a mean drift of 8.8e-07 on the same flow;
operator-b and operator-c passed. The campaign had no idle-versus-idle pair, so
there was no noise floor and no way to tell a treatment effect from any two
captures on that host differing. The campaign now runs two idle series, with
world order rotated per operator so that exactly one host is active in each
position.

**Run 4 passed on all three hosts, on a fabric that was not healthy.**
operator-a reported `replay_rejected` 5574 of 5675 received while the other two
reported none. World boundaries were offsets from each host's own boot; hosts
boot up to half a minute apart, and in a ring exactly one host starts before
its upstream peer, records the tail of that peer's previous world, then sees
the peer's sequence counter reset and correctly rejects the remainder as
replays. Emissions were unaffected, but the relay path was not exercised at
that host. World boundaries are now absolute instants shared by every host.

**Run 5 is the reportable measurement.** With boundaries aligned,
`replay_rejected` was 0 on all three hosts and each received 5975 to 5980 of
5979 sent.

- operator-b: PASS. control KS p=0.3475, treatments 0.7028 and 0.1583.
- operator-c: PASS. control KS p=0.2725, treatments 0.3475 and 0.9848.
- operator-a: INCONCLUSIVE. Its control pair, two idle worlds, was rejected at
  KS p=0.007783, while both its treatment pairs passed at 0.3969 and 0.07151.

**What run 5 shows.** Cell counts were exactly equal within every pair on every
host, in every run that produced data: 5991/5991, 5993/5993, 5996/5996,
5997/5997. The node emits the same number of cells whether or not it is the one
publishing, and mean inter-arrival drift stayed at 1e-6 to 1e-7 of the cadence
against a registered tolerance of 2e-2. Maximum one-second burst was identical
across worlds everywhere.

**What it does not show.** operator-a yields no verdict: on that host two
identical worlds differ by the rule's standards more than idle differs from
active, so its noise floor exceeds the registered alpha and nothing can be
concluded there. fr-par-1 was also the host rejected in run 3, when no control
existed to check it against, which is the reading the control was added to make
possible -- but two runs cannot establish that a host is systematically noisy.

**Boundary.** One administrator, one provider, one account, three regions.
That is three failure domains in the geographic sense and one in the
administrative sense, so it is not evidence of independent operation and does
not support PROD-05 or PROD-21. One run per host, 300 s per world, against a
registered screening design of 30 captures per world at 5 minutes each: this
is a single screening sample, not the screening. No gate is promoted on it.
PROD-28's 30-day soak is untouched by it.

**Artifacts.** Run 5 (`nomad-wan-20260821-134230`) capture digests, SHA-256:

| Capture | Digest |
|---|---|
| `operator-a-active.pcap` | `e38e39aa62daad555cf1e1a61dc76d140124197dae70f588fbab284db6111e68` |
| `operator-a-idle1.pcap` | `6e1d48a1bc4e7ece787d2408ae8ea481cb14bccc1712dac231cc4d1f47b4e564` |
| `operator-a-idle2.pcap` | `d2fabb2b19a0b1833024cf65debe28c1c14c7601ad59d64ffdb316ec64ee9780` |
| `operator-b-active.pcap` | `1fcd0c741c9d4175dc427b7adac937b3093330204f5ed7fde263d4e5fc883580` |
| `operator-b-idle1.pcap` | `c3a4ad78939721008f64f401bc14ac2441e7a214bfd211cff739cfa68ce925dc` |
| `operator-b-idle2.pcap` | `901934f5d57f31ef28dfa1357e5c58f210fa54dfa07ba59beefb86ded2debcfc` |
| `operator-c-active.pcap` | `721736d1b682efa3809422d682ab6cc210f8daa66c9d84e61279f684d6a057f0` |
| `operator-c-idle1.pcap` | `77e72c585a683820f336e1912f6f06a30e6f2417f2e9e2fb861b190b45fa6976` |
| `operator-c-idle2.pcap` | `ae2d06430b2556285291cc4c0049bd729cccfaad60d3582ff56ad5015221d252` |

Analysis reports and per-host campaign logs are held with the run. The campaign is
reproducible from `scripts/wan/run-campaign.sh` plus Scaleway credentials; the
decision path is `scripts/wan/wan-verdict.py` over `scripts/two-world-analysis.py`,
which is the same code and the same exit statuses CI uses.
