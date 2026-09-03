#!/usr/bin/env python3
"""Synchronize the canonical OpenAPI helper into each portable skill."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tooling" / "quake_openapi.py"
TARGETS = (
    ROOT / "plugins/quake-openapi/skills/quake-openapi-navigate/scripts/quake_openapi.py",
    ROOT / "plugins/quake-openapi/skills/quake-openapi-auth/scripts/quake_openapi.py",
    ROOT / "plugins/quake-openapi/skills/quake-installed-app-actions/scripts/quake_openapi.py",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when a bundled helper differs from the canonical source",
    )
    args = parser.parse_args()

    expected = SOURCE.read_bytes()
    stale: list[Path] = []
    for target in TARGETS:
        if target.exists() and target.read_bytes() == expected:
            continue
        stale.append(target)
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)

    if stale:
        action = "stale" if args.check else "updated"
        for target in stale:
            print(f"{action}: {target.relative_to(ROOT)}")
    if args.check and stale:
        print("Run: python3 scripts/sync_skill_helpers.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
