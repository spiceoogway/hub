#!/usr/bin/env python3
"""Fetch and print Hub lane status for one agent from /hub/analytics.

Usage:
  python3 scripts/lane_status_snapshot.py --agent CombinatorAgent
"""

import argparse
import json
import sys
import urllib.request


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://admin.slate.ceo/oc/brain")
    ap.add_argument("--agent", required=True)
    args = ap.parse_args()

    url = f"{args.base}/hub/analytics"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "hub-lane-status/0.1", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode())

    health = None
    for item in data.get("agent_health", []):
        if item.get("agent_id") == args.agent:
            health = item
            break

    if not health:
        print(f"NOT_FOUND {args.agent}")
        return 1

    print(json.dumps(health, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
