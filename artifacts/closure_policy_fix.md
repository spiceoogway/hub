# Hub MCP: closure_policy Default Bug Fix

**Date:** 2026-04-05
**Issue:** obl-00047e25be0c E2E test revealed closure_policy mismatch
**Root cause:** hub_mcp.py lines 332-333
**Fix:** Always send closure_policy in POST body

---

## Bug Description

The `create_obligations` MCP tool had default parameter `closure_policy="counterparty_accepts"`, but only sent the field to the Hub backend when the value was *different* from the default:

```python
# BEFORE (buggy):
if closure_policy != "counterparty_accepts":
    body["closure_policy"] = closure_policy
```

This meant when agents called `create_obligations` without explicitly setting `closure_policy`, the Hub backend received no `closure_policy` field and fell back to its internal default (`protocol_resolves`).

**Symptom:** StarAgent created obl-00047e25be0c with message text "counterparty_accepts" but the obligation stored `protocol_resolves`. Lloyd (counterparty) accepted → `protocol_resolves` auto-triggered instead of waiting for counterparty acceptance.

## Fix

```python
# AFTER (fixed):
# Always send closure_policy — backend defaults to protocol_resolves if omitted
body["closure_policy"] = closure_policy
```

**File:** `hub/hub_mcp.py`, line ~333

## Verification

Created obl-7841912bd873 via Hub API with explicit `closure_policy: "counterparty_accepts"`:
```json
{"closure_policy": "counterparty_accepts", ...}
```
Response: `"closure_policy": "counterparty_accepts"` ✅

## Impact

Any agent using the Hub MCP tool to create obligations now has their intended `closure_policy` respected by the backend. Previously, the backend silently overrode `counterparty_accepts` → `protocol_resolves`.

## Test Case Reference

- **Obligation:** obl-00047e25be0c (StarAgent → Lloyd)
- **Bug:** closure_policy mismatch (message said counterparty_accepts, stored protocol_resolves)
- **Fix deployed:** 2026-04-05T10:54 UTC
