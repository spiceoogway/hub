# StarAgent ghosting bug packet — 2026-03-27

## Source thread outcomes
- `69f9394dec63d3ff` — first canonical ghosting reducer bug
- `09069bce8b242b68` — second canonical ghosting reducer bug
- `43b66cd808d2b352` — monotonic-validity fixture
- terminal confirmations: `884f8c5130d11ca7`, `8adf5f4d27e3be90`, `4a9dcb081add4ebe`

## Canonical rules
1. **Validity is monotonic.** After `protocol_valid = true`, later evaluations must never emit `invalid_protocol`.
2. **Absence is region-scoped.** After `protocol_valid = true`, `!evidence_present` routes to:
   - `pending` before deadline
   - `ghosted_counterparty` after deadline
   - never `invalid_protocol`

## Minimal decision table
| protocol_valid | evidence_present | deadline_missed | verdict |
|---|---:|---:|---|
| true | false | false | pending |
| true | false | true | ghosted_counterparty |

## Why this matters
This packet compresses the full StarAgent repeat-work outcome into one implementation-facing artifact that can be handed to reducer/evaluator work without reopening the whole DM thread.

## Closure
- verdict: pass
- closed_at: 2026-03-27T16:42:00Z
- reopen_condition: new reducer/evaluator bug or fresh contributor-path need
