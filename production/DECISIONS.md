# Decision log

Engineering decisions with rationale. Newest first.

## DEC-015 (2026-08-25): Two wire-format questions are deferred to the freeze, not settled quietly

Both were found by measurement this session, both have a clear technical
answer, and both change bytes on the wire. Recording them together because the
reason for deferring is the same and the freeze is the moment to take them.

**The hop header is authenticated but not encrypted.** A link observer reads
the work flag, the batch coordinates and the 16-byte stream ID off every relay
cell, and the stream ID is unchanged across hops, so ingress and egress link by
reading 16 bytes with no correlation attack
(`nomad-testnet live/node/linkability_test.go`). Encrypting the header under
the existing pairwise hop key removes the linkability. It also invalidates the
published conformance vectors and the second implementation built against them.

**Embedding data in a point's y-coordinate costs sixteen discarded scalar
multiplications per chunk.** Of a 36 ms serial cell seal, about 30 ms is
kyber's `Point.Embed` rejection loop and under 4 ms is the ElGamal. A
prime-order group encoding (Ristretto-style) has no cofactor and no rejection,
which removes the cost rather than spreading it across cores as the current
parallelisation does.

**Decision: neither is made now.** Each is a protocol change with an
interoperability cost, and this project has exactly one second implementation
and one conformance corpus to invalidate. Making them separately, before a
freeze, spends that twice. Making them after a freeze costs far more. So both
are recorded as blockers on PROD-01 with the measurements attached, to be taken
together as one format revision or explicitly declined with a reason.

**What was done instead**, so the deferral is not an excuse for inaction: the
linkability is measured and stated in `THREAT_MODEL.md` rather than left as a
note; the seal cost is parallelised from 36 ms to 12 ms, which clears the 50 ms
deployed cadence with headroom, and the remaining gap to the 5 ms shortest
permitted cadence is recorded as a blocker naming this decision.

## DEC-014 (2026-08-25): A local failure costs one cell, never the schedule

Recorded because it trades availability for the emission invariant in a way a
later reader might otherwise mistake for a bug.

Any error from the sink used to end the scheduler, and in the live node that
closed the socket: an exhausted socket buffer or a full disk stopped a node
permanently. A node going silent is the loudest event a passive observer can
see, from causes that are local and ordinary.

A transient local failure now costs the cell it interrupted and nothing else --
never retried, never deferred and re-emitted, never followed by a catch-up, and
the peer rotation stays a function of the tick index. Which failures qualify is
an **allowlist** of named transient conditions, not a denylist: the first
version asked whether an error was fatal and answered with a list of one, so
hop sequence exhaustion became a counter. `EPERM` and `EINVAL` are deliberately
absent, being a firewall verdict and an unusable destination, and a transient
condition that does not clear stops the node after a bounded run.

The cost is that the crudest alarm an operator had -- the process exiting --
is gone. It is replaced rather than dropped: `last_sent_at` and `send_dropped`
are published, `nomad-node --check-health` fails a node that is up and emitting
nothing, and both deploy runbooks, the Compose healthcheck and the WAN campaign
use it.

## DEC-013 (2026-08-24): Nomad-browser is the browser; the engine forks are parked

The maintainer's decision, recorded because it changes what "done" means for
Workstream F and should not be re-litigated by a later session reading the
workstream list.

Nomad-browser is a working networkless browser core with a release pipeline,
an enforced sandbox entitlement, an adversarially tested materializer handoff
and a no-fallback adapter. `firefox-nomad` and `chromium-nomad` are full engine
checkouts carrying integration contracts and, as of today, a machine-checked
egress inventory each. Nothing more will be invested in them for now.

**What this means for the registry.** F-11 stays PARTIAL and PROD-22 keeps its
blocker saying no engine code is modified in either fork. Neither becomes MET,
and neither is deleted: the criteria still describe work that a full production
deployment would want, and the honest status is "not done and not being
pursued" rather than "not applicable". The inventories remain useful to whoever
picks this up, and their verifier keeps them from rotting.

**Why the decision is reasonable on the merits.** An engine integration is the
single largest remaining piece of work in the whole programme, it duplicates a
guarantee Nomad-browser already provides by construction rather than by
subtraction, and a networkless browser built from nothing is a far smaller
attack surface to defend than a networked engine with its network removed. The
egress inventories are the honest measure of that: thirty-one surfaces in Gecko
and eighteen in Blink, each of which would have to be closed and stay closed.

## DEC-009 (2026-08-20): One two-world capture harness, born in A, extended in E

The blind-capture/preregistration machinery required by the airlock DoD
(A-12) and by WAN testing (E-06/E-07) is a single harness to prevent
divergent methodology. Built during Workstream A, extended in E.

## DEC-008 (2026-08-20): Publication ingress spike before descriptor freeze

The client constant-rate uplink and online distributed mix path do not exist
yet (evaluator findings 1-2). An ingress spike runs immediately after C's
descriptor core lands; EpochDescriptor v1 reserves a versioned
`uplink_profile` field so the spike's traffic-class parameters land without
re-cutting the descriptor. A minimal authenticated operator-service layer is
pulled into A's scope; B extends it.

## DEC-007 (2026-08-20): Public rotation-failure policy for full-QUAL DKG

Full-QUAL ceremonies mean one unresponsive operator aborts rotation. Policy:
public retry ladder with fresh sessions; after three failed sessions the
sanctioned path is a membership transition excluding the non-completing
operator under the approval quorum; if no successor exists at retire_at the
epoch retires anyway (availability sacrificed, no silent extension). The
Pedersen abort-on-complaint/bias tradeoff is recorded in the spec for the
external cryptographic review.

## DEC-006 (2026-08-20): Membership transition is defined once, in Workstream C

The signed membership-transition primitive (approval quorum by previous-epoch
operators inside EpochDescriptor v1) is Workstream C protocol. Workstream B
governance tooling and PROD-07 accountability consume and extend it; they do
not define a second transition mechanism.

## DEC-005 (2026-08-20): Canonical binary encoding for all new signed objects

New lifecycle and identity objects (EpochDescriptor, approvals, activations,
revocations, erasure statements, SiteDescriptor) compute digests/signatures
over a specified canonical binary encoding (fixed field order, big-endian
integers, length-prefixed strings/lists, no floats). JSON is transport only.
Existing objects (topology v3, DKG certificate v1, batch descriptor v2) are
frozen as-is and embedded by exact bytes, preserving their digests and all
existing evidence. Rationale: Go json.Marshal is implementation-defined and
cannot support cross-platform vectors or a second implementation.

## DEC-004 (2026-08-20): Envelope window vs. active window

Topology v3 requires the DKG inside its own validity window, which conflicts
with prepare-while-active rotation if the window means "active". Resolution:
the topology window is the epoch's validity envelope (ceremony + DKG +
active + grace); the descriptor's activate_at/retire_at define the ACTIVE
sub-window; envelopes of consecutive epochs overlap. No topology schema
change; the epoch manager alone decides which epoch is ACTIVE.

## DEC-003 (2026-08-20): Epoch lifecycle extends the existing ceremony stack

Workstream C will generalize nomad-testnet's signed topology + DKG certificate
into a canonical EpochDescriptor and lifecycle state machine rather than
replacing the ceremony code. Rationale: DKG-01..12 are proven fail-closed at
fixture level with immutable evidence; rewriting would discard evidence and
risk regressions. New wire objects get new versioned domain strings; existing
domains keep their meaning.

## DEC-002 (2026-08-20): Execution artifacts live in nomad-protocol/production

workstreams.json is the requirement registry for GOAL.md; readiness.json
remains the sole authority for PROD gate status (CI-enforced against the DoD
table). workstreams.json never duplicates PROD statuses, only ownership
mapping, to avoid dual-source drift.

## DEC-001 (2026-08-20): Full goal text committed as production/GOAL.md

The complete production goal is versioned in-repo and referenced by the
session goal condition, so any future session recovers the full requirement
set from the repository alone.
