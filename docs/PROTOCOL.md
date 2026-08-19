# Protocol components

This document defines interfaces, not a deployable Internet wire protocol.

## Cell

Every observable information-fabric unit has a fixed protocol-defined size inside a traffic class. Variable application objects are converted to equal-size encrypted/coded symbols before they reach the fabric.

## Epoch

Traffic schedules and mix batches operate in epochs. An epoch defines cell count, peer slots and the anonymity threshold. Local user activity is not an epoch input.

## Coded symbol

A coded symbol contains a coefficient vector and equal-size data vector over GF(2^8). It may be re-encoded by forming new linear combinations. Authentication/encryption is a separate layer.

## Basin

A basin is a coarse opaque identifier derived locally from a vector representation. Basin proximity is probabilistic discovery metadata; exact object correctness always comes from cryptographic verification.

## Reconstruction

A client may combine locally cached candidate symbols until a decoder has enough independent information. The resulting canonical object is accepted only if its commitment and publisher signature verify.
