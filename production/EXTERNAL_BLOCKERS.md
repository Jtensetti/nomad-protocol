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
- **Engineering boundary before evidence collection:** onboarding and
  recovery documents exist, and draft PR #16 head `74c830c` implements the
  automatic public lifecycle, persisted chains, retirement guards,
  revocation, exact epoch-key rotation/erasure and live later-compromise test.
  The CLI examples match the mandatory retired share and secret flow. The PR
  is unmerged and exact-head Actions still needs to execute, but the remaining
  evidence action here genuinely requires independent operators. Recruiting
  may start now; no independent-operator evidence may be claimed before those
  administrators execute it themselves.
- **Exact external handoff after that boundary:** each administrator generates
  its private material locally, returns only the signed enrollment and public
  endpoint, follows the versioned runbook on its own host, and publishes the
  resulting DKG/activation/retirement evidence. Project maintainers must not
  generate, copy or escrow an operator's private material.

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
- **Engineering boundary before signing:** the corpus, compatibility matrix,
  downgrade rule and cross-architecture check exist, but PROD-01 still lacks a
  published conformance schema and a single normative account of all state
  transitions, errors and timeouts. The protocol is not frozen. Do not create
  or sign `protocol-v1` until those blockers are closed and the release target
  is fixed.
- **Exact external handoff after that boundary:** the project owner verifies
  the frozen commit and corpus digest, signs that exact commit with the
  project-controlled key, and publishes only the public key and signed tag.

## EB-8: GitHub Actions runner availability

- **Missing:** a runner that actually starts the required repository
  workflows. Draft PR #16 run `32757136789` on exact head `74c830c` failed in
  the `unit` job with `steps: null` and no logs; `live-compose` and `release`
  were skipped. Earlier runs `32746518775` and `32737789012` have the same pattern.
  The same zero-step failure pattern affects the current Nomad repositories.
- **Why not autonomous:** Actions enablement, billing/minutes budgets and
  self-hosted-runner registration are account/organization controls not
  exposed to repository code or the GitHub connector.
- **Exact minimal handoff:** the owner opens GitHub repository/organization
  **Settings → Actions** and **Billing/Budgets**, enables Actions for these
  private repositories and restores hosted-runner capacity, or registers a
  trusted ephemeral self-hosted runner. No repository secret is required for
  the unit/Compose jobs.
- **Verification afterward:** rerun workflow `32757136789`; `unit` must show an
  assigned runner and execute checkout, formatting, dependency gates, build,
  vet, race, component, conformance and platform steps; `live-compose` must
  then execute and pass. Preserve the run URL and artifact digests against
  exact head `74c830c`.
- **Alternative:** a complete external test report from exact head `74c830c`
  may satisfy evidence rule item 4, but it must include every required command
  and immutable digests; the older 2026-08-21 report cannot be reused for this
  head.

## What none of these are

Each blocker contains an irreducibly external action: a person,
credential, machine, independent organization or elapsed duration. That does
not imply all adjacent engineering is complete. EB-2 and EB-7 explicitly name
their remaining engineering boundary so an external party is not asked to
validate a moving or incomplete target.

Two further gates are held by the same principle without appearing here,
because they need a second party rather than an external one: PROD-02 (a
reviewed threat model) and PROD-27 (a privacy review). Both artifacts are
finished; in each case the author must not also be the judge. A maintainer who
did not write them can close either without any external dependency at all.
