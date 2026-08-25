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
| Hop header | 48 | per-link routing and authentication; see below |

The 1200-byte value is a versioned profile constant, not a claim that every
future traffic class must use this size.

Earlier revisions of this document described the last 48 bytes as "random
representation padding, fresh filler, not application data". That was true of
the mix layer and false of the wire: the region carries the hop header below,
and an implementation built from the old text could not interoperate at all.
The error was found by attempting a second implementation from this
specification (PROD-03), which is what that criterion is for.

### Hop header

The mix layer treats bytes 1152..1200 as padding and never parses them, so the
link layer uses them. The header authenticates one hop; it is **not**
end-to-end and carries no confidentiality — see `THREAT_MODEL.md` for what a
link observer therefore reads.

All integers are big-endian. Offsets are relative to the start of the header,
that is byte 1152 of the cell.

| Offset | Bytes | Field |
|---:|---:|---|
| 0 | 4 | magic, exactly `4E 48 43 01` (`"NHC"` and version 1) |
| 4 | 2 | sender operator slot |
| 6 | 2 | ordinal, this cell's index within its batch |
| 8 | 2 | batch size |
| 10 | 2 | flags; bit 0 set means the cell carries work |
| 12 | 16 | stream ID |
| 28 | 4 | hop sequence, per sender per link |
| 32 | 16 | authentication tag |

A **cover** cell has flags 0, and its stream ID, ordinal and batch size are all
zero. A **work** cell has bit 0 of flags set, a non-zero stream ID, a batch
size of 2..256, and an ordinal strictly below the batch size. Any other flag
bit set is invalid. A zero hop sequence is invalid. A receiver rejects a cell
whose sender slot is not the peer it received it from.

The stream ID of a work cell is the first 16 bytes of

    SHA256("nomad-live-stream-v1" || uint16(batch size) || payload_0 || ... || payload_n)

over the batch's 1152-byte ciphertexts in ordinal order, so it is stable across
hops. A relay re-seals a cell with its own sender slot and its own hop sequence
and leaves the remaining fields as they arrived.

### Hop authentication tag

The tag is the first 16 bytes of HMAC-SHA-256 under the pairwise key the two
operators share for the epoch. It is computed over, in order:

    "nomad-hop-cell-v1"
    topology digest                      (32 bytes)
    epoch                                (8 bytes)
    receiver operator slot               (2 bytes)
    length of the network identifier     (2 bytes)
    network identifier                   (that many bytes)
    cell[0 .. 1184]                      (the cell up to but excluding the tag)

Binding the digest, epoch, receiver and network identifier means a cell cannot
be replayed into a different epoch, network or peer even when the pairwise key
is unchanged. An all-zero pairwise key is invalid, as is an authentication
context with a zero digest, an empty network identifier or a zero epoch: each
fails closed rather than authenticating everything.

The tag region is zeroed before the tag is computed, so a verifier recomputes
over the cell with those 16 bytes cleared. Comparison is constant-time.

### Hop replay window

A receiver keeps, per sender and per epoch, the highest hop sequence seen and a
64-bit bitmap of the sequences below it. A sequence above the highest advances
the window; one within 64 below it is accepted once and then rejected; one
64 or more below the highest is rejected. Gaps are ordinary: hop sequences are
allocated per sender across all its peers, and a cell that fails locally before
reaching the socket returns its number rather than leaving a gap.

## Signed topology document

The topology is the root of trust: it names the operator set, their endpoints
and keys, the epoch, the validity window, the traffic class and the DKG
profile. Every other check in the system is relative to it, so an
implementation that cannot verify one cannot participate at all.

It was not specified here until an attempt to write a second implementation
found that it could not be (PROD-03). What follows is what the reference
implementation does. Read the last subsection before building on it: the
encoding it signs is defined by one language's library defaults, which is a
defect, not a design.

### Structure

A signed topology is a JSON object with exactly two members:

```json
{"document": { ... }, "signature": "<base64 Ed25519 signature>"}
```

The document's members, in this order:

| Member | Type |
|---|---|
| `version` | string, exactly `nomad-live-topology-v3` |
| `network_id` | string |
| `epoch` | unsigned integer |
| `not_before`, `not_after` | RFC 3339 timestamps |
| `traffic` | object: `cell_size`, `cell_interval_ms`, `max_lateness_ms`, `queue_capacity` |
| `dkg` | object: `threshold`, `session_id`, `start_at`, `phase_duration_ms` |
| `operators` | array of operator objects |

Each operator, in this order: `id`, `index`, `endpoint`, `partial_endpoint`,
`dkg_endpoint`, `identity_key`, `kex_key`, `dkg_identity_key`, `peer_plan`,
`attestation`. Keys are base64; `peer_plan` is an array of operator indices.

### Three signed messages

Each is a domain string concatenated with the canonical encoding below — no
length prefix, no separator — and all three use v3 domains.

1. **Draft digest.** Blank every operator's `attestation`, encode, then
   `SHA256("nomad-topology-draft-v3" || canonical)`. This is what each
   operator attests to, so attestations bind the same membership, endpoints,
   keys, window, traffic class and peer plans regardless of the order they
   were collected in.
2. **Authority signature.** `Ed25519` over
   `"nomad-topology-authority-v3" || canonical`, where the canonical encoding
   is of the document **with** attestations present.
3. **Topology digest.** `SHA256("nomad-topology-digest-v3" || canonical)`,
   over the same bytes as the authority signature. This is the 32-byte value
   the hop authentication tag binds to.

### Verification order

A verifier must, in this order: reject an input above the size bound; reject
**duplicate JSON object keys** before decoding anything, because a signature
check cannot catch them — each implementation verifies whatever it parsed, so
a duplicate key makes one accept what another refuses; reject unknown members
and trailing data; validate the document against its own rules and the current
time; check the authority signature against a **pinned** key, never one the
document names; then check every operator's attestation.

### The bytes on disk are not the bytes signed

A topology file is pretty-printed, with two-space indentation and newlines. The
canonical encoding below has no insignificant whitespace at all. A verifier
must parse the file and re-encode canonically; hashing the file as it found it
verifies nothing and is the first mistake to make here.

### The canonical encoding, and why it is a defect

The canonical encoding is the output of Go's `encoding/json` on the reference
implementation's structs. Reproducing it requires all of:

- members in the struct-declaration order given above, **not** sorted;
- no insignificant whitespace;
- `<`, `>` and `&` escaped as `\u003c`, `\u003e` and `\u0026` — a rule
  specific to Go's encoder that no JSON specification requires;
- an absent `operators` array encoded as `null`, not `[]`;
- every member always present, including empty strings and zeros.

This is written down so a second implementation is possible today. It should
not survive the protocol freeze. A canonical encoding defined by one
language's default library behaviour is not a specification: the HTML escaping
in particular is invisible until a `network_id` or an endpoint contains an
ampersand, at which point every signature over that document fails in one
implementation and verifies in another. A freeze should replace it with an
encoding that is canonical by definition — RFC 8785, or the length-prefixed
binary form the hop tag already uses. See `production/DECISIONS.md`.

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
