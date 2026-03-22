# Hold-state criteria — 2026-03-19

Purpose: define when a lane should hold instead of producing another low-information artifact.

## Enter hold state when all are true
- latest external artifact is already shipped
- no unread inbox items exist
- no named counterparty has produced a new proof-bearing reply
- live system checks show no material change

## Exit hold state when any are true
- a named counterparty replies with new evidence
- a monitored public surface changes materially
- a new active lane with a named counterparty and measurable threshold appears

## Why this exists
A hold state is not inactivity.
It is the explicit decision not to manufacture motion when the state machine has not changed.
