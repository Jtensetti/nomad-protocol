# Publication ingress: spike finding and uplink profile (draft v1)

Status: DRAFT. Records the result of the publication-ingress spike
(DEC-008) and specifies the client uplink traffic class that follows from
it. Not active protocol until the full airlock lands.

## Why the spike ran first

The execution plan originally assumed publication fragments could ride
"pre-existing fixed-size fixed-cadence cells". An internal evaluator
challenged that: the fixed-cadence fabric in the tree is
operator-to-operator, clients have only a downlink fetcher, and a
publisher-facing uplink does not exist. Since the shape of that uplink
determines what the epoch descriptor must encode, it was prototyped before
the descriptor was frozen.

## Finding: the operator cell profile cannot carry publication traffic

Measured, not assumed, in `nomad-testnet/live/uplink` (test
`TestCurrentProfileWorkCellsAreDistinguishable`). Cells were built exactly
as `live/node` builds them, and two independent passive classifiers were
run over 16 work cells and 16 cover cells:

| Classifier | Feature | Result |
|---|---|---|
| Header flag | `Flags & FlagWork` in the cleartext hop header | 32/32 |
| Ciphertext structure | payload region parses as compressed group elements | 32/32 |

Both separated work from cover perfectly on the version 1 profile. The hop
header was authenticated but not encrypted, so bytes 1152..1199 stated in
the clear whether a cell carried work, along with its stream identifier and
batch coordinates; and a work payload is a batch of ElGamal ciphertext
points while cover is uniform random, so even with the header removed the
two were trivially separable.

Hop cell version 2 encrypts the whole cell per link (see DEC-016), and
`live/uplink/distinguisher_test.go` now runs both classifiers against sealed
cells and requires both to fail. The measurement above is kept as the
before, on a cell in memory, because it is what the uplink profile was
designed against and because the two profiles solve different problems: the
relay profile is now indistinguishable to an observer of a *link*, while the
uplink profile is indistinguishable to the receiving operator as well.

**This does not contradict the reader claim the project already makes.**
Operator relay work is driven by public replication policy, so the
observable is the same whichever object a reader is interested in, and
reader non-interference is unaffected. What the finding establishes is
narrower and decisive: this cell profile cannot carry publisher uplink
traffic, because there the existence of work *is* the private fact that
must not be observable. Had the airlock been built on the assumption of
reuse, the resulting system would have announced every publication in
cleartext.

## Uplink profile v1

An uplink cell is exactly `fabric.CellSize` (1200) bytes:

| Region | Bytes | Content |
|---|---:|---|
| Sequence | 8 | big-endian counter, cleartext |
| Sealed body | 1192 | AES-256-GCM ciphertext and tag |

The sealed body covers a 1176-byte plaintext: a 1152-byte inner committee
ciphertext followed by 24 zero bytes. The sequence is the AEAD's associated
data, and the nonce is derived deterministically from the session key and
that sequence, so nothing random needs transmitting and a nonce cannot
repeat without a sequence repeat.

Two properties follow, and both are tested:

1. **A network observer cannot distinguish work from cover.** Every cell is
   a counter followed by a pseudorandom string of fixed length. Both
   classifiers above fail against it.
2. **The entry operator cannot distinguish work from cover either.** Cover
   is a *real* committee encryption of the reserved empty fragment,
   produced on the identical code path. After stripping the outer layer the
   entry operator holds a 1152-byte committee ciphertext in both cases.
   Only threshold decryption reveals which it was, and by then the mix
   boundary stands between ingress and released plaintext.

The second property is what keeps a malicious entry operator from being a
publication oracle. Its cost is that cover cells are mixed and threshold
decrypted like real ones; that cost is accepted, because the alternative is
an operator that learns exactly when each client published.

Session keys are derived by HKDF from the client's key agreement with the
entry operator, bound to network, epoch, topology digest and operator slot,
so a captured session cannot be replayed into another epoch or against
another operator.

## What is still open

- The uplink is specified and cell-level tested, but not yet wired to a
  running client, an entry operator service, or the deposit mailbox.
- `EpochDescriptor.uplink_profile` remains reserved and must stay empty
  until this profile is finalized; the descriptor already refuses a
  non-empty value.
- Cadence parameters (interval, and whether a client uplink runs whenever
  the client is online) are not yet fixed. Participation visibility is
  already inside the declared threat model, but the exact rate is a
  deployment decision that needs the WAN campaign in Workstream E.
- No packet-level two-world capture of a running publisher exists yet; the
  current evidence is cell construction, not a wire capture.

## Non-claims

- Cell indistinguishability is not publication anonymity. It removes one
  necessary leak; the deposit, mixing, threshold release and timing
  separation still have to hold, and none of that is implemented yet.
- Nothing here addresses an active adversary that selectively drops a
  target's uplink; that analysis belongs with the airlock's failure
  behavior.
