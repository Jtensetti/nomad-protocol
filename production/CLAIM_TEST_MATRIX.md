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
| Cell timing does not depend on private activity | real interface, two worlds, blind | **CONTRADICTED — a reproducible difference is measured. See EVIDENCE_INDEX.md. Under a two-sample KS test over inter-arrivals, with a Latin-square rotation removing the position confound, idle and active differ at 1−p = 0.993 against a 0.517 control spread, reproduced on a second measurement.** | finding |
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
| One operator cannot link ingress to released plaintext | composition tests | permutation uniformity across trials, recovered with threshold authority (replaces a withdrawn byte-similarity matcher that passed against an order-preserving chain) | adversarial, in-process |
| Only the certified committee can produce a chain | forgery tests | rounds carry receipts signed by certified identity keys; a chain from a non-member, and one with a substituted signer, are refused | adversarial |
| A chain cannot replay into another epoch or committee | negative tests | sealed digest + release-epoch commitment; cross-epoch, cross-committee and cross-committee-epoch replays refused | adversarial |
| A round that does not re-randomise is refused | negative tests | zero-blinding detector over every column pair | adversarial |
| A partial or reordered shuffle chain is refused | negative tests | twelve deviations, each failing the epoch closed | adversarial |
| Cover is indistinguishable from a deposit before decryption | classifier over the wire form | whole-cell padding comparison at every occupancy | adversarial |
| Sealing leaks no publication volume through timing | duration + lock-contention measurement | seal duration and concurrent-deposit blocking compared empty vs full | adversarial |
| One bad deposit cannot censor an epoch | negative tests | malformed and small-order deposits refused at the boundary; an undecryptable column is dropped, not fatal | adversarial |
| Release timing takes no private input | determinism test | pure function of four public parameters; seal refused early at every occupancy | unit |
| Batch size and shape do not reveal the deposit count | unit + decryption | identical size and shape at 0, 1, n-1, n deposits; every column including cover decrypts | adversarial |
| Deposits are idempotent and capacity does not grow | negative tests | resend, conflict, over-capacity and restart regressions | adversarial |
| A depositor learns nothing about the epoch's occupancy | oracle tests | a full epoch drops silently; probing past capacity is indistinguishable from acceptance | adversarial |
| One depositor cannot name or squat another's slot | derivation + negative tests | IDs derived from (session, sequence); a foreign session cannot collide across 16 sequences | adversarial |
| One session cannot occupy the whole batch | quota test | per-session bound enforced silently, other sessions unaffected | adversarial |
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
| Eclipse is structurally impossible | invariant test | no peer discovery exists; peer set is a function of the signed topology and is byte-identical after a flood from unnamed addresses and correctly sealed cells from the wrong socket | adversarial |
| Sybil identities buy nothing | invariant test | 64 fresh identities leave the peer set unchanged; admission consults a signed document, never a population | adversarial |
| Amplification is bounded well below 1 | flood campaign | 0.0003-0.0008 outbound/inbound across four flood types, up to 396 MB in for 118 KB out | adversarial |
| Abusive peers are rejected for their own reason at no cost | negative tests | malformed, unauthenticated, misdirected, cross-epoch and replayed each rejected, nothing stored | adversarial |
| Availability under flood | sustained campaign | **not claimed — a flood can push a small node past its lateness budget; see ADMISSION_AND_RATE_CONTROL.md** | none |
| Backpressure does not alter private-sensitive cadence | wire trace under load | **none** | none |

## Operational output

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| A process may emit only fields with a written public rationale | schema allowlist | `live/telemetry` fails closed on any unlisted field; fourteen forbidden counters named with reasons | adversarial |
| Operational output contains no secret in any encoding | scan of everything written | production node run with known secrets; every file under its state directory scanned in raw, hex, upper hex and three base64 forms; instrument rehearsed against all five secrets first | adversarial |
| Operational output does not accumulate | retention test | health file rewritten in place, no append-only log | unit |

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

## Long-horizon correlation

The threat model assumes an adversary that correlates observations over long
periods. Nothing here bounds it.

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| Repeated sessions do not intersect to identify a reader | long-horizon campaign over many sessions | **none — E-10 NOT_STARTED** | none |
| Repeated publications do not intersect to identify a publisher | long-horizon campaign across epochs | **none — E-10 NOT_STARTED** | none |
| Cover traffic bounds aggregate leakage, not just per-observation leakage | analysis + campaign | **none; no analysis exists** | none |

Fixed-rate cover bounds what one observation reveals. It says nothing about
what many reveal in aggregate. This is the largest unmeasured area in the
project and the easiest to over-read from the per-observation results above.

## How to read the gaps

Every row at `none` is a claim the project must not make. Several of them —
publish/no-publish equivalence, browser egress capture, reproducibility with
a second builder, blind two-world classification, and every row in the
long-horizon section — are gated on external resources (EB-1, EB-3, EB-4) or
on unstarted work rather than on further design.

They are also why the great majority of PROD gates are not MET. Two gates
(PROD-08, PROD-12) are MET because their criteria name harms this matrix has
rows for at `adversarial` level; that is not a statement about the others.
