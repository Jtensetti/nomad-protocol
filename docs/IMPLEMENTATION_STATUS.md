# Implementation status

Last reviewed: 2026-08-19.

| Area | Current artifact | Status | What is actually established |
|---|---|---|---|
| Cell representation | `nomad-constant-rate-fabric` | implemented experiment | Go type fixes cell size at 1200 bytes |
| Wall-clock cadence | `nomad-constant-rate-fabric` | implemented experiment | scheduler emits one cell per configured interval; no packet-capture claim |
| Real UDP transport | `nomad-testnet` | missing | issue/work item only |
| Batch permutation | `nomad-anytrust-mix-sim` | model | cohort bookkeeping and random permutation |
| Payload-preserving mix crypto | none | missing | no deployable construction exists in this project |
| Anytrust committee protocol | none | missing | repository name does not imply implementation |
| RLNC | `nomad-rlnc` | implemented experiment | GF(2^8) encode/re-encode/decode |
| Coded-symbol pollution resistance | none | missing | exact verification happens after decoding only |
| Local lexical embedding | `nomad-semantic-basins` | implemented baseline | deterministic lexical vector only, not semantic understanding |
| Local model adapter | `nomad-semantic-basins` | implemented adapter | loopback-only HTTP embeddings request |
| Basin quantization | `nomad-semantic-basins` | implemented experiment | seeded 64-bit random-hyperplane signature |
| Basin privacy | none | missing | inversion/membership leakage not solved |
| Exact reconstructed-object verification | `nomad-local-reconstruction` | implemented experiment | SHA-256 commitment + Ed25519 over domain-separated hash |
| Public/private client dependency split | `Nomad-browser` | implemented code structure | selector and planner are separate Go packages with dependency tests |
| Browser process isolation | Firefox/Chromium forks | missing | integration documents only |
| Reader packet-trace indistinguishability | none | missing | requires real transport and capture experiments |
| Publisher deposit/airlock | none | missing | architecture/threat-model concept only |

“Implemented experiment” means runnable code with tests. It does not mean independently reviewed, production-ready or secure against the full threat model.
