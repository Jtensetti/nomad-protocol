# Threat model

## Reader security goal

For any two local reader actions `R0` and `R1`, the externally observable network transcript should be indistinguishable within the ideal model:

`T(R0) == T(R1)`.

This requires traffic schedule, size, peer-selection policy, network cache behavior and retransmission behavior to be independent of private local selection.

## Publisher security goal

After a publication has crossed an anonymous deposit/airlock and is independently replicated, the public object should not be linkable to the original network identity solely from protocol metadata.

This is weaker than perfect pre-deposit publisher anonymity. A global active censor capable of selectively isolating candidate publishers can create an availability oracle before new information enters the network. The architecture does not claim to make that causal fact disappear.

## In scope

- passive global observation,
- large colluding node sets,
- one-honest-mix/anytrust assumptions,
- active dropping/tagging as research tests,
- traffic-shape and selection side channels,
- semantic metadata leakage,
- compromised intermediate nodes.

## Out of scope

- compromised endpoint hardware or OS,
- forensic seizure of plaintext at an endpoint,
- malware inside the trusted browser domain,
- identity disclosure in the published content itself,
- cryptographic breaks of standardized primitives.

## Required falsification work

Before any deployment claim:

1. formal non-interference proof for Selection Firewall,
2. reviewed mix cryptography and active-attack proof,
3. long-horizon intersection tests,
4. cache/churn side-channel tests,
5. basin inversion and membership-inference tests,
6. packet loss/congestion tests proving application activity cannot affect observable transport,
7. independent security review.
