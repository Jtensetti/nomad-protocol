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

## Admission and directory

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| A topology must be attested by every operator it lists | negative tests | stripped attestation and dropped operator both refused; each survivor's attestation covers the whole document | adversarial |
| A superseded topology version is refused | negative test | version-downgrade case | adversarial |
| Traffic class and threshold cannot be weakened below the profile | negative tests | off-profile cell size, sub-floor threshold, sub-floor operator count | adversarial |
| A node will not accept a topology older than one it has served | rollback across restart | persisted per-network watermark; refusal verified at the binary boundary | adversarial |
| Two topologies for one network epoch fail closed | negative test | equivocation refused rather than last-writer-wins | adversarial |
| A watermark the node cannot parse is not permission to proceed | negative tests | truncated, wrong-version, zero-epoch, short-digest and unknown-field states all refuse | adversarial |
| The admission format is described well enough to interoperate | a consumer that is not this codebase | signed-topology golden vectors exist; **nothing outside this repository has parsed them** | none |

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
| Failure and retry add no traffic | capture under failure, four conditions | success, timeout, restart with a durable queue, adversarial loss: every world emits the same cell count, size and destination as an idle publisher | adversarial, in-process |
| Failure and retry do not shift emission timing | capture under failure, four conditions | judged by the full preregistered rule in CI, with a measured noise floor of 0.0003 to 0.0038 against a 0.02 tolerance; restart is compared against restart-without-work, since a restart is observable by construction | adversarial, in-process |
| A publisher can hold the cadence it is given | per-cell cost against the cell interval | **CONTRADICTED — sealing one cell takes ~87 ms against a 50 ms deployed interval and a 5 ms permitted minimum; half the cost is a discarded companion mix column. See EVIDENCE_INDEX.** | finding |
| A queued object reaches a sealed batch across the uplink | end-to-end path | queue to drain to ingress to airlock to seal, with the fixed batch size preserved | integration |
| Emission count does not depend on having work | busy versus idle publisher | a full queue and no queue at all emit the same number of identically sized cells over the same ticks; the test fails if either run was not actually mixed | adversarial, in-process |
| The queue is never read on the emission path | design + package graph | a filling goroutine holds a one-slot buffer; the tick does a non-blocking receive and touches no disk | structural |
| The entry operator cannot separate work from cover | cell inspection | one cell size, one inner-layer size, only threshold decryption distinguishes them | adversarial |
| Deposit order does not predict release position | correlation experiment with positive control | no defence 1.00, seal only 0.18, full path 0.21, chance 0.25 over 25 trials | adversarial, in-process |
| The shuffle chain's own contribution to unlinkability | adversary observing between hops or controlling mixers | **none — the experiment above defeats its adversary with the seal alone and does not reach the chain's purpose** | none |

## Accountability

| Claim | Boundary required | Tests | Level |
|---|---|---|---|
| A mixer that signs an unsound round can be named | forgery + attribution tests | `AttributeFault` names the signer; the receipt covers context, input, output and proof digests together | adversarial |
| Blame is verifiable by a third party, not testimony | independent re-derivation | `VerifyFaultReport` re-derives the fault from the transcript; a fabricated report against an honest chain is refused | adversarial |
| Blame cannot be moved onto an honest mixer | negative test | a genuine report re-pointed at a neighbour fails verification | adversarial |
| An impersonated mixer is not blamed for the forgery | negative test | a receipt failing under the key it names marks that mixer a victim | adversarial |
| Broken linkage is not pinned on one neighbour | negative test | charged to the chain assembler; linkage checked before soundness so a mixer handed the wrong input is not accused | adversarial |
| A stopped mixer can be reported | availability report | a quorum of distinct certified observers each sign a non-receipt bound to a deadline the public timetable fixes | adversarial |
| An availability report cannot evict an honest operator | negative tests | below quorum establishes nothing; a repeated signer, an uncertified key and self-accusation do not count; an accusation cannot be re-pointed | adversarial |
| Statements cannot be moved to another round or deadline | negative tests | the round context and deadline are inside the signed message; verified by rewriting a report *and* every statement in it consistently, which the report-level consistency check alone does not catch | adversarial |
| A falsely accused operator can answer, and the answer names its accusers | refutation | the accused produces its own sound round for that exact position; a round from another position, another mixer's round and an unsound round are all refused | adversarial |
| A stopped mixer can be shown to have *withheld* | — | **not decidable: asynchrony makes withholding and a dropped packet indistinguishable, so the report is deliberately non-attributable** | n/a |
| Reporting availability does not leak reader activity | privacy boundary | every certified operator is judged at every deadline so report volume cannot track load; two observations of one position are byte-identical; CI holds the observer's graph to mix and topology | adversarial |
| Selective failure is detected | serving some peers and not others | **none** | none |
| Faults are attributed against a live committee | active-adversary injection | **none — constructed transcripts and a unit-tested delivery source only; needs a running committee where an operator actually stops** | none |
| A vanished operator's share is not rerouted to a survivor | two-world at the surviving peer | the survivor receives exactly its half of a two-peer rotation with the other operator absent, and the sender counts every scheduled emission as sent | adversarial |
| Private activity during an outage does not change what a peer sees | two-world at the surviving peer | idle and busy outage worlds deliver identical counts, sizes and destinations | adversarial |
| An outage is survivable across regions | regional outage test | **none — B-09 NOT_STARTED; loopback only** | none |

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
| The engine egress surfaces are enumerated and anchored | inventory verified against the tree | 31 Gecko and 18 Blink surfaces, each with what the integration owes it; a verifier fails when an anchor stops existing | structural |
| An engine fork routes renderer paths through verified local data | engine implementation + browser tests | **none — no engine code is modified in either fork** | none |
| Partial write cannot render | filesystem adversarial tests | materializer boundary tests | adversarial |
| Symlink, traversal, overwrite rejected | filesystem adversarial tests | materializer boundary tests | adversarial |
| Release is reproducible | two independent builders | comparison tool only; **no second builder** | none |
| An embedding model that changed is detected | behavioural attestation | a fixed public probe set fingerprinted by basin, refused when it moves; degenerate probe sets rejected at attestation time | adversarial |
| The embedding service is running the model it claims | attestation of the model itself | **not establishable: a service willing to lie about its model is willing to lie about a hash of it** | n/a |
| The semantic service is sandboxed with authenticated IPC | sandbox + mutual auth + egress capture | **none — bounded loopback adapter only** | none |
| Dependencies are scanned and gated | CI | govulncheck reachability gate in all nine repositories and all nine vendored modules, verified by exit code | integration |
| The toolchain still receives security fixes | CI pin against Go's support window | every repository on 1.25, after a 1.23 pin aged out and left 20 reachable stdlib vulnerabilities in the one repo that was scanning | integration |
| Dependencies are not malicious | provenance or attestation of the dependency itself | **none — govulncheck answers whether an advisory is reachable, not whether a dependency is what it claims to be** | none |
| Build has an SBOM and provenance | release artifacts | both generated in CI; provenance stamps itself unsigned outside a protected identity, and no release key exists (EB-7) | integration |
| Update cannot roll back | updater tests | a persisted watermark refuses anything not strictly newer, pre-release ordering included, so a signed 1.2.0-alpha.1 cannot install over 1.2.0 | adversarial |
| Two signed artefacts for one version are refused, not resolved | negative test | equivocation is an error rather than a choice, because resolving it silently is how a build made for one person reaches them | adversarial |
| A genuine manifest does not authorise a different file | negative test | size checked before hash, so a padded artefact fails on length | adversarial |
| Corrupting the watermark does not disable rollback protection | negative test | an unreadable watermark refuses the install rather than reading as absent | adversarial |
| The updater cannot give the browser network access | dependency direction | the update package fetches nothing, and a test fails if its graph gains net, net/http, net/url or os/exec | adversarial |
| Updates are verified against a genuine release key | release key custody | **none — no release key exists (EB-7); the mechanism is exercised against test keys only** | none |
| A user is protected without doing this manually | installer integration | **none — nothing invokes the verifier when a disk image is mounted** | none |

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

| Every supported target builds | cross-compilation matrix | eight targets including windows/amd64 and windows/arm64, gated in CI | integration |
| The Windows cross-process lock works | a Windows runner | **none — it compiles and has never run** | none |

## How to read the gaps

Every row at `none` is a claim the project must not make. Several of them —
publish/no-publish equivalence, browser egress capture, reproducibility with
a second builder, blind two-world classification, and every row in the
long-horizon section — are gated on external resources (EB-1, EB-3, EB-4) or
on unstarted work rather than on further design.

They are also why the great majority of PROD gates are not MET. Two gates
(PROD-08, PROD-12) are MET because their criteria name harms this matrix has
rows for at `adversarial` level; that is not a statement about the others.
