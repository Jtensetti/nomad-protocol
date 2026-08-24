# External blockers

Genuine external dependencies that cannot be produced autonomously. Everything
up to each boundary is (or will be) completed so the external party performs
only the listed action. Never fabricate these.

## EB-1: Apple Developer ID signing and notarization credentials

- **Missing:** Developer ID Application certificate + Apple notarization
  credentials for Nomad-browser releases.
- **Why not autonomous:** requires a paid Apple Developer Program membership
  and legal identity; credentials must never be created or held by an agent.
- **Where obtained:** <https://developer.apple.com/programs/> (enrollment),
  then an App Store Connect API key or app-specific password for `notarytool`.
- **Where configured:** protected GitHub environment secrets in
  `Jtensetti/Nomad-browser` used by the existing fail-closed release workflow:
  `MACOS_CERT_P12_BASE64`, `MACOS_CERT_PASSWORD`, `NOTARY_KEY_ID`,
  `NOTARY_ISSUER_ID`, `NOTARY_PRIVATE_KEY` (names per the workflow file; set
  values only in GitHub environment secrets, never in the repo).
- **Verification afterward:** re-run the release workflow; it must show
  Developer ID identity check, hardened runtime, notarization `Accepted`,
  stapling and `spctl` Gatekeeper assessment, and attach the notarization log
  and artifact digests as immutable evidence.
- **Already complete:** the protected fail-closed signing/notarization
  workflow exists and is validated without credentials (commit `b19710b`).

## EB-2: Independently administered operators (>=3, ideally 5)

- **Missing:** three to five genuinely independent administrators (separate
  people/organizations, accounts, billing, credentials, hosts, regions) to run
  Nomad operators and perform DKG/topology attestation themselves.
- **Why not autonomous:** administrative and legal independence cannot be
  synthesized; five processes under one admin are one trust domain.
- **Where obtained:** recruit operators (e.g. privacy-community organizations,
  universities, individuals) willing to run the operator package.
- **Where configured:** each operator follows
  `nomad-testnet/deploy/OPERATOR_ONBOARDING.md`, generating all private
  material locally and publishing only signed public enrollments.
- **Verification afterward:** signed enrollments from distinct identities,
  WAN DKG transcript across their hosts, per-operator attestations of the
  activated epoch descriptor, and (for PROD-05) witnessed key custody/erasure
  statements from each administrator.
- **Already complete:** the onboarding package is written and the lifecycle
  tooling exists. `nomad-testnet/deploy/OPERATOR_ONBOARDING.md` is addressed
  to an external administrator and needs no other project knowledge; it
  covers identity generation, reading and attesting the draft, verifying the
  signed topology, the DKG, serving, rotation and erasure, and states what
  an operator will never be asked for. `nomad-operator` provides init,
  inspect, attest, verify and erase; `deploy/RECOVERY_RUNBOOK.md` covers the
  failure cases and is exercised by TestRecoveryDrill. **The only remaining
  action is recruiting the people.**

## EB-3: Multi-region WAN test infrastructure

- **Missing:** hosts in >=3 regions/providers (with IPv4+IPv6) for real WAN
  campaigns and 72-hour captures; requires cloud accounts and payment.
- **Why not autonomous:** infrastructure costs money and accounts that are
  not available in this execution environment.
- **Where obtained:** any three diverse providers/regions (can be modest VMs);
  operator machines from EB-2 can double as WAN endpoints.
- **Where configured:** Workstream E ships deployment scripts and an exact
  run procedure; secrets are limited to ordinary SSH access held by the user.
- **Verification afterward:** capture archives with kernel timestamps and
  digests from each region, matching the preregistered tolerances, attached
  as immutable CI/release artifacts.
- **Already complete / in progress:** dedicated-bridge pcap gate exists;
  Workstream E is building the netem matrix, blind-classification harness and
  72-hour capture harness validated locally.

## EB-4: Independent external assessors and red team (PROD-04, PROD-29, PROD-30)

- **Missing:** independent cryptographic, systems, browser and
  privacy/traffic-analysis assessors, plus a release red team, none of whom
  are project maintainers or Claude agents.
- **Why not autonomous:** independence is the security control; an agent
  self-review is QA, not an audit, and must never be recorded as one.
- **Where obtained:** commercial audit firms, academic groups, or established
  independent researchers chosen by the project owner.
- **Where configured:** assessors receive the audit package produced under
  Workstream I (frozen target, spec, threat model, claim/test matrix,
  vectors, reproducible builds, captures, limitations).
- **Verification afterward:** publicly identifiable final reports, recorded
  findings, and assessor-verified remediation with zero unresolved Sev1/Sev2.
- **Already complete / in progress:** specifications, published test
  vectors, adversarial test suites and claim documentation are being
  assembled continuously; two internal adversarial reviews have already run
  and their findings are fixed with regressions. Booking assessors is
  wall-clock bound and should start now rather than after implementation.

## EB-5: Second independent protocol implementation (PROD-03)

- **Missing:** an interoperating implementation of the public wire protocol
  built without sharing protocol code.
- **Why not autonomous:** independence requires a separate implementer; an
  agent-written second implementation in this project shares authorship and
  cannot count as independent for PROD-03.
- **Where obtained:** external contributor/team, aided by the frozen
  specification and conformance vectors from PROD-01 work.
- **Verification afterward:** cross-implementation transcript corpus and a
  successful conformance run in CI.
- **Already complete:** the formats an implementer needs are published and
  enforced. A nine-vector conformance corpus covers the hop cell, the uplink
  cell frame, the object manifest and signed topologies, sealed by a digest
  over the ordered set and identical on 32-bit and 64-bit builds;
  `nomad-testnet/conformance/COMPATIBILITY.md` names all 58 frozen labels with
  the refusal behaviour for each, enforced by a test that fails if the code
  gains a version the matrix omits. What remains for the second party is only
  to read them and disagree.

## EB-6: Two-person release decision (PROD-30)

- **Missing:** a second human release approver.
- **Why not autonomous:** the control exists precisely to prevent a single
  actor (human or agent) from approving a release alone.
- **Where obtained:** project owner designates a second maintainer.
- **Verification afterward:** signed release decision recorded in the release
  evidence with two distinct identities.

## EB-7: Project release key for the signed specification tag (PROD-01)

- **Missing:** a signing key under project control, and a signed tag on the
  frozen specification.
- **Why not autonomous:** a release key is long-lived signing authority over
  what the project asserts the protocol *is*. An agent must not create or hold
  one, and a key generated here would prove only that this session signed
  something. This is not an independence requirement -- the maintainer may
  sign their own specification -- it is a custody one.
- **Where obtained:** the project owner generates the key on hardware they
  control (a hardware token is preferable to a file), publishes the public
  half in the repository, and keeps the private half off any machine an agent
  can reach.
- **Where configured:** `git config user.signingkey`, then
  `git tag -s protocol-v1 -m "..."` on the commit that freezes the
  specification. The public key belongs in the repository so a verifier needs
  nothing but the clone.
- **Verification afterward:** `git tag -v protocol-v1` succeeds against the
  published public key, and the tagged tree's conformance corpus digest
  matches the one recorded in the evidence index.
- **Already complete:** everything the tag would cover. The corpus, the
  compatibility matrix, the downgrade rule and the cross-architecture check
  are in place and enforced; the specification content is written. What is
  missing is a signature over it, and only custody prevents that.

## What none of these are

None of these seven is a design problem, and none is waiting on further
engineering here. Each names a person, a credential, a machine or an elapsed
duration. Where a blocker sits between "the work is done" and "the gate is
MET", the work is described above as already complete so that the external
party performs exactly one action and no more.

Two further gates are held by the same principle without appearing here,
because they need a second party rather than an external one: PROD-02 (a
reviewed threat model) and PROD-27 (a privacy review). Both artifacts are
finished; in each case the author must not also be the judge. A maintainer who
did not write them can close either without any external dependency at all.
