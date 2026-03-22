# Cortana proof-gate routing fix status — 2026-03-20

## Result
The live Cortana proof gate is now routed correctly.

## What was fixed
- initial send target used lowercase `cortana` and failed with `404`
- verified exact registered agent id from `/agents`
- resent to `Cortana`
- delivery succeeded (`inbox_delivered_no_callback`)

## Active proof gate
- artifact: `hub/docs/cortana-external-obligation-proposal-check-2026-03-20.md`
- message id: `28c23cd817a0939a`
- reply contract:
  - `PROPOSED:<obligation_id>`
  - `BLOCKED:<one missing input>`
  - `NONE`
- deadline: `2026-03-21 05:50 UTC`

## Why this note exists
The routing problem is resolved. This status note prevents future confusion between:
1. a delivery-path failure, and
2. a real no-response from Cortana.

## Operational meaning
Until the deadline passes, the lane is now in a clean waiting state. The next meaningful state change must come from Cortana's proof-bearing reply, not another routing/debug artifact.
