#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "docs/DEFINITION_OF_DONE.md",
    "docs/PRODUCTION_DEFINITION_OF_DONE.md",
    "docs/IMPLEMENTATION_STATUS.md",
    "docs/ARCHITECTURE.md",
    "docs/PROTOCOL.md",
    "docs/SECURITY_PROPERTIES.md",
    "docs/THREAT_MODEL.md",
]
FORBIDDEN_STALE = [
    "Payload-preserving mix crypto | none | missing",
    "Real UDP transport | \u0060nomad-testnet\u0060 | missing",
    "Reader packet-trace indistinguishability | none | missing",
    "currently only a model",
    "current mix repository does not carry application payload",
    "BROWSER_RC_COMMIT",
]

errors = []
documents = {}
for relative in REQUIRED:
    path = ROOT / relative
    if not path.is_file():
        errors.append(f"missing required document: {relative}")
        continue
    text = path.read_text(encoding="utf-8")
    documents[relative] = text
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"{relative}:{line_number}: trailing whitespace")

joined = "\n".join(documents.values())
for stale in FORBIDDEN_STALE:
    if stale in joined:
        errors.append(f"stale or placeholder claim remains: {stale!r}")

dod = documents.get("docs/DEFINITION_OF_DONE.md", "")
for number in range(1, 13):
    criterion = f"DOD-{number:02d}"
    if dod.count(criterion) != 1:
        errors.append(f"{criterion} must appear exactly once")
if dod.count("| MET |") != 12:
    errors.append("all twelve v0.1 DoD criteria must have explicit MET status")

registry_path = ROOT / "production/readiness.json"
if not registry_path.is_file():
    errors.append("missing production readiness registry: production/readiness.json")
    registry = {"criteria": []}
else:
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        errors.append(f"invalid production readiness registry: {exc}")
        registry = {"criteria": []}

production_dod = documents.get("docs/PRODUCTION_DEFINITION_OF_DONE.md", "")
allowed_statuses = {"NOT_MET", "PARTIAL", "BLOCKED", "MET"}
criteria = registry.get("criteria", [])
registry_ids = [item.get("id") for item in criteria if isinstance(item, dict)]
expected_ids = [f"PROD-{number:02d}" for number in range(1, 31)]
if registry_ids != expected_ids:
    errors.append("production registry must contain PROD-01 through PROD-30 in order")

table_statuses = {}
for match in re.finditer(
    r"^\| (PROD-\d{2}) \|.*\| (NOT_MET|PARTIAL|BLOCKED|MET) \|$",
    production_dod,
    re.MULTILINE,
):
    table_statuses[match.group(1)] = match.group(2)

if list(table_statuses) != expected_ids:
    errors.append("production DoD table must contain PROD-01 through PROD-30 in order")

met_count = 0
for item in criteria:
    if not isinstance(item, dict):
        errors.append("every production criterion must be an object")
        continue
    criterion = item.get("id")
    status = item.get("status")
    if status not in allowed_statuses:
        errors.append(f"{criterion}: unknown production status {status!r}")
    if table_statuses.get(criterion) != status:
        errors.append(f"{criterion}: document and registry status differ")
    evidence = item.get("evidence")
    blockers = item.get("blockers")
    if not isinstance(evidence, list) or not isinstance(blockers, list):
        errors.append(f"{criterion}: evidence and blockers must be lists")
        continue
    if status == "MET":
        met_count += 1
        if not evidence:
            errors.append(f"{criterion}: MET requires immutable evidence")
        if blockers:
            errors.append(f"{criterion}: MET cannot retain blockers")

score = re.search(r"Current score: \*\*(\d+)/30 production gates MET\.\*\*", production_dod)
if not score:
    errors.append("production DoD must contain the machine-checkable score")
elif int(score.group(1)) != met_count:
    errors.append("production DoD score does not match readiness registry")

for relative, text in documents.items():
    base = (ROOT / relative).parent
    for target in re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", text):
        if "://" in target:
            continue
        if not (base / target).resolve().is_file():
            errors.append(f"{relative}: broken Markdown link: {target}")

if errors:
    print("\n".join(errors), file=sys.stderr)
    raise SystemExit(1)
print("Nomad protocol documentation checks passed")
