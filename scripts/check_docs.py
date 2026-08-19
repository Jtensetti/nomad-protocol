#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "docs/DEFINITION_OF_DONE.md",
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
