# StarAgent second ghosting bug canonical note — 2026-03-27

## Delivered bug
Reducer treats:
- `protocol_valid = true`
- `evidence_present = false`
- `deadline_missed = false`

as:
- `invalid_protocol`

instead of:
- `pending`

## Correct rule
Before deadline, post-validity evidence absence is a waiting state, not a protocol-authoring failure.

## Minimal branch-order fix
If:
- `protocol_valid = true`
- `evidence_present = false`
- `deadline_missed = false`

then emit:
- `pending`

and only after deadline transition to:
- `ghosted_counterparty`

## One-line invariant
**Absence is region-scoped.** After `protocol_valid = true`, `!evidence_present` routes to `pending` before deadline and `ghosted_counterparty` after deadline — never `invalid_protocol`.
