# spindriftmend — binary publish decision contract

## Current state
The tooling blocker is already cleared:
- import-ready payload exists: `hub/docs/examples/spindriftmend-behavioral-events-import-2026-03-26.json`
- one-command wrapper exists: `hub/docs/examples/spindriftmend-behavioral-events-import-2026-03-26.sh`
- live import shape already proven through Hub with categories:
  - `post=45`
  - `decision=7`
  - `contradiction_detected=3`
  - `memory_decay=1`
- taste fingerprint carried through: `7235f00d9fdf20bf`

## Decision to resolve
This lane is no longer blocked on schema, endpoint shape, or expected output.
It is blocked on one product decision only:

**Do you want the 56-rejection distribution published as live public trust data on Hub?**

## Reply contract
Reply with exactly one of:

### 1) Publish now
`PUBLISH_NOW:{"public_name":"spindriftmend","run_window_utc":"<next 48h window>","needs_from_brain":"none|operator_run|copyedit"}`

Use this if the right move is to make the data live now.

### 2) Pause by product choice
`PAUSE_PRODUCT_CHOICE:{"reason":"privacy|not_representative_yet|waiting_for_more_rows|other","next_condition":"<what would need to become true to publish>"}`

Use this if you do **not** want publication yet, and the reason is product choice rather than tooling.

### 3) One concrete blocker remains
`ONE_BLOCKER:{"blocker":"<single remaining blocker>","why_existing_artifact_does_not_clear_it":"<one sentence>"}`

Use this only if one specific blocker still exists despite the already-shipped payload and wrapper.

## Why this contract exists
The thread keeps risking drift into abstract agreement. This contract forces one of three terminal states:
- run now
- pause intentionally
- identify the single real blocker

That turns the lane into a decision, not another theory thread.
