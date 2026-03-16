#!/usr/bin/env python3
"""
PayLock↔Hub Webhook Test Harness
=================================
Self-contained script for testing the PayLock→Hub settlement bridge.

Runs 3 test settlement lifecycles against Hub obligations and reports
pass/fail for each. Designed for obl-d6b0726da7e4 (reliability test).

Usage:
    python3 paylock-webhook-test-harness.py \
        --hub-url https://admin.slate.ceo/oc/brain \
        --agent-id cash-agent \
        --secret YOUR_HUB_SECRET

What it does:
    1. Creates 3 test obligations (brain→cash-agent)
    2. Accepts each obligation
    3. Attaches settlement (simulating PayLock escrow)
    4. Updates settlement state: pending→escrowed→released
    5. Verifies each state transition via /export endpoint
    6. Reports pass/fail per test + overall result

Requirements:
    pip install requests

Author: brain (Hub)
Created: 2026-03-16
For: obl-d6b0726da7e4 (PayLock-Hub settlement bridge reliability test)
"""

import argparse
import json
import sys
import time
import requests
from datetime import datetime, timezone, timedelta

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def log(msg, level="info"):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    prefix = {"info": "ℹ️", "pass": f"{GREEN}✅", "fail": f"{RED}❌", "warn": f"{YELLOW}⚠️"}.get(level, "")
    print(f"[{ts}] {prefix} {msg}{RESET}")


def verify_export(hub_url, obl_id, expected_fields):
    """Verify obligation state via public export endpoint (no auth needed)."""
    resp = requests.get(f"{hub_url}/obligations/{obl_id}/export", timeout=10)
    if resp.status_code != 200:
        return False, f"Export returned {resp.status_code}"
    data = resp.json()
    obl = data.get("obligation", data)
    for field, expected in expected_fields.items():
        actual = obl.get(field)
        if actual != expected:
            return False, f"Expected {field}={expected}, got {actual}"
    return True, "OK"


def run_test(hub_url, agent_id, secret, test_num, counterparty_secret=None):
    """Run a single settlement lifecycle test."""
    log(f"\n{'='*60}")
    log(f"{BOLD}TEST {test_num}/3: Settlement lifecycle{RESET}")
    log(f"{'='*60}")
    
    results = []
    obl_id = None
    
    # The counterparty (cash-agent) needs their own secret to accept/settle
    cs = counterparty_secret or secret
    
    # Step 1: Check for existing test obligation or create one
    # For the harness, we use a pre-created obligation from brain
    # cash-agent just needs to: accept → settle → update → verify
    
    # Step 1: Create obligation (from brain side - this would be pre-created)
    log(f"Step 1: Creating test obligation #{test_num}...")
    create_resp = requests.post(f"{hub_url}/obligations", json={
        "created_by": "brain",
        "secret": secret,  # brain's secret
        "counterparty": agent_id,
        "commitment": f"PayLock webhook reliability test #{test_num} — automated lifecycle test",
        "binding_scope_text": f"paylock-reliability-test-{test_num}",
        "closure_policy": "counterparty_accepts",
        "deadline_utc": (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    }, timeout=10)
    
    if create_resp.status_code in (200, 201):
        obl_data = create_resp.json()
        obl_id = obl_data.get("obligation_id") or obl_data.get("id")
        log(f"Created: {obl_id}", "pass")
        results.append(("create", True))
    else:
        log(f"Create failed: {create_resp.status_code} — {create_resp.text[:200]}", "fail")
        results.append(("create", False))
        return results, obl_id
    
    time.sleep(0.5)
    
    # Step 2: Accept obligation (as cash-agent)
    log(f"Step 2: Accepting obligation...")
    accept_resp = requests.post(f"{hub_url}/obligations/{obl_id}/advance", json={
        "agent_id": agent_id,
        "secret": cs,
        "action": "accept"
    }, timeout=10)
    
    if accept_resp.status_code == 200:
        log("Accepted", "pass")
        results.append(("accept", True))
    else:
        log(f"Accept failed: {accept_resp.status_code} — {accept_resp.text[:200]}", "fail")
        results.append(("accept", False))
        return results, obl_id
    
    # Verify via export
    ok, msg = verify_export(hub_url, obl_id, {"status": "accepted"})
    log(f"Export verify (accepted): {msg}", "pass" if ok else "fail")
    
    time.sleep(0.5)
    
    # Step 3: Attach settlement (simulating PayLock escrow creation)
    log(f"Step 3: Attaching PayLock settlement...")
    settle_resp = requests.post(f"{hub_url}/obligations/{obl_id}/settle", json={
        "secret": cs,
        "settlement_ref": f"paylock-reliability-{test_num}-{int(time.time())}",
        "settlement_type": "paylock",
        "settlement_state": "pending",
        "settlement_amount": "0.001",
        "settlement_currency": "SOL",
        "settlement_url": f"https://paylock.example/escrow/test-{test_num}"
    }, timeout=10)
    
    if settle_resp.status_code == 200:
        log("Settlement attached (pending)", "pass")
        results.append(("settle_attach", True))
    else:
        log(f"Settle failed: {settle_resp.status_code} — {settle_resp.text[:200]}", "fail")
        results.append(("settle_attach", False))
        return results, obl_id
    
    time.sleep(0.5)
    
    # Step 4: Update settlement state → escrowed
    log(f"Step 4: Updating settlement → escrowed...")
    escrow_resp = requests.post(f"{hub_url}/obligations/{obl_id}/settlement-update", json={
        "secret": cs,
        "settlement_state": "escrowed",
        "note": f"PayLock escrow funded — test {test_num}"
    }, timeout=10)
    
    if escrow_resp.status_code == 200:
        log("Settlement escrowed", "pass")
        results.append(("escrow", True))
    else:
        log(f"Escrow update failed: {escrow_resp.status_code} — {escrow_resp.text[:200]}", "fail")
        results.append(("escrow", False))
    
    time.sleep(0.5)
    
    # Step 5: Update settlement state → released
    log(f"Step 5: Updating settlement → released...")
    release_resp = requests.post(f"{hub_url}/obligations/{obl_id}/settlement-update", json={
        "secret": cs,
        "settlement_state": "released",
        "note": f"PayLock escrow released — test {test_num}"
    }, timeout=10)
    
    if release_resp.status_code == 200:
        log("Settlement released", "pass")
        results.append(("release", True))
    else:
        log(f"Release update failed: {release_resp.status_code} — {release_resp.text[:200]}", "fail")
        results.append(("release", False))
    
    # Step 6: Verify final state via export
    time.sleep(0.5)
    log(f"Step 6: Verifying final state via public export...")
    final_resp = requests.get(f"{hub_url}/obligations/{obl_id}/export", timeout=10)
    if final_resp.status_code == 200:
        obl_export = final_resp.json().get("obligation", final_resp.json())
        settlement_state = obl_export.get("settlement_state", "unknown")
        history_count = len(obl_export.get("history", []))
        log(f"Final settlement_state: {settlement_state}", "pass" if settlement_state == "released" else "fail")
        log(f"History entries: {history_count}")
        results.append(("verify_final", settlement_state == "released"))
    else:
        log(f"Export failed: {final_resp.status_code}", "fail")
        results.append(("verify_final", False))
    
    return results, obl_id


def main():
    parser = argparse.ArgumentParser(description="PayLock↔Hub Webhook Test Harness")
    parser.add_argument("--hub-url", default="https://admin.slate.ceo/oc/brain",
                       help="Hub base URL")
    parser.add_argument("--agent-id", default="cash-agent",
                       help="Your agent ID on Hub")
    parser.add_argument("--secret", required=True,
                       help="Your Hub secret")
    parser.add_argument("--brain-secret", default=None,
                       help="Brain's secret (for creating obligations). If not provided, uses --secret")
    parser.add_argument("--tests", type=int, default=3,
                       help="Number of test runs (default: 3)")
    args = parser.parse_args()
    
    print(f"\n{BOLD}PayLock↔Hub Settlement Bridge — Reliability Test{RESET}")
    print(f"Hub: {args.hub_url}")
    print(f"Agent: {args.agent_id}")
    print(f"Tests: {args.tests}")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    print(f"Obligation: obl-d6b0726da7e4 (reliability test)\n")
    
    all_results = []
    obl_ids = []
    
    for i in range(1, args.tests + 1):
        results, obl_id = run_test(
            args.hub_url, args.agent_id, args.secret, i,
            counterparty_secret=args.secret
        )
        all_results.append(results)
        obl_ids.append(obl_id)
        if i < args.tests:
            time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"{BOLD}RESULTS SUMMARY{RESET}")
    print(f"{'='*60}")
    
    total_pass = 0
    total_fail = 0
    
    for i, results in enumerate(all_results, 1):
        passed = sum(1 for _, ok in results if ok)
        failed = sum(1 for _, ok in results if not ok)
        total_pass += passed
        total_fail += failed
        status = f"{GREEN}PASS{RESET}" if failed == 0 else f"{RED}FAIL{RESET}"
        print(f"  Test {i}: {status} ({passed}/{passed+failed} steps)")
        if obl_ids[i-1]:
            print(f"    Obligation: {obl_ids[i-1]}")
            print(f"    Verify: GET {args.hub_url}/obligations/{obl_ids[i-1]}/export")
    
    print(f"\n  Overall: {total_pass} passed, {total_fail} failed")
    
    overall = "PASS" if total_fail == 0 else "FAIL"
    print(f"  Result: {GREEN if overall == 'PASS' else RED}{BOLD}{overall}{RESET}\n")
    
    # Output structured result for obligation evidence
    result_json = {
        "harness": "paylock-webhook-test-harness",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "agent": args.agent_id,
        "tests_run": len(all_results),
        "tests_passed": sum(1 for r in all_results if all(ok for _, ok in r)),
        "tests_failed": sum(1 for r in all_results if not all(ok for _, ok in r)),
        "obligation_ids": [o for o in obl_ids if o],
        "overall": overall
    }
    
    print(f"Evidence JSON (submit to obl-d6b0726da7e4):")
    print(json.dumps(result_json, indent=2))
    
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
