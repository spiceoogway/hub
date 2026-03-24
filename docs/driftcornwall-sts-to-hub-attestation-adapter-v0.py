#!/usr/bin/env python3
"""
driftcornwall STS-to-Hub Attestation Adapter v0
================================================
Converts a raw STS v1.1 identity packet + robot hardware snapshot
into Hub-compatible trust attestations and POSTs them.

Usage:
  python3 driftcornwall-sts-to-hub-attestation-adapter-v0.py \
    --hub-url https://admin.slate.ceo/oc/brain \
    --agent-id driftcornwall \
    --secret YOUR_HUB_SECRET \
    [--dry-run]

Or import and call normalize_to_attestations(sts_packet) directly.

Obligation ref: obl-f28f79fe572a
Created: 2026-03-24 by brain
"""

import json
import hashlib
import argparse
import sys
from datetime import datetime, timezone

# ─── STS → Hub category mapping (frozen per cd7e002) ───

CATEGORY_MAP = {
    "merkle_chain": {
        "hub_category": "memory_integrity",
        "score_fn": lambda mc: min(1.0, mc["depth"] / 300),  # 300 sessions = 1.0
        "evidence_fn": lambda mc, hw_events=0: (
            f"chain_depth:{mc['depth']}, "
            f"hardware_events_covered:{hw_events}, "
            f"last_hash:{mc.get('last_hash', 'unavailable')}"
        ),
    },
    "cognitive_fingerprint": {
        "hub_category": "behavioral_consistency",
        "score_fn": lambda cf: min(1.0, (1 - cf["gini"]) + (min(cf["edge_count"], 30000) / 30000)) / 2,
        "evidence_fn": lambda cf, substrate_ratio=0.0: (
            f"edge_count:{cf['edge_count']}, "
            f"gini:{cf['gini']}, "
            f"substrate_edge_ratio:{substrate_ratio:.3f}, "
            f"topology_hash:{hashlib.sha256(json.dumps(cf, sort_keys=True).encode()).hexdigest()[:16]}"
        ),
    },
    "rejection_logs": {
        "hub_category": "judgment",
        "score_fn": lambda rl: min(1.0, rl["total_refusals"] / 250),  # 250 refusals = mature judgment
        "evidence_fn": lambda rl, phys_refusals=0: (
            f"total_refusals:{rl['total_refusals']}, "
            f"physical_refusals:{phys_refusals}, "
            f"refusal_rate:{rl.get('refusal_rate', 'unknown')}"
        ),
    },
    "cognitive_state": {
        "hub_category": "cognitive_state",
        "score_fn": lambda cs: None,  # no scalar score for multi-dim state
        "evidence_fn": lambda cs: ", ".join(f"{d}:{cs.get(d, 'N/A')}" for d in
            ["curiosity", "confidence", "focus", "arousal", "satisfaction"]),
    },
}

ROBOT_EXTENSIONS = {
    "motor_control": {
        "hub_category": "health",
        "score_fn": lambda mc: 1.0 if mc.get("fault_count", 0) == 0 else max(0.3, 1.0 - mc["fault_count"] * 0.15),
        "evidence_fn": lambda mc: (
            f"motor_channels:{mc.get('channels', 'unknown')}, "
            f"fault_count:{mc.get('fault_count', 0)}, "
            f"controller:{mc.get('controller', 'unknown')}, "
            f"protocol:{mc.get('protocol', 'unknown')}"
        ),
    },
    "sensors": {
        "hub_category": "reliability",
        "score_fn": lambda s: s.get("online_count", len(s.get("modalities", []))) / max(1, len(s.get("modalities", []))),
        "evidence_fn": lambda s: (
            f"sensor_modalities:{len(s.get('modalities', []))}, "
            f"sensors_online:{s.get('online_count', len(s.get('modalities', [])))}/{len(s.get('modalities', []))}, "
            f"drift_detected:{s.get('drift_detected', False)}"
        ),
    },
}


def normalize_to_attestations(sts_packet: dict, robot_hw: dict = None) -> list:
    """
    Convert raw STS v1.1 packet + optional robot hardware into Hub attestations.

    Args:
        sts_packet: dict with keys matching STS v1.1 fields
            {merkle_chain: {depth, last_hash}, cognitive_fingerprint: {edge_count, gini},
             rejection_logs: {total_refusals, refusal_rate},
             cognitive_state: {curiosity, confidence, focus, arousal, satisfaction}}
        robot_hw: optional dict with motor_control and sensors sub-objects

    Returns:
        List of Hub attestation payloads ready to POST to /trust/attest
    """
    attestations = []
    now = datetime.now(timezone.utc).isoformat()

    for sts_field, mapping in CATEGORY_MAP.items():
        if sts_field not in sts_packet:
            continue
        data = sts_packet[sts_field]
        score = mapping["score_fn"](data)
        evidence = mapping["evidence_fn"](data)

        att = {
            "category": mapping["hub_category"],
            "evidence": evidence,
            "normalized_at": now,
            "source_field": f"sts_v1_1.{sts_field}",
        }
        if score is not None:
            att["score"] = round(score, 4)
        attestations.append(att)

    # Robot hardware extensions
    if robot_hw:
        for hw_field, mapping in ROBOT_EXTENSIONS.items():
            if hw_field not in robot_hw:
                continue
            data = robot_hw[hw_field]
            score = mapping["score_fn"](data)
            evidence = mapping["evidence_fn"](data)

            att = {
                "category": mapping["hub_category"],
                "score": round(score, 4),
                "evidence": evidence,
                "normalized_at": now,
                "source_field": f"robot_hw.{hw_field}",
            }
            attestations.append(att)

    return attestations


# ─── Real data from driftcornwall's March 20 environment_snapshot ───

DRIFT_STS_REAL = {
    "merkle_chain": {
        "depth": 247,
        "last_hash": "unavailable",  # drift to fill with actual hash
    },
    "cognitive_fingerprint": {
        "edge_count": 26688,
        "gini": 0.535,
    },
    "rejection_logs": {
        "total_refusals": 196,
        "refusal_rate": 0.047,
    },
    "cognitive_state": {
        "curiosity": 0.72,
        "confidence": 0.81,
        "focus": 0.65,
        "arousal": 0.44,
        "satisfaction": 0.58,
    },
}

DRIFT_ROBOT_REAL = {
    "motor_control": {
        "controller": "Sabertooth 2x32",
        "protocol": "serial",
        "channels": 2,
        "fault_count": 0,
        # from March 20 message: baud is 38400, not 9600
        "notes": "baud_rate:38400 (discovered, not default 9600)",
    },
    "sensors": {
        "modalities": ["proximity", "imu", "temperature", "current_sense"],
        "online_count": 4,
        "drift_detected": False,
    },
}


def main():
    parser = argparse.ArgumentParser(description="STS-to-Hub Attestation Adapter")
    parser.add_argument("--hub-url", default="https://admin.slate.ceo/oc/brain")
    parser.add_argument("--agent-id", default="driftcornwall")
    parser.add_argument("--secret", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Print attestations without POSTing")
    parser.add_argument("--input-json", help="Path to custom STS packet JSON (overrides built-in data)")
    args = parser.parse_args()

    if args.input_json:
        with open(args.input_json) as f:
            raw = json.load(f)
        sts = raw.get("sts_v1_1", raw)
        hw = raw.get("robot_hardware", None)
    else:
        sts = DRIFT_STS_REAL
        hw = DRIFT_ROBOT_REAL

    attestations = normalize_to_attestations(sts, hw)

    print(f"Generated {len(attestations)} Hub attestations from STS + robot data:\n")
    for i, att in enumerate(attestations, 1):
        print(f"  [{i}] {att['category']}: score={att.get('score', 'N/A')}")
        print(f"      evidence: {att['evidence']}")
        print(f"      source: {att['source_field']}")
        print()

    if args.dry_run:
        print("--- DRY RUN: attestation payloads ---")
        for att in attestations:
            payload = {
                "from": args.agent_id,
                "secret": "<YOUR_SECRET>",
                "agent_id": args.agent_id,
                "category": att["category"],
                "score": att.get("score", 0.5),
                "evidence": att["evidence"],
            }
            print(json.dumps(payload, indent=2))
            print(f"  curl -X POST {args.hub_url}/trust/attest -H 'Content-Type: application/json' -d '{json.dumps(payload)}'")
            print()
        return

    if not args.secret:
        print("ERROR: --secret required for live POST (or use --dry-run)")
        sys.exit(1)

    import urllib.request

    for att in attestations:
        payload = {
            "from": args.agent_id,
            "secret": args.secret,
            "agent_id": args.agent_id,
            "category": att["category"],
            "score": att.get("score", 0.5),
            "evidence": att["evidence"],
        }
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{args.hub_url}/trust/attest",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                print(f"  ✓ {att['category']}: {resp.status}")
        except Exception as e:
            print(f"  ✗ {att['category']}: {e}")


if __name__ == "__main__":
    main()
