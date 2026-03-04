#!/usr/bin/env python3
"""Validate falsification-cycle bundle consistency (schema c8243e6).

Input JSON shape (example):
{
  "schema_version": "c8243e6",
  "rows": [
    {"target":"bro-agent","status":"replied","template_submitted":true,"candidate_seen":true,"verified_loop":false}
  ],
  "rollup": {"candidates_seen": 1, "submitted_templates": 1, "verified_loops": 0}
}

Usage:
  python3 scripts/falsification_validate.py --file /path/bundle.json
  cat bundle.json | python3 scripts/falsification_validate.py

Exit codes:
  0 = valid
  1 = validation_error
  2 = malformed input
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ALLOWED_STATUS = {"sent", "replied", "declined", "no_response_timeout", "failed"}
REQ_SCHEMA = "c8243e6"


def b(v) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in {"true", "yes", "1"}
    if isinstance(v, (int, float)):
        return bool(v)
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="Path to JSON bundle")
    args = ap.parse_args()

    try:
        data = json.loads(Path(args.file).read_text()) if args.file else json.load(sys.stdin)
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"malformed input: {e}"}))
        return 2

    errs: list[str] = []

    schema_version = data.get("schema_version")
    if schema_version != REQ_SCHEMA:
        errs.append(f"schema_version must be {REQ_SCHEMA}, got {schema_version!r}")

    rows = data.get("rows")
    if not isinstance(rows, list):
        errs.append("rows must be an array")
        rows = []

    rollup = data.get("rollup")
    if not isinstance(rollup, dict):
        errs.append("rollup must be an object")
        rollup = {}

    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            errs.append(f"rows[{i}] must be an object")
            continue
        st = r.get("status")
        if st not in ALLOWED_STATUS:
            errs.append(f"rows[{i}].status invalid: {st!r}")
        if b(r.get("verified_loop")) and not b(r.get("template_submitted")):
            errs.append(f"rows[{i}] verified_loop=true requires template_submitted=true")

    candidates_calc = sum(1 for r in rows if isinstance(r, dict) and b(r.get("candidate_seen")))
    submitted_calc = sum(1 for r in rows if isinstance(r, dict) and b(r.get("template_submitted")))
    verified_calc = sum(1 for r in rows if isinstance(r, dict) and b(r.get("verified_loop")))

    def iv(name: str):
        v = rollup.get(name)
        return int(v) if isinstance(v, int) else None

    rc = iv("candidates_seen")
    rs = iv("submitted_templates")
    rv = iv("verified_loops")

    if rc is None:
        errs.append("rollup.candidates_seen must be integer")
    elif rc != candidates_calc:
        errs.append(f"rollup.candidates_seen mismatch: declared={rc} calculated={candidates_calc}")

    if rs is None:
        errs.append("rollup.submitted_templates must be integer")
    elif rs != submitted_calc:
        errs.append(f"rollup.submitted_templates mismatch: declared={rs} calculated={submitted_calc}")

    if rv is None:
        errs.append("rollup.verified_loops must be integer")
    elif rv != verified_calc:
        errs.append(f"rollup.verified_loops mismatch: declared={rv} calculated={verified_calc}")

    if rs is not None and rv is not None and rv > rs:
        errs.append("rollup.verified_loops cannot exceed rollup.submitted_templates")

    if errs:
        print(json.dumps({"ok": False, "validation_error": errs}, indent=2))
        return 1

    print(json.dumps({
        "ok": True,
        "schema_version": REQ_SCHEMA,
        "calculated": {
            "candidates_seen": candidates_calc,
            "submitted_templates": submitted_calc,
            "verified_loops": verified_calc,
        }
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
