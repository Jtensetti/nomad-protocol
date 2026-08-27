# Decision log

Engineering decisions with rationale. Newest first.

## DEC-020 (2026-08-27): A refused deposit destroys publication work, and only a retained sealed cell can retry

Running the publication path as separate processes for the first time showed
that a publisher loses a fixed share of its work every epoch, silently, and that
neither side reports it.

The mechanism. A publisher emits at a constant cadence, by design, whether or
not it has work and whether or not anybody is listening. The airlock's deposit
window closes before the release boundary, by design, so the shuffle chain and
threshold decryption have a fixed budget. The two are independent, so every cell
emitted between the cutoff and the next epoch is refused. Measured across real
processes: 38-43% of cells in a short run at a three-second period; at the
default one-minute period with a fifteen-second cutoff it is 25% of every
period in steady state.

Being refused would be harmless if the publisher could send the work again, and
`PUBLICATION_AIRLOCK.md` says exactly that: deposits are idempotent so "a client
that cannot tell whether its uplink cell arrived -- and it cannot, since the
uplink carries no acknowledgement that would distinguish work from cover --
resends freely". The idempotence is real. What the specification does not say,
and what decides whether the property is usable, is *what* a client has to keep
in order to resend.

Two candidates, and only one works:

- **Retransmitting the byte-identical sealed cell** is idempotent. The airlock
  recognises the payload as one it already holds and consumes no second slot.
- **Re-sealing the same fragment** is not. The inner layer is a fresh
  encryption to the committee on every seal, so the second attempt presents a
  *different* payload for a held deposit slot, and the airlock refuses it as a
  conflict. It is right to refuse: a different payload for a held sequence is
  indistinguishable from an overwrite attempt, and resolving it silently would
  drop whichever publication lost.

The implementation keeps neither. `publish.Queue.Next` removes the fragment from
disk as it hands it out, and `deposit.Drain.Emit` seals it and retains nothing.
So the retry the airlock's idempotence exists to support cannot be performed at
all, and a work cell refused for any reason -- a closed window, a full epoch, a
datagram lost in transit -- is publication work destroyed.

This is recorded rather than fixed, deliberately. The fix changes what the
publisher holds and when it emits, which is the component the core invariant
constrains most tightly, and a wrong fix here is worse than the defect: the
obvious one -- keep the fragment and seal it again -- is precisely the case the
airlock refuses. Designing it, implementing it and judging it in the same breath
as discovering it is what the planner/implementer/evaluator separation exists to
prevent.

The shape a fix has to fit: the publisher retains the sealed cell rather than
the fragment; it retransmits it verbatim; the choice between retransmitting and
sealing fresh cover depends only on the public schedule and the publisher's own
queue, never on feedback from the operator, because there is none and inventing
one would be a private-state-dependent signal; the emission rate does not change,
since one cell goes out per tick either way; and what is retained is bounded,
because an unbounded retry buffer is a memory leak in the process that holds the
publication queue.

Two smaller things came out of the same run. Re-sealing produces different bytes
on the wire, so a retransmission is not distinguishable from any other cell by
repetition -- a concern worth checking and, having checked it, not a finding.
And `live/entry`'s first counters could not express any of this: one called
"deposited" counted cells the airlock had silently dropped, and one called
"refused" mixed authentication failures with cells that merely arrived outside a
window. A counter that cannot distinguish an attack from a schedule is not
instrumentation.

## DEC-019 (2026-08-26): Descriptors are distributed through a transparency log, and an unwitnessed chain cannot reach a publisher verdict

PROD-15's open blocker was that the recovery drill's step 6 showed a reader who
had not seen a recovery still accepting the attacker, with nothing bounding how
long that lasted. The chain already made rollback and equivocation detectable by
a verifier that sees both branches; what was missing was anything that made
anyone see both branches.

Descriptors now go into an RFC 6962 append-only log. A verifier accepts a
descriptor only with an inclusion proof against a checkpoint it has verified,
moves between checkpoints only with a consistency proof from the size it itself
holds, and stops issuing a publisher verdict once its checkpoint is older than
its freshness window.

Three choices in this are worth recording because the obvious alternative was
worse:

*The gate is structural, not advisory.* A chain built without a log view can
never return PUBLISHER_VERIFIED, and the witnessed and unwitnessed append paths
refuse to do each other's job. The alternative -- an optional distribution
argument -- would have meant that any deployment that forgot to wire it up
silently returned to exactly the unbounded case PROD-15 describes. That is the
kind of fallback the engineering rules forbid, and it would have been invisible
in precisely the deployments that needed the property.

*The freshness gate sits on the positive verdict only.* A contradicted claim is
still reported PUBLISHER_INVALID when the reader's log view is stale. Gating
the whole of Resolve would have traded a true negative for an absence, which is
strictly worse for the reader: it would tell someone "unknown" about a
publication the reader can prove is wrong.

*Distribution must not observe what a reader reads.* The obvious implementation
fetches a checkpoint or a proof when a user opens a site, which makes an
observable network event depend on private activity and violates the core
invariant outright. Instead the inclusion proof travels with the publication
over the same path as the object, and checkpoint refresh runs on a fixed cadence
that does not depend on what anyone is reading. It follows that a failed refresh
is never retried harder because a user is waiting -- that would be the
private-state-dependent catch-up traffic the invariant rules out. A reader whose
refresh fails goes stale and says so.

What this does not do is make the log honest. A log that signs two heads at one
size has equivocated, and the implementation produces transferable evidence
rather than preventing the act. Preventing it needs more than one log or
cosigning witnesses, which is a deployment decision and is recorded as an open
item rather than claimed.

Two defects were found and fixed while building it, both worth naming. Both
proof verifiers consumed the proof path root-to-leaf while the prover emits it
leaf-to-root, as RFC 6962 specifies; this passed a hand-traced example whose
decision sequence happened to be a palindrome and failed the exhaustive
all-sizes test. And the RFC 6962 split was computed by a doubling loop that
overflows on a size near the top of the uint64 range, after which the counter is
negative, the comparison never ends and the verifier spins forever allocating --
a denial of service reachable by anyone who can hand a reader a document, since
sizes come out of proofs.

## DEC-018 (2026-08-26): The uplink session is established in band, one-sided

The publisher read a shared secret from a file and the entry operator read the
same bytes from its own. That is a real deployment and it needs a channel that
distributes a per-publisher secret to a named operator before anything can be
published -- a channel that knows who publishes what, which is the fact the
whole airlock exists to keep from existing.

DEC-015 deferred this on the grounds that the 1200 bytes were spent and an
in-band handshake was a wire-format change. Two things changed that. The
wire-format cost was paid anyway for DEC-016, so the corpus and the second
implementation were already being regenerated. And the premise was wrong in a
way worth naming: it assumed the handshake had to fit *alongside* a fragment.
It does not. The first cell of a session carries the introduction instead of a
fragment, at the cost of one cell per session, and on the wire it is 1200 bytes
with an 8-byte counter like every other cell.

**One-sided, deliberately.** The publisher authenticates the operator against
the `kex_key` in the signed topology and proves nothing about itself. The
instinct is to make a handshake mutual; here mutual authentication would hand
the entry operator exactly the identity it must not have. Its only guarantee is
that somebody who verified the topology is speaking to it, and everything that
bounds abuse afterwards is per session.

**The session secret goes through the unchanged derivation.** The handshake
produces the same thing the file used to: 32 bytes fed into
`nomad-uplink-session-v1`. The data path, its published vectors and its second
implementation do not move because the way the secret is obtained changed.

**Three separated domains, and the reason is not symmetry.** The session
identifier is public -- the airlock derives deposit slots from it, so it appears
in state an operator can see. A domain collision between it and the session
secret is a one-character edit that publishes key material. It is a distinct
domain, and a test requires all three derivations to differ, because that is
the kind of defect no round-trip test notices.

**What was rejected:** an unauthenticated first cell with the key in the clear
and no tag (nothing binds the introduction to the epoch); a mutual handshake
(gives the operator an identity); and putting the ephemeral key in the 24 bytes
of existing padding (it does not fit, and shrinking the inner ciphertext to make
it fit would change the mix layer for the benefit of the link layer).

## DEC-017 (2026-08-26): The canonical topology encoding is specified, not inherited

The bytes every topology signature is computed over were the output of Go's
`encoding/json` on the reference implementation's structs. That is not a
specification, it is an implementation detail that happened to be reachable
from another language if you described it carefully enough — which the second
implementation did, and recorded as a defect while doing it.

**Specified instead:** members sorted by UTF-16 code unit, no whitespace,
minimal string escaping, integers only, an absent array as `[]`. Close to
RFC 8785, stricter about numbers: a fractional or exponential literal is
refused rather than given a canonical form, because every number in a Nomad
signed document is an integer and refusing the rest removes the entire
floating-point half of JCS.

**Two of the three inherited quirks were live.** Struct-declaration order meant
inserting a field in the middle of a struct would silently change the signed
bytes of documents that had not otherwise changed. An absent array as `null`
was the same class of accident.

**The third was latent, and that is the more interesting one.** Go's escaping
of `<`, `>` and `&` could not be reached by any valid document: every
free-form string in a topology is constrained by a pattern, a URL parser, an
RFC 3339 parser or base64, and none of those alphabets contains those
characters. The defect was real and unreachable at the same time. It is fixed
anyway, and a test pins the unreachability so that loosening a field turns
into a failing test rather than into two implementations disagreeing about a
signature. "The encoding is wrong but validation keeps the difference out of
reach" is two invariants pretending to be one, and only one of them is
written down anywhere.

**Cost:** the signed bytes changed, so the corpus was regenerated and the
second implementation ported — for the second time in one session, after
DEC-016. That is the cost DEC-015 was trying to avoid paying twice. Paying it
twice took an afternoon, and the alternative was carrying two known-wrong
formats into a freeze.

## DEC-016 (2026-08-26): The hop cell is encrypted per link. Supersedes half of DEC-015

DEC-015 deferred two wire-format questions to the freeze on the grounds that
each would invalidate the conformance corpus and the second implementation, and
that spending that cost twice was worse than spending it once. The reasoning
was sound and the conclusion was wrong for the first of the two, for a reason
DEC-015 did not weigh: the freeze is what the deferral was waiting for, and the
unencrypted header was itself a blocker on the freeze. Deferring a change to
the moment that the change is a precondition for is not a deferral, it is a
deadlock.

**Taken now: the hop cell is encrypted under the pairwise link key** — the
whole cell, payload and routing metadata, not only the header. Encrypting the
header alone would have left the second distinguisher in place: a work cell
carries mix ciphertext, which parses as compressed group elements, while a
cover cell is uniform random, and that separated the two perfectly without
reading a single header byte.

The cost DEC-015 named was paid rather than avoided. The corpus was
regenerated, the second implementation was ported, and both directions of the
cross-implementation check pass on the new format. That cost turned out to be a
day's work and it bought the evidence back: porting the second implementation
found a real specification gap (the two encrypted regions are not contiguous,
so "encrypt the payload and the metadata" has two readings that produce
different bytes), which is exactly what the second implementation exists for.

**The keystream is HMAC-SHA-256 in counter mode, not a block cipher.** That is
a protocol decision. It means an implementation needs SHA-256 and nothing else
to speak this format, which the second implementation demonstrates by being
written against the Python standard library, where there is no AES. At twenty
cells per second per link the arithmetic is free.

**Still deferred: the Ristretto-style group encoding.** DEC-015's second
question stands as recorded. It is a performance change with no privacy
consequence, the parallelised seal already clears the deployed interval, and
nothing about the freeze depends on it.

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
