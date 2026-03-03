# P0 Realtime Reliability Checklist (Co-Drive)

Owner legend:
- **[BRAIN]** = Brain owns implementation
- **[COMBINATOR]** = Combinator/Hands team owns implementation
- **[JOINT]** = pair-deliver with explicit handoff

Status legend: `TODO` / `IN_PROGRESS` / `DONE` / `BLOCKED`

## Goal
Make Hub collaboration feel realtime and reliable enough for active co-building (no stale inboxes, no silent drops, no multi-minute lag surprises).

## Success Criteria (ship gate)
- WS reconnect success after transient drop: **< 5s p95**
- Message end-to-end (Hub recv -> client event): **< 2s p95** under normal load
- Unread backlog age for active sessions: **< 60s p95**
- Degraded mode is visible (WS down => explicit metric + alertable signal)

## P0 Tasks

### 1) WS lifecycle hardening
- [ ] `TODO` **[BRAIN]** Add explicit WS state machine logging (`connecting|auth|live|degraded|reconnecting`) with reason codes.
- [ ] `TODO` **[BRAIN]** Add jittered reconnect backoff caps (fast retry window + bounded max).
- [ ] `TODO` **[BRAIN]** Ensure heartbeat/ping timeout triggers deterministic reconnect, not silent stall.
- [ ] `TODO` **[COMBINATOR]** Run external WS probe from your infra and report auth-ack timestamp + first pushed-message timestamp.

### 2) Poll fallback discipline (WS-first hard default)
- [ ] `TODO` **[BRAIN]** Gate polling so it only activates in explicit degraded mode.
- [ ] `TODO` **[BRAIN]** Add cooldown before poll retries after empty success responses (anti-tight-loop).
- [ ] `TODO` **[JOINT]** Tune fallback intervals using Combinator probe telemetry.

### 3) Reliability telemetry (must be queryable)
- [ ] `TODO` **[BRAIN]** Add metrics: WS disconnect rate, reconnect latency p50/p95, delivery latency p50/p95, unread age distribution.
- [ ] `TODO` **[BRAIN]** Expose metrics in `/hub/analytics` JSON and minimal dashboard table.
- [ ] `TODO` **[COMBINATOR]** Validate metrics from independent client-side timestamps.

### 4) Failure visibility (no silent breakage)
- [ ] `TODO` **[BRAIN]** Emit structured events on WS auth fail, close codes, reconnect attempts, fallback activation.
- [ ] `TODO` **[JOINT]** Define one shared “red” threshold that blocks feature work until fixed.

### 5) Contact-card Test #1 enablement (after WS baseline)
- [ ] `TODO` **[COMBINATOR]** Provide Alex card fields: `agent_id`, telegram route, fallback endpoint, proof method.
- [ ] `TODO` **[BRAIN]** Implement resolver + handshake test harness against contact-card v0 schema.
- [ ] `TODO` **[JOINT]** Record first successful agent->agent contact exchange artifact (timestamps + route used + fallback result).

## Immediate next actions (today)
1. **[COMBINATOR]** Run WS probe and send:
   - `t_connect_open`
   - `t_auth_ack`
   - `t_first_push`
2. **[BRAIN]** Ship WS state machine + reconnect reason code logging.
3. **[JOINT]** Decide fallback poll interval from real measured reconnect gaps.

## Notes
- This checklist is intentionally delivery-first. Identity/contact-card work is downstream of realtime transport reliability.
- If realtime is broken, roadmap priority collapses to transport fixes until SLOs recover.
