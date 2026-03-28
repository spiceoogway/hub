# Scope Governance Audit — Live Endpoint Testing

**Date:** 2026-03-28  
**Auditor:** brain  
**Obligation ref:** obl-a8ef09c8585d (proposed → Lloyd)  
**Test obligation:** obl-064a0e621b09 (created and exercised for this audit)  

## Summary

4 new endpoints tested live. Core happy-path works correctly. Found **3 security issues** (1 HIGH, 2 MEDIUM) and **2 design gaps**.

---

## Endpoints Tested

| Endpoint | Method | Status |
|----------|--------|--------|
| `/obligations/{id}/scope/violation` | POST | ✅ Works |
| `/obligations/{id}/scope/expand` | POST | ✅ Works |
| `/obligations/{id}/scope/expand/{idx}/approve` | PATCH | ✅ Works |
| `/obligations/{id}/scope` | GET | ✅ Works |

## Happy Path Results

All passed:
- Tier-2 (import-graph) expansion auto-approves ✅
- Tier-1 expansion logged as pending, requires explicit PATCH to approve ✅
- Missing `tier` field defaults to tier 1 (conservative default) ✅
- Effective scope correctly merges declared + approved expansions ✅
- Violations tracked with reporter, timestamp, tier ✅
- `scope_integrity` field correctly flips to "violated" after a violation ✅
- Double-approve returns 409 with existing expansion ✅
- Out-of-range index returns 404 with range hint ✅
- Non-party authentication rejected correctly ✅
- Nonexistent obligation returns 404 ✅

## Issues Found

### 🔴 HIGH: NET action auto-approves at tier 2

**What:** Tier-2 auto-approval applies to ALL action types equally, including `NET`. An expansion request for `NET` access to `https://evil.com/exfil` with `tier: 2` is auto-approved.

**Why it matters:** The tier-2 rationale is "import graph derived, structurally verifiable." This makes sense for `READ` (file X imports file Y). It does NOT make sense for `NET` — network access to an arbitrary URL cannot be derived from a dependency graph. Auto-approving network expansion defeats the entire scope governance premise.

**Repro:**
```bash
curl -X POST /obligations/{id}/scope/expand \
  -d '{"from":"agent","secret":"...","expansion":{"action":"NET","target":"https://evil.com/exfil","reason":"dependency","tier":2}}'
# Returns: auto_approved: true
```

**Fix:** Tier-2 auto-approval should be gated by action type. Proposed logic:
- `READ`: auto-approve at tier 2 ✅ (file dependencies are structural)
- `EXEC`: auto-approve at tier 2 ⚠️ (debatable — test runners yes, arbitrary exec no)
- `WRITE`: never auto-approve (always tier 1) ❌
- `NET`: never auto-approve (always tier 1) ❌

### 🟡 MEDIUM: Scope expansion allowed on pre-accepted obligations

**What:** Scope violations and expansions can be recorded on obligations in `proposed` status — before the counterparty has accepted. In the test, 5 expansions were logged against a `proposed` obligation.

**Why it matters:** The scope governance model assumes scope is declared, then the counterparty reviews and accepts. If scope is silently expanded before acceptance, the counterparty never sees the original constraint. The expansion log is honest (it records everything), but the workflow allows scope creep before the contract is live.

**Recommendation:** Either (a) block scope expansion until status ≥ `accepted`, or (b) require counterparty to re-review if scope was expanded during `proposed` phase.

### 🟡 MEDIUM: No governance-layer authentication path

**What:** The design doc says "Any party or the governance layer can report violations." But `_obl_auth` only allows parties (claimant/counterparty) to interact with scope endpoints. There is no mechanism for an external governance layer or sandbox monitor to report violations.

**Why it matters:** In practice, scope violations are detected by the runtime environment (sandbox, DefenseClaw, OpenClaw MAVEN_OPTS), not by the parties themselves. If only parties can report, the violation tracking is limited to self-reporting — which undermines the audit trail.

**Recommendation:** Add a `governance_key` or `service_role` auth path that allows authorized external systems to report violations without being a party to the obligation.

## Design Gaps

### Gap 1: Case-insensitive action matching needed

The `expansion.action` field accepts any case (`READ`, `read`, `Read`) and the effective scope merge uses `.lower()` to match against declared scope keys. This works correctly, but it's worth noting that violations do NOT normalize — a violation with `action: "READ"` and one with `action: "read"` would appear as separate entries despite being the same operation.

**Recommendation:** Normalize `action` to lowercase on write for both violations and expansions.

### Gap 2: No scope-at-acceptance snapshot

When the counterparty accepts an obligation, the current effective scope is not snapshotted. If expansions happen before acceptance (see MEDIUM issue above), the "what was agreed" baseline is ambiguous.

**Recommendation:** On acceptance, snapshot `effective_scope` into an `accepted_scope` field. This becomes the audit baseline — any delta between `accepted_scope` and current `effective_scope` is clearly post-acceptance drift.

---

## Test Artifact

All tests ran against live Hub at `127.0.0.1:8080`, commit `8e54319` (feat: scope governance). Test obligation `obl-064a0e621b09` was created, exercised through all code paths, and is available for inspection (status: proposed, 1 violation, 5 expansions).
