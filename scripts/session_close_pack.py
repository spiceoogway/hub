#!/usr/bin/env python3
"""Generate a compact session-close pack (Retain + NEXT + Git status).

Usage:
  python3 scripts/session_close_pack.py --repo . --out /tmp/session_close.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
from pathlib import Path


def run(cmd: list[str], cwd: str) -> str:
    try:
        return subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f"<error: {e}>"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="/tmp/session_close.md")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.out)

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], str(repo))
    status = run(["git", "status", "--porcelain"], str(repo))

    changed = []
    if status and not status.startswith("<error"):
        for line in status.splitlines()[:20]:
            changed.append(line)

    ts = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        f"# Session Close Pack ({ts})",
        "",
        "## Retain (top 3)",
        "- [ ]",
        "- [ ]",
        "- [ ]",
        "",
        "## NEXT (first action next session)",
        "- [ ]",
        "",
        "## Git",
        f"- branch: `{branch}`",
    ]

    if changed:
        lines.append("- changed files:")
        for c in changed:
            lines.append(f"  - `{c}`")
    else:
        lines.append("- changed files: none")

    out.write_text("\n".join(lines) + "\n")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
