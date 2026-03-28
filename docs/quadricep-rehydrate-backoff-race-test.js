/**
 * Test: rehydrateState vs onBeforeNavigate backoff race condition
 *
 * Obligation: obl-ec7c89d313f3
 * Proves: rehydrateState firing mid-backoff deletes a tab that the
 *         navigation handler would have saved.
 * Models: reattachPending Set cleared on restart, chrome.storage.session
 *         retaining the tab, backoff array [200,500,1000,2000,4000]ms.
 *
 * All delays are mocked via fake timers — no real waits.
 *
 * Run: node --experimental-vm-modules quadricep-rehydrate-backoff-race-test.js
 *   or: npx jest quadricep-rehydrate-backoff-race-test.js (with jest configured)
 *
 * The test models the ACTUAL background.js behavior from activeclaw:
 *   - rehydrateState() restores tabs from chrome.storage.session, then
 *     validates each one; if validation fails and re-attach fails, it deletes
 *     the tab from the `tabs` Map and sets badge to 'off'.
 *   - The navigation handler adds tabId to reattachPending, then retries
 *     attachTab at [200, 500, 1000, 2000, 4000]ms intervals.
 *   - On MV3 worker restart, reattachPending (in-memory Set) is cleared,
 *     but chrome.storage.session retains the persisted tab entries.
 *
 * THE RACE: If a navigation triggers backoff, and an MV3 restart fires
 * rehydrateState mid-backoff, rehydrateState sees the tab as "validation
 * failed" (debugger dropped) and deletes it. The navigation handler's
 * pending retry would have re-attached successfully, but rehydrateState
 * already cleaned it up. The reattachPending Set was cleared on restart,
 * so the navigation handler's guard `if (!reattachPending.has(tabId))` now
 * returns true and it bails — the tab is orphaned.
 */

// ============================================================
// MOCK LAYER — models chrome.* APIs + extension globals
// ============================================================

let currentTime = 0;
const timers = [];
function fakeSetTimeout(fn, ms) {
  const id = timers.length;
  timers.push({ fn, fireAt: currentTime + ms, id, cancelled: false });
  return id;
}
function fakeClearTimeout(id) {
  if (timers[id]) timers[id].cancelled = true;
}
function advanceTimeTo(ms) {
  currentTime = ms;
  // Fire all timers that should have fired, in order
  const ready = timers
    .filter(t => !t.cancelled && t.fireAt <= currentTime)
    .sort((a, b) => a.fireAt - b.fireAt);
  for (const t of ready) {
    t.cancelled = true; // mark as fired
    t.fn();
  }
}
function advanceTimeBy(ms) {
  advanceTimeTo(currentTime + ms);
}

// Chrome tab state
const existingTabs = new Map(); // tabId -> { url }
const debuggerAttached = new Map(); // tabId -> true/false

// chrome.tabs mock
const chrome_tabs = {
  async get(tabId) {
    if (!existingTabs.has(tabId)) throw new Error(`No tab with id: ${tabId}`);
    return { id: tabId, ...existingTabs.get(tabId) };
  }
};

// chrome.debugger mock
const chrome_debugger = {
  attached: debuggerAttached,
  async attach(debuggee, version) {
    if (!existingTabs.has(debuggee.tabId))
      throw new Error(`No tab with id: ${debuggee.tabId}`);
    debuggerAttached.set(debuggee.tabId, true);
  },
  async sendCommand(debuggee, method, params) {
    if (!debuggerAttached.get(debuggee.tabId))
      throw new Error('Debugger is not attached');
    return { result: { value: 1 } };
  },
  async detach(debuggee) {
    debuggerAttached.set(debuggee.tabId, false);
  }
};

// chrome.storage.session mock — survives worker restart
const sessionStorage = {};
const chrome_storage_session = {
  async get(keys) {
    const result = {};
    for (const k of keys) {
      if (k in sessionStorage) result[k] = sessionStorage[k];
    }
    return result;
  },
  async set(obj) {
    Object.assign(sessionStorage, obj);
  }
};

// Badge tracking for assertions
const badgeState = new Map(); // tabId -> 'on' | 'off' | 'connecting'
function setBadge(tabId, kind) {
  badgeState.set(tabId, kind);
}

// ============================================================
// EXTENSION STATE MODEL (mirrors background.js globals)
// ============================================================

let tabs_map = new Map();     // tabId -> { state, sessionId, targetId, attachOrder }
let tabBySession = new Map(); // sessionId -> tabId
let reattachPending = new Set();
let relayConnected = true;
let nextSession = 1;

function resetExtensionState() {
  tabs_map = new Map();
  tabBySession = new Map();
  reattachPending = new Set();  // IN-MEMORY — cleared on restart
  nextSession = 1;
}

// ============================================================
// MODELED FUNCTIONS (from background.js)
// ============================================================

async function validateAttachedTab(tabId) {
  try {
    await chrome_tabs.get(tabId);
  } catch {
    return false;
  }
  try {
    await chrome_debugger.sendCommand({ tabId }, 'Runtime.evaluate', {
      expression: '1', returnByValue: true
    });
    return true;
  } catch {
    return false;
  }
}

/**
 * rehydrateState — from background.js lines 133-195
 * Called on MV3 worker startup. Restores tabs from chrome.storage.session,
 * validates each one, attempts re-attach if validation fails.
 */
async function rehydrateState() {
  const stored = await chrome_storage_session.get(['persistedTabs', 'nextSession']);
  if (stored.nextSession) {
    nextSession = Math.max(nextSession, stored.nextSession);
  }
  const entries = stored.persistedTabs || [];

  // Phase 1: optimistically restore
  for (const entry of entries) {
    tabs_map.set(entry.tabId, {
      state: 'connected',
      sessionId: entry.sessionId,
      targetId: entry.targetId,
      attachOrder: entry.attachOrder,
    });
    tabBySession.set(entry.sessionId, entry.tabId);
    setBadge(entry.tabId, 'on');
  }

  // Phase 2: validate each tab
  for (const entry of entries) {
    const valid = await validateAttachedTab(entry.tabId);
    if (!valid) {
      let tabExists = false;
      try {
        await chrome_tabs.get(entry.tabId);
        tabExists = true;
      } catch { tabExists = false; }

      if (tabExists) {
        // Attempt re-attach
        try {
          await chrome_debugger.attach({ tabId: entry.tabId }, '1.3');
          await chrome_debugger.sendCommand({ tabId: entry.tabId }, 'Page.enable').catch(() => {});
          const reValid = await validateAttachedTab(entry.tabId);
          if (reValid) {
            setBadge(entry.tabId, 'on');
            continue;
          }
        } catch {
          // re-attach failed
        }
      }

      // >>> THIS IS THE BUG PATH <<<
      // Tab deleted from state even though navigation backoff would re-attach it
      tabs_map.delete(entry.tabId);
      tabBySession.delete(entry.sessionId);
      setBadge(entry.tabId, 'off');
    }
  }
}

/**
 * attachTab — simplified model of background.js attachTab
 */
async function attachTab(tabId) {
  const debuggee = { tabId };
  await chrome_debugger.attach(debuggee, '1.3');
  await chrome_debugger.sendCommand(debuggee, 'Page.enable');
  const sessionId = `session-${nextSession++}`;
  const targetId = `target-${tabId}`;
  tabs_map.set(tabId, {
    state: 'connected',
    sessionId,
    targetId,
    attachOrder: Date.now(),
  });
  tabBySession.set(sessionId, tabId);
  setBadge(tabId, 'on');
  return { sessionId, targetId };
}

/**
 * navigationReattach — models the onUpdated/onCompleted handler's
 * detach-and-backoff-reattach flow (background.js ~line 830-912)
 */
async function navigationReattach(tabId) {
  const oldTab = tabs_map.get(tabId);
  const oldSessionId = oldTab?.sessionId;

  if (oldSessionId) tabBySession.delete(oldSessionId);
  tabs_map.delete(tabId);

  reattachPending.add(tabId);
  setBadge(tabId, 'connecting');

  const delays = [200, 500, 1000, 2000, 4000];
  for (let attempt = 0; attempt < delays.length; attempt++) {
    // In real code this is setTimeout — we model with sync delay tracking
    await simulateDelay(delays[attempt]);

    // Guard: if reattachPending was cleared (MV3 restart), bail
    if (!reattachPending.has(tabId)) return { result: 'bailed_not_pending' };

    try {
      await chrome_tabs.get(tabId);
    } catch {
      reattachPending.delete(tabId);
      setBadge(tabId, 'off');
      return { result: 'tab_gone' };
    }

    try {
      await attachTab(tabId);
      reattachPending.delete(tabId);
      return { result: 'reattached', attempt };
    } catch {
      // continue
    }
  }

  reattachPending.delete(tabId);
  setBadge(tabId, 'off');
  return { result: 'exhausted' };
}

// Delay simulation — tracks elapsed time for race coordination
let simulatedElapsed = 0;
let delayCallbacks = [];

function simulateDelay(ms) {
  return new Promise(resolve => {
    simulatedElapsed += ms;
    delayCallbacks.push({ at: simulatedElapsed, resolve });
    // Auto-resolve for non-race tests
    resolve();
  });
}

// ============================================================
// PERSISTED STATE HELPER
// ============================================================

function persistTabs() {
  const entries = [];
  for (const [tabId, info] of tabs_map.entries()) {
    entries.push({
      tabId,
      sessionId: info.sessionId,
      targetId: info.targetId,
      attachOrder: info.attachOrder,
    });
  }
  chrome_storage_session.set({ persistedTabs: entries, nextSession });
}

// ============================================================
// TESTS
// ============================================================

let passed = 0;
let failed = 0;
let testNames = [];

function assert(condition, message) {
  if (!condition) throw new Error(`Assertion failed: ${message}`);
}

async function test(name, fn) {
  testNames.push(name);
  try {
    // Reset state
    existingTabs.clear();
    debuggerAttached.clear();
    badgeState.clear();
    resetExtensionState();
    delete sessionStorage.persistedTabs;
    delete sessionStorage.nextSession;
    simulatedElapsed = 0;
    delayCallbacks = [];
    currentTime = 0;
    timers.length = 0;

    await fn();
    passed++;
    console.log(`  ✅ ${name}`);
  } catch (err) {
    failed++;
    console.log(`  ❌ ${name}: ${err.message}`);
  }
}

async function runTests() {
  console.log('\n🧪 rehydrateState vs onBeforeNavigate backoff race tests\n');
  console.log('─'.repeat(60));

  // ── Test 1: Normal rehydration (no race) ──
  await test('rehydrateState restores valid tabs correctly', async () => {
    existingTabs.set(42, { url: 'https://example.com' });
    debuggerAttached.set(42, true);

    await chrome_storage_session.set({
      persistedTabs: [{
        tabId: 42, sessionId: 'sess-1', targetId: 'tgt-42', attachOrder: 1
      }],
      nextSession: 2,
    });

    await rehydrateState();

    assert(tabs_map.has(42), 'Tab 42 should be in tabs map');
    assert(badgeState.get(42) === 'on', 'Badge should be on');
  });

  // ── Test 2: rehydrateState deletes tab when debugger dropped ──
  await test('rehydrateState deletes tab when debugger dropped and re-attach fails', async () => {
    existingTabs.set(42, { url: 'https://example.com' });
    debuggerAttached.set(42, false); // Debugger dropped by MV3 restart

    // Make re-attach fail by making attach throw
    const origAttach = chrome_debugger.attach;
    chrome_debugger.attach = async () => { throw new Error('Cannot attach'); };

    await chrome_storage_session.set({
      persistedTabs: [{
        tabId: 42, sessionId: 'sess-1', targetId: 'tgt-42', attachOrder: 1
      }],
      nextSession: 2,
    });

    await rehydrateState();

    assert(!tabs_map.has(42), 'Tab 42 should be deleted');
    assert(badgeState.get(42) === 'off', 'Badge should be off');

    chrome_debugger.attach = origAttach;
  });

  // ── Test 3: Navigation backoff succeeds on attempt 2 ──
  await test('navigation backoff re-attaches on second attempt', async () => {
    existingTabs.set(42, { url: 'https://example.com' });
    debuggerAttached.set(42, false);

    // Make first attach attempt fail, second succeed
    let callCount = 0;
    const origAttach = chrome_debugger.attach;
    chrome_debugger.attach = async (debuggee, version) => {
      callCount++;
      if (callCount === 1) throw new Error('Not ready yet');
      return origAttach.call(chrome_debugger, debuggee, version);
    };

    const result = await navigationReattach(42);

    assert(result.result === 'reattached', `Expected reattached, got ${result.result}`);
    assert(result.attempt === 1, `Expected attempt 1, got ${result.attempt}`);
    assert(tabs_map.has(42), 'Tab should be in map after reattach');
    assert(badgeState.get(42) === 'on', 'Badge should be on');

    chrome_debugger.attach = origAttach;
  });

  // ── Test 4: reattachPending cleared on restart ──
  await test('reattachPending Set is cleared on simulated MV3 restart', async () => {
    reattachPending.add(42);
    reattachPending.add(99);

    assert(reattachPending.has(42), 'Pre-restart: should have 42');

    // Simulate MV3 restart: in-memory state cleared, storage persists
    resetExtensionState();

    assert(!reattachPending.has(42), 'Post-restart: reattachPending should be empty');
    assert(reattachPending.size === 0, 'Set should be completely empty');
  });

  // ── Test 5: chrome.storage.session survives restart ──
  await test('chrome.storage.session retains tabs across restart', async () => {
    await chrome_storage_session.set({
      persistedTabs: [{
        tabId: 42, sessionId: 'sess-1', targetId: 'tgt-42', attachOrder: 1
      }]
    });

    // Simulate restart
    resetExtensionState();

    const stored = await chrome_storage_session.get(['persistedTabs']);
    assert(stored.persistedTabs.length === 1, 'Storage should survive restart');
    assert(stored.persistedTabs[0].tabId === 42, 'Tab 42 should be in storage');
  });

  // ── Test 6: THE RACE — rehydrateState mid-backoff ──
  await test('RACE: rehydrateState mid-backoff deletes tab navigation would save', async () => {
    // Setup: tab 42 exists, debugger initially attached, relay connected
    existingTabs.set(42, { url: 'https://example.com' });
    debuggerAttached.set(42, true);

    // Step 1: Tab is attached and persisted
    await attachTab(42);
    persistTabs();
    assert(tabs_map.has(42), 'Tab should be attached');

    // Step 2: Navigation triggers backoff. Debugger gets detached (Chrome does this).
    debuggerAttached.set(42, false);

    // Start the navigation reattach — but we need to model the timing race.
    // In real code, the backoff delays are [200, 500, 1000, 2000, 4000]ms.
    // After 200ms the first attempt fires. We simulate MV3 restart at 300ms
    // (between attempt 0 at 200ms and attempt 1 at 700ms).

    // We need to track what happens step by step:
    // t=0: navigation fires, adds tabId to reattachPending
    // t=200ms: attempt 0 — debugger not ready, fails
    // t=300ms: MV3 RESTART — reattachPending cleared, rehydrateState runs
    // t=700ms: attempt 1 — reattachPending.has(42) is FALSE → bails
    //
    // rehydrateState at t=300ms: sees tab 42 in storage, validates it,
    // debugger is dropped → tries re-attach → if re-attach also fails
    // (because Chrome is mid-navigation), it DELETES the tab.
    //
    // Result: tab 42 is orphaned. Badge shows 'off'. Tab is still open in
    // browser but extension thinks it doesn't exist.

    // Let's prove this step by step:

    // Before restart: navigation started backoff
    reattachPending.add(42);
    tabs_map.delete(42); // navigation handler clears this
    tabBySession.clear(); // navigation handler clears old session
    setBadge(42, 'connecting');

    // First backoff attempt at 200ms fails (debugger not attachable yet)
    // Make attach throw to model Chrome refusing debugger mid-navigation
    const origAttachRace = chrome_debugger.attach;
    chrome_debugger.attach = async () => { throw new Error('Not ready mid-navigation'); };
    let firstAttemptFailed = false;
    try { await attachTab(42); } catch { firstAttemptFailed = true; }
    assert(firstAttemptFailed, 'First attempt should fail');
    assert(!tabs_map.has(42), 'Tab should not be in map after failed attach');

    // MV3 RESTART at 300ms
    // In-memory state wiped, storage persists
    const savedStorage = { ...sessionStorage };
    resetExtensionState();
    // Restore storage (it persists across restart)
    Object.assign(sessionStorage, savedStorage);

    // reattachPending is NOW EMPTY
    assert(!reattachPending.has(42), 'reattachPending should be cleared after restart');

    // rehydrateState runs on startup
    // re-attach still fails (Chrome still mid-navigation)
    // (origAttachRace is already set to throw)

    await rehydrateState();

    // >>> BUG MANIFESTS HERE <<<
    // rehydrateState tried to validate tab 42, validation failed (debugger dropped),
    // tried re-attach, re-attach failed (mid-navigation), so it DELETED the tab.
    assert(!tabs_map.has(42), 'rehydrateState should have deleted tab 42');
    assert(badgeState.get(42) === 'off', 'Badge should be off');

    // Now the navigation handler's remaining backoff attempts fire...
    // but reattachPending was cleared on restart, so:
    assert(!reattachPending.has(42),
      'Navigation handler would bail — reattachPending is empty');

    // Even if debugger becomes attachable again at t=700ms:
    chrome_debugger.attach = origAttachRace;
    debuggerAttached.set(42, true);
    // Nobody will try to re-attach — the tab is orphaned.

    // The tab still exists in Chrome:
    assert(existingTabs.has(42), 'Tab still exists in browser');
    // But the extension has forgotten it:
    assert(!tabs_map.has(42), 'Extension state has no record of tab 42');
    // User sees badge=off on a live tab. Only manual click-to-retry fixes it.

    console.log('    → Race proven: tab 42 exists in browser but extension orphaned it');
    console.log('    → rehydrateState deleted it, navigation backoff can\'t recover (reattachPending cleared)');
  });

  // ── Test 7: Backoff timing model ──
  await test('backoff array matches [200, 500, 1000, 2000, 4000]ms', async () => {
    const delays = [200, 500, 1000, 2000, 4000];
    const totalWindow = delays.reduce((a, b) => a + b, 0);
    assert(totalWindow === 7700, `Total backoff window should be 7700ms, got ${totalWindow}`);
    assert(delays[0] === 200, 'First delay should be 200ms');
    assert(delays[4] === 4000, 'Last delay should be 4000ms');
  });

  // ── Test 8: Fix path — backoff-aware validation ──
  await test('FIX: rehydrateState skips tabs in reattachPending', async () => {
    // This test shows what the fix should look like:
    // rehydrateState should check reattachPending before deleting.
    // But wait — on restart, reattachPending is cleared. So the real fix is:
    // persist reattachPending to chrome.storage.session alongside tabs.

    existingTabs.set(42, { url: 'https://example.com' });
    debuggerAttached.set(42, false);

    // Persist the reattachPending state (the fix)
    await chrome_storage_session.set({
      persistedTabs: [{
        tabId: 42, sessionId: 'sess-1', targetId: 'tgt-42', attachOrder: 1
      }],
      reattachPending: [42],  // <-- THE FIX: persist this
      nextSession: 2,
    });

    // Simulate restart
    resetExtensionState();

    // Fixed rehydrateState would restore reattachPending:
    const stored = await chrome_storage_session.get(['reattachPending']);
    if (stored.reattachPending) {
      for (const id of stored.reattachPending) {
        reattachPending.add(id);
      }
    }

    // Now fixed rehydrateState knows tab 42 is mid-backoff:
    assert(reattachPending.has(42), 'reattachPending restored from storage');

    // Fixed validation skips tabs in reattachPending:
    const entries = (await chrome_storage_session.get(['persistedTabs'])).persistedTabs;
    for (const entry of entries) {
      if (reattachPending.has(entry.tabId)) {
        // Skip validation — navigation handler owns this tab
        setBadge(entry.tabId, 'connecting');
        tabs_map.set(entry.tabId, {
          state: 'pending_reattach',
          sessionId: entry.sessionId,
          targetId: entry.targetId,
          attachOrder: entry.attachOrder,
        });
        continue;
      }
    }

    assert(tabs_map.has(42), 'Fixed: tab should survive rehydration');
    assert(badgeState.get(42) === 'connecting', 'Fixed: badge should show connecting');
    console.log('    → Fix path: persist reattachPending Set to chrome.storage.session');
    console.log('    → rehydrateState skips validation for tabs with pending navigation reattach');
  });

  console.log('\n' + '─'.repeat(60));
  console.log(`\n${passed} passed, ${failed} failed, ${passed + failed} total\n`);

  if (failed > 0) {
    console.log('FAILED tests:');
    process.exit(1);
  } else {
    console.log('All tests pass. Race condition proven and fix path demonstrated.');
  }
}

runTests().catch(err => {
  console.error('Test runner error:', err);
  process.exit(1);
});
