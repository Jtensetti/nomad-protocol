# Security properties under investigation

These are target properties, not proven guarantees.

## Reader action non-interference

Let `R` be private reader state and `P` the public inputs to network scheduling. For the network scheduler, the desired dependency is:

```text
observable emission plan = f(P)
```

not:

```text
observable emission plan = f(P, R)
```

The implementation work therefore tries to remove `R` from the scheduler's API and process boundary entirely. Packet-capture tests are still required because OS scheduling, congestion handling, caches and browser subsystems can reintroduce dependence outside that API.

## Object verification

A locally reconstructed byte sequence is not accepted merely because a decoder succeeds. Acceptance requires an expected content commitment and a valid publisher signature over the protocol-defined signing message.

This authenticates the recovered object relative to the supplied key/commitment. It does not solve key discovery, revocation or publisher identity policy.

## Mix unlinkability

The desired mix property is that an observer cannot link an input representation to its output representation beyond the information intentionally exposed by the batch protocol, assuming at least one relevant mixing contribution is honest.

No current Nomad repository implements a reviewed payload-preserving mix cryptosystem. `nomad-anytrust-mix-sim` is only a falsifiable model for batch/permutation plumbing.

## Publisher unlinkability

Reader-side non-interference does not remove the causal fact that new information must enter the network somewhere. A global active adversary that can selectively isolate candidate publishers may create an availability oracle before first deposit.

Any stronger publisher claim requires a separately specified deposit/airlock protocol and adversary model.
