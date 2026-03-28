# StarAgent ghosting bug canonical note — 2026-03-27

## Delivered bug
`invalid_protocol` is being emitted whenever `evidence_present = false`, even after `protocol_valid = true`.

## Correct rule
Once `protocol_valid = true`, later evidence absence must route by deadline/counterparty state, not by authoring blame.

## Minimal branch-order fix
If:
- `protocol_valid = true`
- `evidence_present = false`
- `deadline_missed = true`

then emit:
- `ghosted_counterparty`

and never fall through to:
- `invalid_protocol`

## One-line invariant
**Validity is monotonic.** After `protocol_valid = true`, the reducer must never later emit `invalid_protocol` for the same case.
