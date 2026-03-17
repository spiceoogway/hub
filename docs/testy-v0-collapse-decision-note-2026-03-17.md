# testy v0 collapse decision note — 2026-03-17

Follow-up from `testy` on the rebind reducer ordering.

## Decision
Keep **`explicit frame`** and **`silence_policy`** **collapsed at v0**.

## Reason
In the current ontology, `silence_policy` is just the action-bearing slice of explicit frame state.
Splitting them now would create fake disagreement and force the evaluator to pretend there are two independent sources when there is really one.

## v0 rule
Treat them as one reducer input:
- `explicit_frame_or_silence_policy`

That collapsed input keeps the canonical ordering:

**explicit frame / silence_policy > open obligations > send_gate > waiting_on**

## Reopen split only if
One of these becomes true later:
1. the system starts storing `silence_policy` independently from frame state
2. there are real observed cases where frame semantics and silence semantics diverge
3. evaluator complexity at v1 actually buys disambiguation rather than fake precision

## Immediate implication
Do not add a separate evaluator field for `silence_policy` in v0.
Keep the surface small and honest.
