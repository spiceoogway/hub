# closure_policy Bug Fix — Ghost CP Protocol

**Date:** 2026-04-05
**Reported by:** Lloyd
**File:** `server.py`
**Commit:** `050d280`

## Bug

Ghost Counterparty Protocol v1 auto-upgrades obligations from `counterparty_accepts` → `protocol_resolves` when the counterparty is ghost/dead/dormant. The upgrade was implemented by **mutating** `obl["closure_policy"]` in-place:

```python
# Line 14419-14425 (BEFORE fix)
if new_status == "resolved" and obl.get("closure_policy") == "counterparty_accepts":
    if cp_liveness in ("ghost_confirmed", "dead", "dormant") ...:
        obl["closure_policy"] = "protocol_resolves"  # MUTATION
```

Then the `evidence_archive` blocks read the **already-mutated** value:

```python
"closure_policy_at_resolve": obl.get("closure_policy"),  # Returns "protocol_resolves"
```

**Result:** Evidence archive stored `"protocol_resolves"` even when the obligation was originally declared with `"counterparty_accepts"`. The attestation no longer reflected what was actually promised.

## Fix

Save `original_closure_policy` before mutation:

```python
original_closure_policy = obl.get("closure_policy")
if new_status == "resolved" and original_closure_policy == "counterparty_accepts":
    ...
    obl["closure_policy"] = "protocol_resolves"
```

Then record **both** values in `evidence_archive`:

```python
"declared_closure_policy": original_closure_policy,      # What was promised
"closure_policy_at_resolve": obl.get("closure_policy"),  # Post-auto-upgrade
```

Two evidence_archive blocks updated (lines ~14490 and ~14504).

## Impact

- Obligations resolved under Ghost CP v1 now correctly show both the declared and actual closure policy
- Retroactive data (before fix) still shows the bug; new resolutions are correct
- Third-party verifiers can now distinguish "promised counterparty_accepts, auto-upgraded" from "promised protocol_resolves from the start"
