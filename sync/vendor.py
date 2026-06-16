#!/usr/bin/env python3
"""vendor — keep an edition's vendored copy of Org Tools in sync with this canonical repo.

    python sync/vendor.py sync  <edition-repo>   # copy canonical -> <edition>/vendor/ai-org-tools/
    python sync/vendor.py check <edition-repo>   # exit 1 if the vendored copy drifts (CI gate)

Single source of truth (here) + self-contained editions (in-repo, so box/dogfood stay offline) + drift
detection (check). The chosen hybrid home from ADR-0001.
"""
from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

CANON = Path(__file__).resolve().parent.parent
INCLUDE = ["tools", "registry"]                     # what gets vendored into editions


def _vendored(edition: Path) -> Path:
    return Path(edition).resolve() / "vendor" / "ai-org-tools"


def _diff(a: Path, b: Path) -> list[str]:
    """Recursively list paths that differ / are missing between canonical a and vendored b."""
    out: list[str] = []
    if not b.exists():
        return [f"missing: {b}"]
    cmp = filecmp.dircmp(a, b)
    out += [f"only-canonical: {a/n}" for n in cmp.left_only]
    out += [f"only-vendored: {b/n}" for n in cmp.right_only]
    out += [f"differs: {a/n}" for n in cmp.diff_files]
    for sub in cmp.common_dirs:
        out += _diff(a / sub, b / sub)
    return out


def do_sync(edition: Path):
    dst = _vendored(edition)
    for inc in INCLUDE:
        d = dst / inc
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(CANON / inc, d)
    (dst / "VENDORED.md").write_text(
        "# Vendored from ai-org-tools (canonical). Do not edit here — edit canonical and re-sync.\n"
        "CI checks this copy matches canonical (`sync/vendor.py check`).\n", encoding="utf-8")
    print(f"synced {INCLUDE} -> {dst}")


def do_check(edition: Path) -> int:
    dst = _vendored(edition)
    drift: list[str] = []
    for inc in INCLUDE:
        drift += _diff(CANON / inc, dst / inc)
    if drift:
        print("DRIFT — vendored copy is out of sync with canonical:")
        for d in drift:
            print("  " + d)
        return 1
    print("vendored copy matches canonical ✓")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("sync", "check"):
        print(__doc__); raise SystemExit(2)
    cmd, edition = sys.argv[1], Path(sys.argv[2])
    if cmd == "sync":
        do_sync(edition)
    else:
        raise SystemExit(do_check(edition))
