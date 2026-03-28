# StarAgent ghosting reducer ordering note — 2026-03-27

## Bug
Reducer treats `!evidence_present` as a context-free terminal and emits `invalid_protocol` even after `protocol_valid = true`.

## Correct rule
`!evidence_present` is region-scoped:
- pre-validity: may support `invalid_protocol`
- post-validity + deadline not missed: `awaiting_evidence`
- post-validity + deadline missed: `ghosted_counterparty`

## Minimal reducer order
```text
if !protocol_valid:
  invalid_protocol
elif evidence_present:
  shipped | fail | blocked
elif deadline_missed:
  ghosted_counterparty
else:
  awaiting_evidence
```

## Invariant
**Validity is monotonic.** Once `protocol_valid = true`, the reducer must never emit `invalid_protocol` later.

Forbidden transition:
```text
protocol_valid = true  =>  not invalid_protocol
```

If that transition exists, the reducer is laundering execution failure back into authoring failure.
