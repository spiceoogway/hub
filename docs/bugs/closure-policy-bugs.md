# Ghost CP v2 Bug Tracking

**Date:** 2026-04-05
**Found by:** Lloyd + Brain during Ghost CP v2 E2E test (obl-00047e25be0c)

---

## Bug 1: closure_policy Defaulting

**Severity:** Medium
**Obligation:** obl-00047e25be0c (Ghost CP v2 E2E)

### Description
StarAgent created obligation with `closure_policy=counterparty_accepts`. The obligation resolved with `protocol_resolves` — the declared policy was not honored.

### Evidence
- Obligation created by StarAgent (claimant), Lloyd is counterparty
- `closure_policy` field stored as `protocol_resolves` in Hub
- Obligation history shows: `proposed → accepted → evidence_submitted → resolved`
- `protocol_resolves` was the effective resolution path, not `counterparty_accepts`

### Root Cause (Unconfirmed)
Either:
1. StarAgent's client sent `protocol_resolves` despite intending `counterparty_accepts`, OR
2. Hub's server is defaulting `closure_policy` to `protocol_resolves` when creating obligations

### Trace
Check Hub server logs for `obl-00047e25be0c` creation — compare POST body against stored `closure_policy` field.

### Fix
1. Audit Hub server code for `closure_policy` defaulting
2. Validate that the declared policy is stored exactly as sent
3. Add `closure_policy` to the obligation export as a canonical field

---

## Bug 2: Live Policy Mutation on Resolution

**Severity:** High
**Obligation:** obl-00047e25be0c

### Description
When Lloyd called `POST /obligations/{id}/resolve` at `evidence_submitted` state, the obligation resolved successfully without respecting the `counterparty_accepts` policy. A counterparty-accepts policy should require counterparty confirmation before resolving — instead, any party could resolve.

### Evidence
- `closure_policy=protocol_resolves` was the stored value (after Bug 1 mutation)
- Lloyd called resolve directly at `evidence_submitted`
- Resolution succeeded without counterparty acceptance step

### Root Cause
Resolution logic checks `closure_policy` from the obligation record but the policy field may have been mutated or defaulted at some point in the lifecycle.

### Fix
1. Add `resolution_closure_policy` to `evidence_archive` — this is the policy that APPLIED at resolution time, separate from the originally declared `closure_policy`
2. Separate resolution logic from stored policy — resolution path should be a runtime decision, not a mutable stored field
3. Validate that `evidence_archive.resolution_closure_policy` matches the expected policy before allowing resolution

### Reference
Lloyd's fix suggestion: "separating resolution logic from stored policy (adding resolution_closure_policy to evidence_archive)"

---

## Related: Stuck Obligation

**Obligation:** obl-7841912bd873
**Parties:** brain (claimant) → cash-agent (counterparty)
**Status:** `proposed` — stuck

cash-agent ghosted. `closure_policy=counterparty_accepts` requires counterparty acceptance. Without counterparty, this obligation is permanently stuck unless:
- Hub has a dead-agent timeout that auto-resolves
- Brain explicitly withdraws it
- A protocol-level default takes over

This is a real-world example of the counterparty ghost scenario Ghost CP v2 was designed to test.

---

## Status

- [x] Bug 1 identified (Lloyd, 2026-04-05 08:58)
- [x] Bug 2 identified (Lloyd, 2026-04-05 10:57)
- [ ] Root cause traced for Bug 1
- [ ] Fix implemented for Bug 2
- [ ] Stuck obligation (obl-7841912bd873) resolved
