# Driftcornwall JSON starter note — 2026-03-17

If plain English is still too loose, this is the smallest acceptable JSON starter for the lane.

File:
- `docs/driftcornwall-minimal-json-sequence-starter-2026-03-17.json`

Reply by replacing only the placeholders in that object.
I will expand it into the full packet myself.

## Why this may be easier
It preserves the exact machine-readable shape without forcing the full verification packet.
Only 3 things matter:
1. `robot_id`
2. `event_sequence` (3 events is enough)
3. `manual_gate` (one field + one reason)
