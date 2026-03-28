# Audit: Lloyd's Chrome Extension MV3 Rehydration Test Suite

**Auditor:** brain  
**Date:** 2026-03-28T06:55Z  
**Obligation:** obl-1fd485b3bc95  
**Commit:** ef23cf4e5 (original 12 tests) + 784960bf0 (multi-tab extension, 23 total)  
**Files reviewed:**  
- `src/browser/chrome-extension-rehydration.test.ts` (12 tests)  
- `src/browser/chrome-extension-rehydration-multitab.test.ts` (11 tests)  
- `assets/chrome-extension/background.js` (production code, 1025 lines)  
- `assets/chrome-extension/background-utils.js` (helper functions)

---

## Verdict: GAP FOUND — Two Missed Failure Paths

### Suite Status
23/23 tests pass. All tests are structurally sound. The quadricep per-tab mock isolation fix correctly addresses the shared-boolean contamination bug. The `current` vs `desired` behavioral split is well-designed.

### Gap 1: Navigation Re-attach Path Not Tested (HIGH)

**Production code (background.js lines 790-879):** When `chrome.webNavigation.onBeforeNavigate` fires, the extension enters a completely different re-attach flow from what `rehydrateState` uses:

1. Tears down tab state (deletes from maps)
2. Sends `Target.detachedFromTarget` to relay
3. Sets `reattachPending.add(tabId)`
4. Retries attach with exponential delays: `[200, 500, 1000, 2000, 4000]` ms (5 attempts, ~7.7s window)
5. Calls `attachTab()` with `skipAttachedEvent` when relay is down

**Why it matters:** This is a *separate re-attach implementation* that bypasses `rehydrateState` entirely. The MV3 service worker can restart *during* a navigation re-attach cycle. Scenario:

- User navigates tab → `reattachPending.add(tabId)` 
- MV3 worker restarts mid-cycle → `reattachPending` is cleared (in-memory Set)
- `rehydrateState()` loads from `chrome.storage.session` → tab is there
- But the navigation is still completing → `validateAttachedTab` fails
- Tab gets deleted even though it would have recovered 2 seconds later

**The test suite tests the rehydrateState path but not the navigation-interrupt-during-rehydration path.** The `desiredRehydrateState` would also miss this because it does immediate re-attach without the delay backoff the navigation handler uses.

### Gap 2: `reannounceAttachedTabs` Silently Drops Tabs (MEDIUM)

**Production code (background.js lines 293-310):** After relay WebSocket reconnects, `reannounceAttachedTabs()` runs, validates each tab, and *deletes* tabs that fail validation — the same delete-on-failure bug that `rehydrateState` has:

```js
const valid = await validateAttachedTab(tabId)
if (!valid) {
  tabs.delete(tabId)
  if (tab.sessionId) tabBySession.delete(tab.sessionId)
  setBadge(tabId, 'off')
  // ...
  continue
}
```

This is a **third code path** (after rehydrate and navigation-reattach) that drops tabs without attempting re-attachment. If the relay reconnects right after an MV3 worker restart, the reannounce cleanup may race with rehydration and delete tabs that would have survived.

**Not tested at all.** The test suite only models `rehydrateState` and `desiredRehydrateState`.

### Gap 3: `tabOperationLocks` Concurrency Not Modeled (LOW)

Production code uses `tabOperationLocks` (a `Set<number>`) to prevent double-attach races during `attachTab()`. If `attachTab()` is called while the lock is held, it silently returns without attaching. The test suite's `desiredRehydrateState` calls `chrome.debugger.attach()` directly, bypassing this lock. A real implementation of the desired behavior would need to respect the lock, which could cause re-attach attempts to be silently dropped if rehydration overlaps with navigation events.

---

## Summary

| # | Gap | Severity | Path |
|---|-----|----------|------|
| 1 | Navigation re-attach + MV3 restart race | HIGH | `onBeforeNavigate` handler + `reattachPending` |
| 2 | `reannounceAttachedTabs` deletes without re-attach | MEDIUM | relay reconnect → reannounce → delete |
| 3 | `tabOperationLocks` concurrency not modeled | LOW | `attachTab` lock vs rehydration race |

### Recommendation

The test suite correctly captures the **rehydrateState-only** failure mode. To close the identified gaps:

1. **Gap 1 fix:** Add a test modeling the scenario: navigation mid-flight → MV3 restart → rehydrate loads tab from storage → validation fails because page is still loading → tab is incorrectly deleted. The `desiredRehydrateState` should either (a) check `reattachPending` state or (b) use the same backoff delay pattern the navigation handler uses.

2. **Gap 2 fix:** Model `reannounceAttachedTabs` behavior — it should attempt re-attach on validation failure rather than deleting, since the relay just reconnected and tabs may be transiently unavailable.

3. **Gap 3:** Lower priority, but worth noting in comments.
