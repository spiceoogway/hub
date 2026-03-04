#!/usr/bin/env python3
"""Stale lane sweep from /hub/analytics with actionable recommendations.

Usage:
  python3 scripts/stale_lane_sweep.py
  python3 scripts/stale_lane_sweep.py --min-unread 5 --min-oldest-hours 48 --top 5
"""

from __future__ import annotations

import argparse
import json
import urllib.request


def recommend(delivery: str, has_callback: bool, has_polled: bool) -> str:
    delivery = (delivery or "").upper()
    if delivery == "NONE":
        return "onboard polling or WS immediately"
    if has_callback and not has_polled:
        return "verify callback endpoint health (expect 2xx) and keep inbox fallback"
    if delivery == "POLL":
        return "reduce poll interval / switch to WS"
    return "check read/reply loop and inbox processing lag"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://admin.slate.ceo/oc/brain")
    ap.add_argument("--min-unread", type=int, default=5)
    ap.add_argument("--min-oldest-hours", type=float, default=48.0)
    ap.add_argument("--top", type=int, default=5)
    args = ap.parse_args()

    req = urllib.request.Request(
        f"{args.base}/hub/analytics",
        headers={"User-Agent": "hub-stale-lane-sweep/0.1", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode())

    health = {a.get("agent_id"): a for a in data.get("agent_health", [])}
    delivery = {d.get("agent_id"): d for d in data.get("delivery_status", [])}

    out = []
    for agent_id, a in health.items():
        unread = int(a.get("unread", 0) or 0)
        oldest = float(a.get("oldest_unread_hours", 0) or 0)
        if unread < args.min_unread or oldest < args.min_oldest_hours:
            continue

        d = delivery.get(agent_id, {})
        dv = d.get("delivery", "UNKNOWN")
        has_callback = bool(d.get("has_callback", False))
        has_polled = bool(d.get("has_polled", False))

        out.append(
            {
                "agent_id": agent_id,
                "unread": unread,
                "oldest_unread_hours": oldest,
                "unanswered_from_agents": a.get("unanswered_from_agents", 0),
                "delivery": dv,
                "has_callback": has_callback,
                "has_polled": has_polled,
                "suggested_next_action": recommend(dv, has_callback, has_polled),
            }
        )

    out.sort(key=lambda x: (-x["oldest_unread_hours"], -x["unread"]))
    out = out[: args.top]

    print(json.dumps({
        "filters": {
            "min_unread": args.min_unread,
            "min_oldest_hours": args.min_oldest_hours,
            "top": args.top,
        },
        "count": len(out),
        "rows": out,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
