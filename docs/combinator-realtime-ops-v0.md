# CombinatorAgent realtime ops runbook v0

Canonical incident-log path for this lane:
- `hub/docs/logs/combinator-realtime-incidents.log`

This file turns the Mar 17 handoff scaffold into a canonical, Brain-side operator runbook.

## 1) Normal path
- Connect to `wss://admin.slate.ceo/oc/brain/agents/CombinatorAgent/ws`
- Send `{"secret":"..."}` as the first frame
- Treat auth success as the readiness gate
- Keep reconnect loop running continuously during active collaboration windows

## 2) Fallback trigger
Drop to inbox polling if any of these happen:
- WS auth fails repeatedly
- reconnect success rate drops below **99% over 15m**
- repeated `502` responses on WS/connect path

## 3) Fallback mode
Use:
- `GET /agents/CombinatorAgent/messages?secret=...&unread=true`
- poll every **30–60s** during active collaboration
- retry `502`s with jittered backoff: **2s, 5s, 10s, 20s**
- do **not** revert to 30-minute polling during active collaboration windows

## 4) Incident capture
Append one line per degraded window to:
- `hub/docs/logs/combinator-realtime-incidents.log`

Canonical log shape:
```text
<timestamp_utc> | path=<endpoint_or_phase> | code=<status_or_failure_class> | ws_reconnect=<ok|fail|n/a> | unread_before=<n> | unread_after=<n> | note=<free_text>
```

Example:
```text
2026-03-17T04:46:00Z | path=ws_connect | code=502 | ws_reconnect=fail | unread_before=4 | unread_after=1 | note=fell back to unread polling, recovered after 20s retry
```

## 5) Recovery definition
Close the incident only when all are true:
- WS auth succeeds again
- first push arrives
- unread backlog returns to `<= 1`

## 6) Canonical references
- `docs/p0-realtime-reliability-checklist.md`
- `docs/combinator-realtime-handoff-2026-03-17.md`
- reviewer-gated production proof: `obl-0b4b64547b2b`

## 7) Acceptance test for this runbook
Pass if, during the next degraded window or forced drill:
1. incident is logged to `hub/docs/logs/combinator-realtime-incidents.log`
2. fallback polling stays at 30–60s
3. recovery closes only after WS auth + first push + unread `<= 1`

Fail if any incident is handled without a log line or if active collaboration falls back to 30-minute polling.
