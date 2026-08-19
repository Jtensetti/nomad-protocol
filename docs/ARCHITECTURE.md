# Architecture

## Data path under investigation

```text
publisher object
    |
    +--> canonical bytes / commitment / signature
    |
    +--> encryption layer (not implemented by RLNC)
    |
    +--> equal-size coded symbols
             |
             v
      fixed-cadence fabric
             |
       mixing layer  [currently only a model]
             |
      re-encoding / replication
             |
             v
      distributed coded state
             |
             v
      local network cache
             |
      private selection domain
             |
      local reconstruction
             |
      commitment/signature check
             |
         accepted object
```

The arrows describe intended responsibilities. They do not imply that a complete payload-preserving pipeline exists today.

## Selection boundary

The reader implementation is split conceptually into two capabilities:

- **network capability:** traffic scheduling and protocol maintenance using public state,
- **selection capability:** private query processing, local ranking and reconstruction.

The design objective is that the selection capability has no authority to change the externally observable schedule. Browser and OS integrations can still violate this unless they are tested separately.

## Semantic basins

Basins are coarse similarity hints. They are not secret labels. Exposing them directly may enable inversion, membership inference or interest profiling; the current repository does not solve that problem.

## Mixing

The current mix repository does not carry application payload through a deployable re-randomizable encryption scheme. It models batch thresholding, permutation and representation replacement so that integration code can be written without pretending the cryptography is solved.
