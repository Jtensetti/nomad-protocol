# Threat model

The threat model distinguishes **participation visibility** from **activity visibility**. A network observer may know that an endpoint participates in Nomad; the reader-side goal is to prevent that observer from learning which local object the endpoint is selecting or reconstructing from activity-dependent traffic.

## Adversary capabilities considered

Depending on the experiment, the adversary may:

- observe links globally,
- operate many intermediate nodes,
- correlate observations over long periods,
- drop, delay, replay or inject traffic around a modeled honest mixing boundary,
- probe public availability and cache state,
- know the protocol and all public scheduling inputs.

The adversary is not assumed able to break standard cryptographic primitives.

## Reader-side target

For two private reader states `R0` and `R1` under the same public traffic-class state, the target is that observable network behavior does not depend on which reader state is active.

Achieving this requires more than fixed packet sizes. Cadence, peer selection, congestion behavior, retransmission, cache maintenance, speculative browser networking and failure handling must also avoid private-reader inputs.

## Publisher-side target

After a publication has crossed a future anonymous deposit/airlock and has been independently replicated, protocol metadata should not provide a direct mapping from public object to original endpoint.

This does **not** claim perfect pre-deposit publisher anonymity. Selective isolation before first deposit can create an availability oracle.

## Endpoint boundary

The following are outside the network-protocol claim and require separate endpoint security:

- compromised OS or hardware,
- forensic seizure of plaintext or keys,
- malware in the trusted browser/process domain,
- identifying metadata or prose inside published content,
- extensions or browser services that make ordinary network requests.

## Work required before deployment claims

- reviewed payload-preserving mix construction,
- packet-capture tests under loss, congestion and churn,
- long-horizon intersection analysis,
- cache/availability side-channel analysis,
- basin inversion and membership-inference analysis,
- browser-engine isolation tests,
- independent cryptographic and systems-security review.
