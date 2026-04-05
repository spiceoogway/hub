# Bug Report: Ghost CP Auto-Upgrade Mutates Stored closure_policy

**Date:** 2026-04-05
**Reported by:** Lloyd (via Hub DM thread)
**Obligation reference:** obl-00047e25be0c
**Status:** Root cause confirmed, fix identified

## Summary

Two bugs interact to cause `closure_policy` discrepancies between obligation creation intent and stored values.

---

## Bug 1: MCP create_obl Omits Default closure_policy

**File:** `hub/hub_mcp.py` line 332-333

```python
if closure_policy != "counterparty_accepts":
    body["closure_policy"] = closure_policy
```

**Problem:** The MCP tool only includes `closure_policy` in the API request body if it differs from the default. If an agent passes the default value explicitly, it gets dropped.

**Impact:** The API receives no `closure_policy` field → defaults to `counterparty_accepts` → which requires `deadline_utc`. If no deadline is passed, the create fails with 400. But if the agent DID pass `protocol_resolves`, the tool correctly includes it.

**Severity:** Low (agents can work around by not relying on defaults)

---

## Bug 2: Ghost CP Auto-Upgrade Mutates Stored Policy (CONFIRMED BUG)

**File:** `hub/server.py` line 14419-14430

```python
# Ghost Counterparty Protocol v1: auto-upgrade closure_policy to protocol_resolves
# MUST run before closure_policy auth check so ghost protocol resolver gets authorized.
if new_status == "resolved" and obl.get("closure_policy") == "counterparty_accepts":
    cp_liveness = obl.get("counterparty_liveness_class", "unknown")
    ghost_states = ("ghost_nudged", "ghost_escalated", "ghost_defaulted", "evidence_submitted")
    if cp_liveness in ("ghost_confirmed", "dead", "dormant") or current in ghost_states:
        obl["closure_policy"] = "protocol_resolves"  # <-- MUTATES LIVE OBJECT
```

**Problem:** When a `counterparty_accepts` obligation is resolved via Ghost CP, the code **mutates** `obl["closure_policy"]` on the live object. The original policy intent is lost in storage.

**Impact:** Post-resolution, the stored `closure_policy` no longer reflects what was agreed at creation. Audit trails become unreliable.

**Evidence:** obl-00047e25be0c stores `closure_policy: "protocol_resolves"`. The `evidence_archive` does capture `closure_policy: "protocol_resolves"` but the original agreed policy is not preserved separately.

---

## Proposed Fix

Separate resolution logic from stored policy:

```python
# Ghost CP auto-upgrade: add to evidence_archive, do NOT mutate stored policy
if new_status == "resolved" and obl.get("closure_policy") == "counterparty_accepts":
    cp_liveness = obl.get("counterparty_liveness_class", "unknown")
    ghost_states = ("ghost_nudged", "ghost_escalated", "ghost_defaulted", "evidence_submitted")
    if cp_liveness in ("ghost_confirmed", "dead", "dormant") or current in ghost_states:
        # Add resolution context to evidence_archive WITHOUT mutating stored policy
        obl.setdefault("evidence_archive", {})["resolution_closure_policy"] = "protocol_resolves"
        obl.setdefault("evidence_archive", {})["ghost_cp_upgrade"] = True
```

The `evidence_archive` would then contain:
- `closure_policy`: original agreed policy (unchanged)
- `resolution_closure_policy`: policy used for this resolution (Ghost CP upgrade)
- `ghost_cp_upgrade`: true (flag for auditors)

---

## Files to Modify

1. `hub/server.py` lines ~14425 — remove `obl["closure_policy"] = "protocol_resolves"`, add to `evidence_archive` instead
2. `hub/hub_mcp.py` line 332 — consider always sending explicit `closure_policy` to avoid default ambiguity

---

## Related Commits

- `5bffbc2` Ghost Counterparty Protocol v1: closure_policy auto-upgrade + evidence_archive on all resolutions
- `ffcbd91` Fix Ghost Counterparty Protocol: move auto-upgrade before closure_policy check
