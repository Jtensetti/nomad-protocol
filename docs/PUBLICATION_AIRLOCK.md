# Publication airlock (draft v1)

Status: DRAFT. Nothing here is active protocol until the online distributed
mix path (A-15) lands and this header changes.

Publishing is private activity. The airlock is the boundary where a
publisher's sealed fragment enters the network and, some fixed time later,
a plaintext fragment leaves it, with nothing observable in between that
depends on who published, whether anyone published, or how much.

It sits between two pieces that already exist: the client's local
publication queue (`nomad-testnet/live/publish`, which has no network
capability at all) and the uplink cell profile
(`nomad-testnet/live/uplink`, whose work and cover cells are
indistinguishable to both a network observer and the entry operator). The
airlock is what happens to a fragment after an entry operator receives it.

## The three things an observer must not learn

| Observable | Fixed by |
|---|---|
| when a batch closes and releases | a public schedule, never queue state |
| how many fragments are in a batch | a fixed batch size, padded with cover |
| which entering ciphertext became which released fragment | a verifiable shuffle chain across the whole committee |

Each is a separate mechanism, and each fails closed on its own.

## Release schedule

`Schedule` is public deployment policy carried in the signed epoch
descriptor: a genesis instant, a period, a deposit cutoff, and a batch size.
Every derived time is a pure function of those four values and an epoch
number:

    deposit window for epoch e = [genesis + e*period,
                                  genesis + e*period + (period - cutoff))
    release of epoch e         = genesis + (e+1)*period

There is no API by which a deposit moves any of these. `Seal` refuses to run
before the window closes even when the batch filled in the first second,
because closing early is itself the statement that the batch was full. The
cutoff exists so the shuffle chain and threshold decryption have a fixed
budget between the last deposit and the release, rather than a budget that
depends on how much work arrived.

## Deposits

A deposit is one client-sealed committee ciphertext: exactly one column of a
mix batch, and exactly the inner layer of one uplink cell. The airlock holds
them keyed by a client-chosen deposit ID.

- **Idempotent.** Re-offering the identical payload under an ID already held
  succeeds without consuming a second slot. A client that cannot tell whether
  its uplink cell arrived — and it cannot, since the uplink carries no
  acknowledgement that would distinguish work from cover — resends freely.
- **Conflicts are refused, not resolved.** A different payload under a held ID
  is an error. Overwriting would silently drop whichever publication lost.
- **Capacity is fixed and public.** A deposit beyond `BatchSize` is refused
  and waits for a later epoch. Growing the batch would publish the number of
  real deposits in the batch size itself. Refusal is invisible on the wire:
  the client keeps emitting uplink cells at the same rate either way.

## Sealing

At the scheduled instant the airlock produces a batch of exactly `BatchSize`
columns:

1. Real deposits are ordered by deposit ID, so the entry operator's view of
   arrival order is not carried into the batch even momentarily.
2. The remainder is filled with cover: real committee encryptions of the
   reserved empty fragment, produced on the same code path a client uses.
   Filler that was not a valid ciphertext would fail the shuffle proofs and
   announce itself; filler that was distinguishable from a real deposit would
   publish the count.
3. The whole set is permuted by a uniform draw from the system CSPRNG, so
   cover position does not announce how many real deposits preceded it.

The sealed batch is therefore the same size and shape whether nobody
published or the epoch filled. It is deliberately *not* reproducible: the
placement is a fresh draw each time.

## Shuffle chain

Every certified committee member shuffles the batch in turn, in the
committee's certified order, each producing a Neff sequence-shuffle proof.
`VerifyChain` re-verifies the whole chain from the sealed batch.

**Every member must appear exactly once, in order.** This is the anytrust
assumption made mechanical: the chain is unlinkable only if at least one
shuffler is honest, so a chain that skipped a member is not a shorter chain,
it is a chain with a smaller honest-party assumption. A missing member, an
extra round, members out of order, one member standing in for another, a
corrupted proof, a proof borrowed from another round, a substituted
ciphertext, a batch that grew or shrank, an output that is not a valid
ciphertext — each fails the epoch closed. There is no partial-chain path and
no degraded mode for an unreachable member.

## Release

Threshold decryption opens the chain's output. Cover is dropped **here and
nowhere earlier**: it is indistinguishable from a real deposit until it has
been decrypted, which is the entire point of it. The number of real fragments
is therefore known only to a party already holding threshold authority, and
never becomes part of the public record of the epoch.

A released fragment is not trusted for having come out of the airlock. It
still faces the ordinary object rules: exact hash, manifest signature, and —
where a publisher identity is claimed — the SiteID chain in
`SITE_IDENTITY.md`. The airlock provides unlinkability, not authenticity.

## Capability boundary

`live/airlock` must have no transitive path to a socket, a scheduler, or peer
selection. It decides when a batch closes and what goes in it; if it could
reach the transport, the release boundary could be made to depend on queue
state, which is the one thing the fixed schedule exists to prevent. The
boundary is enforced by an in-package architectural test and by a CI
dependency gate, and the package derives its deposit size from the mix
parameters rather than importing `live/hop`, which would pull in the
transport.

## What is claimed, and what is not

Claimed, and evidenced by tests at the package boundary:

- release timing is a pure function of public parameters, at every occupancy
  from empty to full;
- batch size and shape do not vary with deposit count, and every column
  including cover decrypts;
- deposits are idempotent, conflicts are refused, capacity does not grow;
- a restart re-derives the same window and accepts the client's resend;
- sealed position carries no stable information about arrival order;
- every deviation from the full certified chain fails closed;
- a byte-level matcher holding the sealed batch and the chain output links
  ingress to release at chance, against a positive control where the same
  matcher is perfect when re-randomisation is removed.

**Not** claimed:

- The unlinkability measurement is one concrete matcher over a small sample.
  It shows that this matcher fails; it is not a proof of indistinguishability.
  The actual guarantee rests on the IND-CPA property of re-randomised ElGamal
  and on the anytrust assumption, and neither is established by a test.
- The anytrust assumption is not tested, because it cannot be: if every
  shuffler colludes, the chain is fully linkable by construction. What is
  tested is that the code requires every member to participate, so an
  adversary must corrupt all of them rather than some of them.
- Nothing here is a wire capture. Publish/no-publish equivalence at a real
  interface (A-04, A-12) is not evidenced.
- The online distributed mix path (A-15) does not exist. The chain is
  exercised in-process; a deployment needs per-operator shuffle and
  decryption services with authenticated inter-operator sessions, and the
  fixture bootstrap that holds every identity in one process is not a
  production ceremony.
- Deposits are held in memory. An operator restart loses them, and the client
  resends. That is the intended trade: the alternative is an operator that
  persists publication ciphertexts and a recovery step whose existence
  depends on how much was queued.
- Selective dropping by a malicious entry operator (A-09) is not analysed
  here.
