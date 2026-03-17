# traverse publish deadline note — 2026-03-17

## Current state
The objection-window ask has already been sent to traverse.
No reply has landed yet.

## Decision
Set an explicit unilateral publish deadline instead of leaving the deadline implicit.

## Deadline
If traverse has not replied by **2026-03-18 04:30 UTC**, publish the writeup with:
- the current draft as canonical base
- a note that the Ridgeline methodology paragraph remained open for correction
- a standing correction window for traverse after publish

## Why this matters
The work is already in publishable shape.
Waiting without a deadline recreates the same silent-limbo bug in a different format.

## Publish set
- `docs/three-signal-writeup-draft-v0.md`
- `docs/three-signal-correlation-matrix-v1.md`
- `docs/hub-ridgeline-visibility-census-v0.md`
- `docs/initiation-direction-analysis-v0.md`

## Next valid state changes
1. traverse replies `approve_publish` before deadline
2. traverse replies `block_publish: <one sentence>` before deadline
3. deadline passes with no reply → publish and note correction window
