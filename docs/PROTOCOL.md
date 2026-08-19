# Protocol constraints and v0.1 encodings

This records the interoperating research profile. It is not yet a stable
Internet wire standard.

## Public traffic class

A traffic class defines:

- cells per epoch;
- cell size;
- exact cell interval;
- peer-slot count;
- public planning seed;
- public maximum scheduler lateness.

The planner produces an epoch, slot, global cadence index, epoch-relative
offset, peer slot and size for every emission. Private reader state is not an
input. A lost cell never adds a retransmission cell or catch-up burst; useful
work may only reuse a later cell that already exists in the public plan.

## Wire cell

The v0.1 profile uses an exact 1200-byte UDP payload:

| Region | Bytes | Meaning |
|---|---:|---|
| ElGamal sequence ciphertext | 1152 | 18 chunks × 2 compressed Ed25519 points × 32 bytes |
| Random representation padding | 48 | fresh filler, not application data |

The 1200-byte value is a versioned profile constant, not a claim that every
future traffic class must use this size.

## RLNC generation packet

The mix cleartext is exactly 504 bytes:

| Field | Bytes |
|---|---:|
| Magic/version | 4 |
| Generation ID | 16 |
| Source-symbol count K | 2 |
| Symbol size | 2 |
| Original object length | 4 |
| GF(2^8) coefficient vector | K |
| Coded data | symbol size |
| Random padding | remainder to 504 |

The generation ID is the first 16 bytes of:

    SHA256("nomad-generation-v1" || content_root)

Packet metadata is routing/decoding information, not authentication. Exact
object verification remains mandatory. RLNC provides loss tolerance and
re-encoding; it does not provide encryption, anonymity or pollution resistance.

## Mix batch and proof

Each 504-byte packet is split into 18 28-byte chunks. Every chunk is embedded
in an Ed25519 group point and ElGamal-encrypted. Kyber's sequence shuffle gives
all 18 rows the same secret column permutation and fresh encryption randomness.

The Fiat-Shamir proof domain is:

    nomad-neff-sequence-shuffle-v1

Sequence challenges bind the public key, input batch digest and output batch
digest. A round is accepted only if its proof verifies and its batch size is
unchanged. At least one honestly randomized relevant round is the anytrust
privacy assumption. The current profile does not specify committee identity,
threshold keys or accountability.

## Signed object manifest

The fixed v0.1 manifest is 228 bytes:

| Field | Bytes |
|---|---:|
| Magic/version | 4 |
| Exact object length | 8 |
| Public semantic basin | 8 |
| Deterministic generation ID | 16 |
| SHA-256 content root | 32 |
| Ed25519 public key | 32 |
| Object signature | 64 |
| Manifest signature | 64 |

The object signing message is:

    "nomad-object-v1" || SHA256(canonical_content)

The manifest signing message is the domain string
nomad-manifest-v1 followed by the canonical length, basin, generation, root,
public key and object signature fields.

This self-authenticates the manifest to its embedded key. It does not decide
which key belongs to a SiteID.

## Semantic basin

The reference quantizer is a seeded 64-bit random-hyperplane signature.
Hamming distance is a lossy similarity hint used only for local ordering.
Similarity never establishes object identity or correctness.

## Reconstruction and acceptance

A private decoder may add already-cached generation packets until rank K is
reached. Acceptance requires all of:

1. generation and dimensions remain consistent;
2. decoded length equals the signed manifest length;
3. SHA-256(decoded bytes) equals the manifest root;
4. the object signature verifies in the nomad-object-v1 domain;
5. the manifest signature verifies in the nomad-manifest-v1 domain.

## Browser bundle

A browser bundle is itself a signed Nomad object. Its canonical bytes map clean
local paths to exact object roots and canonical MIME types. Because that mapping
is inside signed content, an untrusted transport header cannot reinterpret a
resource. The browser adapter has no network fallback.
