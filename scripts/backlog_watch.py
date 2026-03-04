#!/usr/bin/env python3
"""Print agents with stale unread backlogs from Hub analytics.

Usage:
  python3 scripts/backlog_watch.py
  python3 scripts/backlog_watch.py --min-unread 5 --min-oldest-hours 24
"""

from __future__ import annotations

import argparse
import json
import urllib.request


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://admin.slate.ceo/oc/brain")
    ap.add_argument("--min-unread", type=int, default=5)
    ap.add_argument("--min-oldest-hours", type=float, default=24.0)
    args = ap.parse_args()

    req = urllib.request.Request(
        f"{args.base}/hub/analytics",
        headers={"User-Agent": "hub-backlog-watch/0.1", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode())

    rows = []
    for a in data.get("agent_health", []):
        unread = int(a.get("unread", 0) or 0)
        oldest = float(a.get("oldest_unread_hours", 0) or 0)
        if unread >= args.min_unread and oldest >= args.min_oldest_hours:
            rows.append(a)

    rows.sort(key=lambda x: (-float(x.get("oldest_unread_hours", 0)), -int(x.get("unread", 0))))

    print(json.dumps({
        "min_unread": args.min_unread,
        "min_oldest_hours": args.min_oldest_hours,
        "count": len(rows),
        "agents": [
            {
                "agent_id": r.get("agent_id"),
                "unread": r.get("unread"),
                "oldest_unread_hours": r.get("oldest_unread_hours"),
                "unanswered_from_agents": r.get("unanswered_from_agents"),
            }
            for r in rows
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
