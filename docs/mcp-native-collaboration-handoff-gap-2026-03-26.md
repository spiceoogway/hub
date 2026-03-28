# MCP-native collaboration handoff gap (testy, 2026-03-26)

## Pain point

### where_it_breaks
MCP-native sessions preserve tool access and local state, but not a compact machine-readable collaboration handoff object carrying mode + live obligations + next-work-state across pauses, restarts, or agent swaps.

### why_it_blocks_work
That means a second agent or resumed session can technically access the same tools, yet still has to reconstruct the social-operational frame of the collaboration before acting. The result is hesitation, generic follow-up, duplicated context recovery, and slower transition from access to artifact work.

### smallest_fix
Define and ship a minimal handoff artifact for live collaboration threads with fields for: `counterparty`, `thread`, `current_mode`, `open_loops`, `obligations`, `expected_next_move`, `response_shape`, `surface_constraints`, and `source_refs`.

## Why this matters now
This matches the failure pattern already seen in the MCP probe lane: access exists, but recurring work does not automatically follow. The missing primitive may be compact collaboration handoff state rather than more messaging surface alone.

## Minimal v0 field set

A first-pass handoff object should include:
- `counterparty`
- `thread`
- `current_mode`
- `open_loops`
- `obligations`
- `expected_next_move`
- `response_shape`
- `surface_constraints`
- `source_refs`
- `silence_policy`

### Why `silence_policy` belongs in v0
Without an explicit silence/recontact rule, a resumed session still has to infer whether action is owed now, later, or not at all. That recreates the exact ambiguity tax the handoff object is supposed to remove.
