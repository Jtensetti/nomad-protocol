# Claim-to-test matrix

Maps every security claim to the tests that exercise it and states the
boundary each reached. A claim without a boundary-level row is not evidenced
at that boundary, however much code exists. Feeds PROD-02.

Levels, weakest first:

- `structural` — enforced by API shape or a CI dependency gate, not by a test
  of behavior;
- `unit` — in-process test;
- `adversarial` — negative and attack tests at the same boundary as the claim;
- `integration` — composed processes, loopback or Compose;
- `boundary` — real interface, process, or release artifact;
- `independent` — verified by an external assessor. **Nothing is here yet.**

## Reader path

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| Emission plan takes no private input | planner API + package graph | selection-firewall tests; Selection Firewall CI gates | structural |
| Cells are exactly 1200 bytes at fixed cadence | real interface | Compose pcap gate (run 32301972409) | boundary, single host |
| Lost cells never cause catch-up bursts | real interface under loss/suspension | scheduler unit tests; one-second burst ceiling asserted on every captured world in the node wire campaign | adversarial, loopback |
| Cell size and destination do not depend on private activity | real socket, work queue empty vs full | `TestWireContentIsIndependentOfPrivateActivity`, mutation-verified | adversarial, loopback |
| Cell timing does not depend on private activity | real interface, two worlds, blind | `TestWireTimingIsIndependentOfPrivateActivityUnderStress`: median cadence decided against an idle-vs-idle control under CPU and disk pressure; not blind, not WAN, count-based effects undecidable on a shared host | integration, loopback |
| Private reader activity does not change wire behavior | real interface, two worlds, blind | as above; the blind evaluator and the WAN environment are both missing | integration |
| Cache maintenance independent of reads | wire trace comparison | CI dependency gates only | structural |
| The analysis rule detects the differences it claims to | both-direction self-tests | `scripts/test-two-world-analysis.py`, in CI: identical worlds accepted, each preregistered difference rejected, parser fails closed on any unparsed line | adversarial |

## Epoch and key lifecycle

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| Descriptor digests and signatures are canonical and reproducible | published vectors | epoch vectors incl. real signatures from a published key | adversarial |
| No single previous operator can force a membership transition | negative tests | quorum-forgery regression (index aliasing + approver binding) | adversarial |
| Split-brain fails closed, halt survives persistence failure | negative tests | equivocation, halt-fails-open, cross-process regressions | adversarial |
| Rollback to a burned epoch is rejected | negative tests | high-water-mark regression | adversarial |
| Rotation timing takes no private input | determinism test | `TestPlanIsDeterministicAndPublicOnly` | unit |
| Retired shares are refused | production path | share-service guard tests; `Chain.ServesEpoch` | unit |
| Retired epoch material is unrecoverable after erasure | adversarial experiment | `TestForwardSecrecyAfterErasure` | adversarial |
| Compromise recovery works end to end | drill | `TestRecoveryDrill` (5-operator, 3-of-5) | integration |
| No machine holds a complete decryption key | process + host separation | Compose share isolation | integration, single host |

## Publisher identity

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| SiteID derivation is deterministic and domain-separated | published vectors | site vectors | adversarial |
| Theft of a signing key does not confer recovery authority | negative tests | recovery-policy seizure regression | adversarial |
| A superseded descriptor cannot be reinstated | negative tests | rollback and absorbing-revocation property test | adversarial |
| Equivocation yields a transferable proof | third-party verification | forged-proof rejection + genuine-proof acceptance | adversarial |
| A foreign descriptor cannot poison a site | negative tests | foreign-genesis regression | adversarial |
| Encodings are unambiguous across implementations | parser differential | strict-parsing table, base64 malleability regression | adversarial |
| Identity resolution creates no query-dependent traffic | capture | pure function, no I/O; **no capture** | structural |
| Browser distinguishes integrity from identity | release binary | states defined; **not integrated** | none |

## Publication

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| Publish cannot reach a socket, transport or scheduler | package graph, transitively | in-package architectural test + CI gate | structural |
| The queue is bounded, crash-safe, idempotent, encrypted at rest | unit + restart | publish queue tests | unit |
| Drain order leaks no publication timing | unit | content-derived order test | unit |
| Uplink work and cover are indistinguishable to an observer | classifier | two independent classifiers fail against uplink | adversarial, cell level |
| Uplink work and cover are indistinguishable to the entry operator | design + test | cover is a real committee encryption on the identical path | unit |
| Publish/no-publish wire equivalence | blind two-world capture | **none** | none |
| One operator cannot link ingress to released plaintext | composition tests | **RETRACTED — see EVIDENCE_INDEX.md. The byte-level matcher scores chance whenever re-randomisation happens, whether or not the permutation hides anything, so it passes against a chain that preserves order exactly.** | none |
| A partial or reordered shuffle chain is refused | negative tests | **RETRACTED — the ten deviations are enforced only against a chain whose author volunteers the truth; `Round.Member` is an unauthenticated label.** | none |
| Release timing takes no private input | determinism test | pure function of four public parameters; seal refused early at every occupancy | unit |
| Batch size and shape do not reveal the deposit count | unit + decryption | identical size and shape at 0, 1, n-1, n deposits; every column including cover decrypts | adversarial |
| Deposits are idempotent and capacity does not grow | negative tests | resend, conflict, over-capacity and restart regressions | adversarial |
| The airlock cannot reach a socket or scheduler | package graph, transitively | in-package architectural test (mutation-verified) + CI gate | structural |
| Failure and retry add no traffic | capture under failure | **none** | none |

## Network coding and resources

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| Inconsistent dependent symbols are rejected | unit | rlnc tests | unit |
| Polluted systematic symbols never enter the basis | negative tests | commitment-mismatch test | adversarial |
| A malicious symbol cannot exceed the generation budget | Byzantine campaign | 50/90/100% campaigns, all budgets asserted | adversarial |
| Replay drains no budget | unit | duplicate test | unit |
| Coded-symbol pollution is prevented | per-symbol verification | **not claimed; see POLLUTION_AND_RESOURCES.md** | none |
| Sybil, eclipse, amplification bounded | simulation | **none** | none |
| Backpressure does not alter private-sensitive cadence | wire trace under load | **none** | none |

## Browser and release

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| Browser has no network entitlement | release binary inspection | CI entitlement gates at build | integration |
| A failed load never falls back to ordinary networking | negative tests at the adapter | thirteen failure modes, each ending in a local 4xx with no redirect header and an intact CSP; adapter graph holds no socket | adversarial |
| The renderer admits only local, non-scriptable URLs | negative tests | scheme, traversal, encoding and data: media-type table; the URL gate and the adapter share one path rule and a test fails if their verdicts diverge | adversarial |
| Zero browser egress including DNS | packet/DNS capture of the binary | **none** | none |
| Partial write cannot render | filesystem adversarial tests | materializer boundary tests | adversarial |
| Symlink, traversal, overwrite rejected | filesystem adversarial tests | materializer boundary tests | adversarial |
| Release is reproducible | two independent builders | comparison tool only; **no second builder** | none |
| Dependencies are scanned and gated | CI | govulncheck reachability gate | integration |
| Build has an SBOM and provenance | release artifacts | generators; provenance unsigned outside CI | integration |
| Update cannot roll back | updater tests | **no updater** | none |

## How to read the gaps

Every row at `none` is a claim the project must not make. Several of them —
publish/no-publish equivalence, browser egress capture, reproducibility with
a second builder, blind two-world classification — are the specific reasons
no PROD gate is MET, and they are gated on external resources (EB-1, EB-3,
EB-4) rather than on further design.
