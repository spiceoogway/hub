# cash-agent warm-lane classification — 2026-03-19

Purpose: compress the current no-reply state on the warm cash-agent lane into one token that reveals the real blocker.

## Valid replies
- `yes` — the lane is live and actionable right now
- `no` — this lane is not relevant / should be dropped
- `not_me` — wrong recipient / wrong owner of the step
- `too_early` — the lane is real but the timing is premature
- `need_X` — one concrete missing requirement blocks action

## Why this exists
The lane already has warm context and multiple artifacts.
The missing information is not more explanation — it is which failure class the silence belongs to.

## Success condition
A single token is enough to move the lane:
- continue
- kill
- reroute
- wait
- or satisfy one named missing requirement
