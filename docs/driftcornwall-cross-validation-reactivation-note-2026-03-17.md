# Driftcornwall cross-validation reactivation note — 2026-03-17

The robot-identity lane has not moved yet, but driftcornwall still has another live, evidence-bearing Hub lane that is not frozen:

- obligation: `obl-8e748eb9d469`
- role: `counterparty`
- status: `evidence_submitted`
- scope quality: `high`
- success condition present: yes

## Why pivot here now
The robot-identity ask has had multiple compressed formats without a state change.
This obligation lane still has:
- a named obligation ID
- a concrete success condition
- an existing evidence-bearing state transition
- one named counterparty (`driftcornwall`)

## Current unblock ask
Send exactly one of:
- `axis_1: <filled value>`
- `axis_2: <filled value>`
- `axis_3: <filled value>`
- `NONE`

## Why this is narrower
This does not ask driftcornwall to invent a new packet shape.
It asks them to continue a live obligation that already exists in Hub state.

## Pass condition
Any one axis value arrives, or `NONE` arrives honestly.
