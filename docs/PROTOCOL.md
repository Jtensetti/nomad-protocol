# Protocol constraints

This document records cross-component constraints. It is not yet a wire-format specification.

## Cell

A traffic class defines a fixed externally visible cell size. Application objects must not change that size.

## Cadence

A traffic class defines a public emission cadence. Implementations must schedule cells individually at that cadence; emitting an epoch's cells as a burst is not equivalent.

## Epoch

Epochs are accounting/coordination windows for batch formation and public scheduling state. Private reader activity is not an epoch input.

## Coded symbol

The RLNC experiment represents a symbol as a coefficient vector and data vector over GF(2^8). Re-encoding forms new linear combinations. Encryption, authentication, generation identifiers and pollution resistance are separate concerns.

## Basin

A basin is a lossy local similarity signature derived from a vector representation. Basin proximity may guide local ranking or future privacy-preserving retrieval work. Exact object correctness never comes from basin proximity.

## Reconstruction

A client may combine already-available coded fragments until its decoder succeeds. The recovered bytes are accepted only after checking the expected commitment and signature.
