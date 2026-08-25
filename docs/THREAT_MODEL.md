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

### Where each capability stands

Every capability below states what is assumed, what is excluded, and where the
evidence is. `production/CLAIM_TEST_MATRIX.md` carries the per-claim rows; a
capability marked *not defended* has no row above `none` there, and the
project must not claim it.

| Capability | Position | Evidence |
|---|---|---|
| Global passive observation | Targeted. Cell size, destination and count are independent of private activity; **cell timing is not** — a reproducible difference is measured. **Cell *contents* are not opaque at the operator relay layer** — see below. | CLAIM_TEST_MATRIX reader path; the timing row is CONTRADICTED, see EVIDENCE_INDEX E-08 |
| Malicious peers | Targeted. A peer that is not in the signed topology gains nothing by existing, and abusive peers are refused per reason at no storage cost. | eclipse, Sybil and abusive-peer rows, adversarial |
| Compromised minority mixers | Targeted, under the anytrust assumption: privacy holds while at least one mixer in the chain is honest, and correctness holds against a minority under the `t`-of-`n` threshold. A majority-compromised committee is **excluded** — it can decrypt, and no protocol mechanism here prevents that. | shuffle-chain forgery, substituted-signer, non-re-randomising and partial-chain rows, adversarial |
| Replay | Targeted, at three boundaries: cells, shuffle chains across epochs and committees, and decoder admissions. | chain-replay, abusive-peer and duplicate-budget rows, adversarial |
| Delay and drop | Targeted for the invariant that matters: loss never produces catch-up traffic. Availability under sustained loss is **not claimed**. | burst-ceiling row; ADMISSION_AND_RATE_CONTROL.md |
| Injection | Targeted. Systematic pollution is refused before admission against signed commitments; dense coded pollution is **not preventable** over GF(2^8) and is bounded by budget and caught at object verification. | pollution rows, adversarial; POLLUTION_AND_RESOURCES.md |
| Sybil pressure | Targeted structurally rather than economically: admission consults a signed topology, never a population, so identities cannot be bought into relevance. Fair *allocation* among admitted sessions is **not claimed**. | Sybil and per-session quota rows, adversarial |
| Endpoint fallbacks | Targeted at the adapter: no failure mode falls back to ordinary networking. Whole-binary egress capture is **missing**, so the claim is bounded to the adapter rather than the shipped browser. | adapter failure-mode row, adversarial; egress-capture row is `none` |
| Long-horizon correlation | **Not defended, and not claimed.** The adversary is assumed capable of it; no mechanism here bounds intersection over repeated sessions, and no measurement has been run. Requirement E-10 is NOT_STARTED. | none |

The last row is the one most likely to be over-read. Fixed-rate cover bounds
what a single observation reveals; it says nothing about what many
observations reveal in aggregate, and Nomad has not measured that.

### The operator-to-operator hop header is not encrypted

The 48 bytes after the mix ciphertext in every relay cell are authenticated
but sent in the clear. A passive observer of a link reads, without attacking
anything:

- the **work flag**, which separates relayed work from cover perfectly. This
  is known and is why publisher traffic uses a different cell profile
  (`PUBLICATION_INGRESS.md`); `live/uplink/distinguisher_test.go` measures the
  separation.
- the **stream ID**, 16 bytes derived from the batch payloads. A relay
  re-seals a cell with its own sender slot and sequence and leaves the rest of
  the header as it arrived, so the same identifier appears at every hop the
  batch takes. Measured in
  `live/node/linkability_test.go`: cells emitted by a relay carry the ingress
  stream ID unchanged, so an observer links a batch's ingress hop to its
  egress hop by reading bytes 1164..1180. No correlation attack is needed.
- the **batch coordinates**, ordinal and size.

What this does and does not mean. It does not break the reader claim: relay
work is scheduled by public replication policy, not by any reader's activity,
so the observable is the same whichever object a reader wants. It does not
break publisher anonymity at the airlock either, because the shuffle changes
the payloads and the stream ID is a hash of them, so the identifier on the far
side of the mix is unrelated to the one on the near side.

What it does mean is that the relay fabric provides **no unlinkability between
hops** for the traffic it carries, and nothing here bounds what that reveals
about operator relay patterns over a long horizon. Encrypting the header under
the existing pairwise hop key would remove the property, at the cost of a wire
format change that invalidates the published conformance vectors — a decision
for the protocol freeze, not a change to make quietly before it. Recorded as
an open design question rather than as a defended position.

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

- independent review of the Kyber shuffle integration and a threshold
  committee key/decryption protocol,
- packet-capture tests under WAN loss, congestion, churn and active delay/drop,
- long-horizon intersection analysis,
- cache/availability side-channel analysis,
- basin inversion and membership-inference analysis,
- Firefox/Chromium engine and background-service isolation tests,
- publication-airlock and SiteID/key-lifecycle specifications,
- independent cryptographic and systems-security review.

## Bounded v0.1 evidence

The v0.1 loopback testnet captures actual 1200-byte UDP datagrams sent to four
publicly planned peer slots. It compares idle/active reader worlds and two
distinct query worlds, then reconstructs only from captured cells. This is
useful regression evidence for the reference implementation; it is not a
global-observer, congestion, browser-engine or deployment experiment.
