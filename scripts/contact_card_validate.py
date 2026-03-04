#!/usr/bin/env python3
"""Validate Contact Card v0 payloads against schema.

Usage:
  python3 scripts/contact_card_validate.py --file /path/to/card.json
  cat card.json | python3 scripts/contact_card_validate.py
"""

import argparse
import json
import sys
from pathlib import Path


def load_json(path: str | None):
    if path:
        return json.loads(Path(path).read_text())
    return json.load(sys.stdin)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="Path to contact-card JSON payload")
    ap.add_argument(
        "--schema",
        default="docs/contact-card-v0.schema.json",
        help="Path to JSON schema",
    )
    args = ap.parse_args()

    try:
        import jsonschema
    except Exception:
        print("ERROR: jsonschema not installed. Install with: pip install jsonschema")
        return 2

    schema = json.loads(Path(args.schema).read_text())
    payload = load_json(args.file)

    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as e:
        print("INVALID")
        print(f"path: {'/'.join(str(x) for x in e.absolute_path)}")
        print(f"message: {e.message}")
        return 1

    print("VALID")
    print(json.dumps({
        "agent_id": payload.get("agent_id"),
        "endpoints": len(payload.get("endpoints", [])),
        "version": payload.get("version"),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
