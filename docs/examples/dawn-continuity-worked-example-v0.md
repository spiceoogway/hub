# Dawn continuity worked example v0

Date: 2026-03-08
Lane: `dawn`

## What manual step this closes

Without a typed wake-transition object, the agent has to recover the gap between:

1. what was known before sleep
2. what was missing after wake
3. what was rebuilt manually
4. what is still unsafe to trust

The example pair makes that path explicit:

- `dawn-wake-transition-example-v0.json` = lowest-friction fill-in artifact
- `dawn-continuity-checkpoint-example-v0.json` = normalized checkpoint object after conversion

## Why this is better than another prose note

It turns an easy-to-lose reconstruction step into visible fields:

- loss surface: `missing_after_wake`
- manual labor: `reconstructed_manually` / `reconstructed_fields`
- residual danger: `still_missing` / `freshness_verified=false`
- exact next action: `resume_action_line`

## Remaining live unknown

The example suggests the load-bearing missing field may be **freshness semantics** rather than identity or permissions.

The hard question is: after wake, how do we know the reconstructed state is still fresh enough to trust?

Candidate shapes:

1. `stale_after_utc`
2. `head_snapshot_id`
3. `reconstruction_confidence`

If none of those are right, the next real wake transition should show what is actually missing.
