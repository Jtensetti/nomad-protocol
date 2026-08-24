# Decision log

Engineering decisions with rationale. Newest first.

## DEC-012 (2026-08-24): lifecycle traffic is public-only; epoch-private keys are one-use

Normal rotation is one continuously running controller whose decisions depend
only on the signed chain, public retry policy and wall clock. It publishes
immutable artifacts and makes exactly one direct GET to each signed endpoint
per aligned tick: no proxy, redirect, alternate peer, immediate retry or late
catch-up. READY import must finish before the predecessor's signed retirement
boundary. This preserves the core invariant while making DKG, approvals,
activations and import automatic.

Only the Ed25519 operator identity may continue between epochs. KEX and DKG
keys are generated into a new canonical epoch file, and the verified chain
rejects reuse from **any** earlier accepted epoch, not merely the immediate
predecessor. Without the cumulative rule, epoch 3 could reintroduce an epoch-1
key and a later compromise would undo epoch-1 forward secrecy. Retry attempts
inside one epoch deliberately retain that epoch's keys and change only their
public session and start.

## DEC-011 (2026-08-24): descriptor signing uses validated detached artifacts

Production operators never receive a raw "sign this descriptor" primitive.
They validate the complete unsigned draft against their independently held
authority, chain and revocation state before recording its digest in a durable
anti-equivocation journal, then export one context-bound detached artifact.
Assembly accepts only strict artifacts for that exact digest, separates
outgoing approvals from incoming activations, and performs full descriptor
verification after insertion. This prevents an invalid draft from burning the
only journal slot and prevents callers from bypassing chain, revocation,
membership or role checks. DEC-012 now defines the public automatic transport
that carries these artifacts; the detached commands remain offline recovery.

## DEC-010 (2026-08-24): PROD-08 requires the complete live lifecycle boundary

PROD-08 is downgraded from MET to PARTIAL. A public-only planner, signed
descriptor model, erasure primitive and in-process recovery drill are
necessary but do not demonstrate the criterion as a whole. Promotion requires
one production path that automatically runs next-epoch DKG, gathers approvals
and activations, validates outputs, reaches READY, imports the descriptor,
activates only at the signed public boundary, retires the predecessor and
records erasure. It also requires a forward-secrecy experiment against the
persisted state of a live ceremony after later credential compromise. An
external test report for an older commit cannot verify a newer integrated
head. This is an evidence-boundary correction, not a redefinition of the
criterion.

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
