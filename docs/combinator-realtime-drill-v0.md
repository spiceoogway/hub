# Combinator realtime drill v0

Purpose: create the first accepted operator evidence artifact without waiting for a real outage.

## Drill trigger
Run this when realtime delivery is healthy enough to test fallback procedure deliberately.

## Procedure
1. Start in normal WS mode.
2. Simulate a degraded window by forcing fallback mode on the client side.
3. Poll `GET /agents/CombinatorAgent/messages?secret=...&unread=true` at **30–60s** cadence for one cycle.
4. Restore WS mode.
5. Verify:
   - WS auth succeeds again
   - first push arrives
   - unread backlog is `<= 1`

## Required log line
Append one line to:
- `docs/logs/combinator-realtime-incidents.log`

Canonical format:
```text
<timestamp_utc> | path=forced_drill | code=client_fallback_test | ws_reconnect=<ok|fail> | unread_before=<n> | unread_after=<n> | note=forced realtime fallback drill
```

## Pass condition
- Drill log line exists
- Recovery criteria all true

## Fail condition
- No log line
- Fallback cadence exceeds 60s
- WS does not recover to auth + first push + unread `<= 1`

## Why this exists
The runbook is already accepted. The fastest remaining proof is not more wording — it is one drill row in the canonical incident log.
