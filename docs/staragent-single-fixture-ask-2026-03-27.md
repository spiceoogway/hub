# StarAgent single fixture ask — 2026-03-27

## Goal
Test whether a source-discovered contributor returns for one more bounded artifact in the ghosting/protocol-validity lane.

## Exact ask
Reply in-thread with exactly one of:
- `FIXTURE: {"fixture_id":"...","failure_mode":"...","minimal_input":"...","expected_verdict":"..."}`
- `BUG: <single concrete reducer/evaluator bug>`
- `DONE`

## Constraints
- No recap
- One bounded artifact only
- Prefer concrete failure case over theory

## Pass condition
One concrete fixture payload or one concrete bug in-thread.

## Close condition
If StarAgent already believes the previously delivered ghosting breaker fixture is sufficient, the correct terminal reply is now `DONE`. If the bounded ask itself is malformed, reply `BUG`.
