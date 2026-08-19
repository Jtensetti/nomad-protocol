# Nomad protocol research stack

Nomad is a research architecture for an **activity-unobservable, content-addressed information fabric**. The central design goal is not merely to encrypt a client-server relationship, but to avoid creating a necessary publisher-to-reader network relationship in the first place.

This repository is the shared specification, threat model and executable security-game harness. The implementation is intentionally split into six independently testable repositories:

1. `nomad-constant-rate-fabric` — fixed-size, protocol-scheduled cells.
2. `nomad-anytrust-mix-sim` — fail-closed anytrust batch-mixing research model.
3. `nomad-rlnc` — random linear network coding and re-encoding.
4. `nomad-semantic-basins` — local embeddings and coarse basin mapping.
5. `nomad-local-reconstruction` — local candidate selection, reconstruction orchestration and exact verification.
6. `nomad-selection-firewall` — non-interference boundary between private consumption and network scheduling.

## Status

**Research prototype, not an audited anonymity network.** The deterministic/data-structure components are executable and tested. The repository deliberately does not ship public-Internet peer discovery, censorship-evasion deployment, autonomous infrastructure acquisition or an unreviewed production mixnet cryptosystem.

## Core invariants

- Fixed externally observable cell size and schedule within a selected traffic class.
- Local read/search/reconstruction choices do not change network emission plans.
- Mix stages fail closed below their anonymity threshold.
- Exact recovered objects are cryptographically verified.
- RLNC is transport/coding, not encryption.
- Semantic basins are hints, not secrets.
- Publisher anonymity before first anonymous deposit is a harder problem than reader unobservability.

## Run the executable security games

```bash
go test ./...
go run ./cmd/security-games
```

Read `docs/ARCHITECTURE.md` and `docs/THREAT_MODEL.md` before treating any component as security-relevant.
