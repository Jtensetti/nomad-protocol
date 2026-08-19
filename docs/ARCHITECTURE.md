# Architecture

## Data flow

```text
publisher canonical object
        |
        +--> content commitment + publisher signature
        |
        +--> encryption (outside RLNC)
        |
        +--> equal-size coded symbols
                 |
                 v
        constant-rate information fabric
                 |
          anytrust batch mixing
                 |
          re-encoding / replication
                 |
                 v
          distributed coded potential
                 |
                 v
browser network cache ----> private selection cache
                                  |
                         local basin ranking
                                  |
                         local reconstruction
                                  |
                         hash/signature verify
                                  |
                             exact object
```

## Selection Firewall

The browser is conceptually split into two processes/domains:

- **Network domain:** traffic scheduling, utility work, coded cache maintenance. It does not receive private user intent.
- **Selection domain:** private semantic intent, local ranking, reconstruction and rendering. It has no API that changes network scheduling.

This non-interference boundary is the most important reader-side privacy invariant.

## Semantic basins

Basins are coarse routing/indexing hints. They must never be treated as confidential labels. A production design would require private retrieval/aggregation to stop basin metadata from becoming a new surveillance surface.

## Mixing

A real Nomad mix requires a reviewed verifiable/re-randomizable shuffle or equivalent construction. The simulator repository models the required property but intentionally does not invent production cryptography.
