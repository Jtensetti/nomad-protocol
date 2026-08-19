# Definition of Done: Nomad v0.1 research reference

Last reviewed: 2026-08-19.

## Release scope

Nomad v0.1 is done when it is a runnable, falsifiable **research reference
implementation** of the reader-side architecture. It is not a deployable
anonymity network, an anonymous publisher system or an isolated production
browser.

A criterion is MET only when the implementation is present at the locked
release-candidate commit and the cited GitHub Actions checks pass. A prose
claim, placeholder workflow or unit test that bypasses the composed data path
does not count.

## Acceptance criteria

| ID | Required result | Automated evidence | Status |
|---|---|---|---|
| DOD-01 | Every changed Go component compiles, passes race-enabled tests and passes go vet. | Component PR checks plus the composed nomad-testnet check. | MET |
| DOD-02 | The Selection Firewall exists in the dependency graph: network control cannot import semantic selection/reconstruction, and private packages cannot import planner/fabric/mix. | go list -deps gates in nomad-testnet and Nomad-browser. | MET |
| DOD-03 | The public plan fixes count, 1200-byte size, cadence, peer slot and global cadence index without a private-reader input. | nomad-selection-firewall tests. | MET |
| DOD-04 | The scheduler emits individual cells on absolute deadlines, fails instead of catch-up bursting and sends actual 1200-byte UDP datagrams. | nomad-constant-rate-fabric loopback tests. | MET |
| DOD-05 | Distinct private worlds—including “Iran military systems” and “sourdough pizza”—produce the same normalized captured-wire count, size, peer selection, encrypted payload and public plan under equal public state. | nomad-testnet multi-peer UDP capture tests. | MET |
| DOD-06 | Cover capacity carries useful coded work when available; a fixed 504-byte RLNC generation packet supports systematic coding, random coding, re-encoding, incremental rank tracking and exact reconstruction. | nomad-rlnc tests and composed reconstruction from captured cells. | MET |
| DOD-07 | A mix round preserves payloads, replaces ciphertext representations and has a verified shuffle proof; the reference committee runs at least two independently randomized rounds. | Kyber Neff sequence-shuffle tests in nomad-anytrust-mix-sim and the composed testnet. | MET |
| DOD-08 | Reconstructed bytes are accepted only after SHA-256 commitment and Ed25519 verification over nomad-object-v1 plus SHA256(content); signed manifest metadata and length are also checked. | nomad-local-reconstruction tamper tests and composed captured-cell test. | MET |
| DOD-09 | Query embedding, basin calculation and candidate ranking occur locally; the HTTP adapter accepts only literal loopback IPs, disables proxies and rejects redirects. | nomad-semantic-basins tests. | MET |
| DOD-10 | Browser-core resource loads resolve only through a signed bundle and verified local cache, while its egress contract denies ordinary browser networking and background services. | Nomad-browser cache, adapter, egress and dependency tests. | MET |
| DOD-11 | Private sibling composition is reproducible without a broad CI credential. | Commit-pinned component locks plus SHA-256 snapshot verification in testnet/browser CI. | MET |
| DOD-12 | Status, protocol and threat-model documents distinguish tested facts from assumptions and production gates. | This repository review and required-document checks. | MET |

## Locked release-candidate evidence

| Repository | Commit |
|---|---|
| nomad-constant-rate-fabric | 19c40723c3518f51ad34867a32dfd755cceda023 |
| nomad-anytrust-mix-sim | 35aa0f84769023b92d108e511bad7af47c34bbd1 |
| nomad-rlnc | 463537740ee86f95aeb1cb65c3e2130300663f9a |
| nomad-local-reconstruction | 5aff4db34adec4f6d01a27f713fd84f0a3495ea6 |
| nomad-selection-firewall | 6e67690f6ed2125cd88dfd3c4da8c7c12d63664b |
| nomad-semantic-basins | 0cad8aa5c74f51b2d463a3a3febb62c17e4ae529 |
| nomad-testnet | b50536cb545448c00a9a04799d3d2620edd43d69 |
| Nomad-browser | 7f4e82c95e7c3457b23b168e00e7d2c5f104464e |

The lock records candidate heads, not a claim that draft pull requests have
been reviewed or merged.

## Claims this DoD permits

- Nomad v0.1 is a runnable research reference stack.
- The tested Go dependency graph enforces the intended network-to-cache-to-
  private-selection direction.
- Under the fixed loopback test profile, tested private query worlds do not
  change the normalized captured UDP trace.
- The tested mix preserves payloads and verifies Kyber Neff shuffle proofs.
- Objects reconstructed from captured cells are accepted only after exact
  cryptographic verification.

## Production gates outside v0.1

These are deliberately **not** waived by marking v0.1 done:

- independent cryptographic and systems-security review;
- threshold/DKG-based mix decryption and authenticated committee membership;
- replay, drop, delay, selective-failure and active-adversary accountability;
- WAN peer discovery, NAT traversal, congestion/churn experiments and Sybil
  resistance;
- long-horizon intersection and cache-availability analysis;
- basin inversion and membership-inference analysis;
- a publication airlock and anonymous deposit protocol;
- SiteID/key discovery, rotation and revocation;
- Firefox/Chromium enforcement at every DNS, socket, WebRTC, speculative-load,
  service-worker, extension, telemetry, crash-reporting and Safe Browsing path.

Until those gates pass, the phrases “production anonymity”, “anonymous
publishing” and “isolated Nomad browser” are not valid project claims.
