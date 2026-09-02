#!/usr/bin/env python3
"""Every test the claim matrix names must exist.

A matrix row is a claim plus the test that evidences it. A row naming a test
that does not exist evidences nothing, and reads exactly like a row that does
-- which is the failure the matrix was written to prevent, occurring inside
the matrix.

This found two such rows. One of them named
TestARelayedCellCarriesItsStreamIDOnwardInTheClear against the claim "relay
hops are unlinkable to a passive observer": a test whose name asserts the
opposite of the claim beside it, left behind when the hop header was encrypted
and the real test renamed.

The code repositories are siblings of this one. When they are not present the
script says what it could not check and exits non-zero only if
NOMAD_REQUIRE_SIBLING_REPOS=1 says they were supposed to be -- a skip that
looks like a pass is the same failure one level up.
"""

import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SIBLINGS = [
    "nomad-testnet", "nomad-anytrust-mix-sim", "nomad-constant-rate-fabric",
    "nomad-local-reconstruction", "nomad-rlnc", "nomad-selection-firewall",
    "nomad-semantic-basins", "Nomad-browser",
]
DOCUMENTS = ["production/CLAIM_TEST_MATRIX.md", "production/EVIDENCE_INDEX.md"]
# The index is a historical record and may name a test that was removed, but
# only one listed here, with a reason. The matrix may not: a claim is evidenced
# by a test that exists or it is not evidenced.
REMOVED = "production/removed-tests.txt"

CITED = re.compile(r"`((?:Test|Fuzz)[A-Za-z0-9_]+)`")
DEFINED = re.compile(r"^func ((?:Test|Fuzz)[A-Za-z0-9_]+)", re.M)


def defined_tests() -> tuple[set[str], list[str]]:
    found, missing_repos = set(), []
    for name in SIBLINGS:
        directory = ROOT.parent / name
        if not directory.is_dir():
            missing_repos.append(name)
            continue
        for path in directory.rglob("*_test.go"):
            found.update(DEFINED.findall(path.read_text(errors="replace")))
    return found, missing_repos


def main() -> None:
    defined, missing_repos = defined_tests()
    if missing_repos:
        print("cannot check cited tests: these repositories are not beside this one: "
              + ", ".join(missing_repos), file=sys.stderr)
        if os.environ.get("NOMAD_REQUIRE_SIBLING_REPOS") == "1":
            sys.exit(1)
        print("not a pass: nothing was checked")
        return

    removed = set()
    for line in (ROOT / REMOVED).read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped.startswith(("Test", "Fuzz")):
            removed.add(stripped)

    problems = []
    for document in DOCUMENTS:
        text = (ROOT / document).read_text()
        for number, line in enumerate(text.splitlines(), 1):
            for name in CITED.findall(line):
                if name in defined:
                    continue
                if name in removed and document != "production/CLAIM_TEST_MATRIX.md":
                    continue
                problems.append(f"{document}:{number}: cites {name}, which no "
                                f"repository defines. Either the citation is stale, "
                                f"or the test was removed on purpose and belongs in "
                                f"{REMOVED} with a reason")
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(1)
    print(f"every cited test exists ({len(defined)} test functions across "
          f"{len(SIBLINGS)} repositories)")


if __name__ == "__main__":
    main()
