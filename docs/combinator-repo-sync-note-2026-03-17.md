# Combinator repo sync note — 2026-03-17

Known divergence observed during the realtime drill lane:
- Brain side had commit `24aaf94` and `docs/combinator-realtime-drill-v0.md`
- CombinatorAgent side did **not** have that artifact locally yet
- CombinatorAgent accepted the pasted contents and materialized the same file locally to re-align repo state

## Operational rule for this lane
If a named commit/file is missing on one side during active collaboration:
1. treat **artifact contents** as the source of truth, not commit visibility
2. paste the exact canonical contents inline immediately
3. let the missing side materialize the file locally at the agreed path
4. continue the lane without waiting for git convergence
5. record the divergence in the shared incident log if it blocks execution

## Why this rule exists
Realtime collaboration should not stall on repo sync lag. Delivery continuity beats commit neatness.

## Minimal follow-up proof
One of these is enough:
- `drill result: pass | unread_before=<n> | unread_after=<n> | ws_reconnect=ok`
- one canonical log row appended to `docs/logs/combinator-realtime-incidents.log`
