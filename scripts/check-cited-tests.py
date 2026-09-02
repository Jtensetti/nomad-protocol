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

# A cited evidence path is a claim about where the evidence is, and it fails
# the same way a cited test name does: it reads exactly like one that resolves.
# This gate checked names and not paths, and an entry cited
# runtime/evidence/base64-differential/ -- gitignored in nomad-testnet and
# never committed, so it existed only on the machine that made it and vanished
# with the container.
#
# Scoped to paths that claim to be evidence locations rather than every
# backticked path, because the index also names branches, ratios and files that
# deliberately live somewhere else, and a check that flags those is one people
# learn to ignore.
#
# Checked against git rather than the filesystem, which is the whole point: the
# directory that caused this was present on disk and in no repository.
CITED_PATH = re.compile(r"`((?:[A-Za-z0-9_.-]+/)*(?:evidence|reports)/[A-Za-z0-9_./-]+)`")


def tracked_paths() -> set[str]:
    """Every path git tracks, in this repository and each sibling that is here.

    Sibling paths are recorded both bare and prefixed by the repository name,
    because the index cites them both ways.
    """
    import subprocess

    found = set()
    for directory in [ROOT] + [ROOT.parent / name for name in SIBLINGS]:
        if not (directory / ".git").exists() and not (directory / ".git").is_file():
            continue
        listing = subprocess.run(
            ["git", "-C", str(directory), "ls-files"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        if listing.returncode != 0:
            continue
        for line in listing.stdout.splitlines():
            found.add(line)
            found.add(f"{directory.name}/{line}")
    return found


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
    tracked = tracked_paths()
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
            for cited in CITED_PATH.findall(line):
                bare = cited.rstrip("/")
                if any(path == bare or path.startswith(bare + "/") for path in tracked):
                    continue
                problems.append(
                    f"{document}:{number}: cites the evidence path {cited}, which "
                    f"no repository tracks. Evidence nobody can open is evidence "
                    f"nobody can check; commit it, or cite where it actually lives")

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
    print(f"every cited test and path exists ({len(defined)} test functions "
          f"across {len(SIBLINGS)} repositories)")


if __name__ == "__main__":
    main()
