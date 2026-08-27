# Nomad engineering rules

The production goal is `production/GOAL.md`. The authoritative readiness state is `production/readiness.json` together with `docs/PRODUCTION_DEFINITION_OF_DONE.md`. `production/workstreams.json` tracks engineering work. Do not create parallel status journals.

## Repository roles

- `nomad-protocol`: specs, threat model, readiness registry and evidence index.
- `nomad-constant-rate-fabric`: fixed-cadence scheduler and UDP transport.
- `nomad-anytrust-mix-sim`: batch crypto, shuffle and DKG.
- `nomad-rlnc`: bounded network coding.
- `nomad-semantic-basins`: local embedding and basin quantization.
- `nomad-local-reconstruction`: signed manifest and exact object verification.
- `nomad-selection-firewall`: public emission planning and capability separation.
- `nomad-testnet`: production-path integration, deployment and adversarial tests.
- `Nomad-browser`: networkless client and release pipeline.
- `firefox-nomad` / `chromium-nomad`: engine integration contracts; not production priorities unless explicitly reactivated.

## Verification

Every Go repo: `go build ./...`, `go vet ./...`, `go test -race ./...`.
`nomad-testnet` additionally owns Compose/live, dependency and packet-boundary gates. `nomad-protocol` must pass `python3 scripts/check_docs.py`.

## Privacy invariant

Private user activity must never create, remove, alter, reschedule, accelerate, delay, retry or reroute an externally observable network event. Prefer losing or deferring work over emitting a private-dependent signal. Never add ordinary-network fallback or private-state-dependent catch-up traffic. Public planner APIs must not accept private query, object, reconstruction or publication state.

## Evidence rules

A production criterion becomes `MET` only when its own rule is satisfied by production-path implementation, positive and negative/adversarial tests at the named boundary, immutable evidence, and no unresolved Sev1/Sev2 findings. Where the criterion requires independent evidence, internal agent review is not sufficient. Never fabricate audits, operators, credentials or external evidence. Record durable evidence in `production/EVIDENCE_INDEX.md` and the authoritative registry, not in narrative progress files.

## Git and review

Start new work from current `main` on a focused short-lived branch. Do not route new work through historical `claude/*`, `agent/*` or other staging branches merely because they exist. Keep `main` green, never rewrite published history referenced by evidence, and do not merge security-sensitive work until the affected tests and relevant exact-head CI are green. Reconcile useful work onto current `main`; close superseded experiments instead of stacking more branches on them.

For security-sensitive changes, separate implementation from evaluation where practical. An internal evaluator is QA, not an independent external assessor. Keep the source tree and evidence chain minimal: every checked-in report, fixture or document must support a build, test, protocol rule, operator task or readiness claim.
