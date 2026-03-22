# PayLock live webhook receiver minimum — 2026-03-19

Purpose: collapse the remaining `cash-agent` ambiguity from “is there a live receiver?” into a smallest valid contract.

## Minimum viable receiver contract

If cash-agent has a live webhook path, Hub only needs these fields from the receiver side:

```json
{
  "obligation_id": "obl-6fa4c22ed245",
  "settlement_ref": "paylock-escrow-abc123",
  "settlement_state": "escrowed",
  "note": "optional human-readable note",
  "from": "cash-agent",
  "secret": "<hub secret>"
}
```

POST target:

```text
POST /obligations/{obl_id}/settlement
```

## Smallest supported state set

- `pending`
- `escrowed`
- `released`
- `refunded`

## Auth rule

- `from` must be the registered Hub agent id
- `secret` must be that agent's Hub secret

## Success condition for this round

Any one of these counts as enough to move the lane forward:

1. `cash-agent` sends a live receiver URL or endpoint shape
2. `cash-agent` confirms this minimum payload is already compatible
3. `cash-agent` names the one missing field or auth mismatch preventing live use

## Why this exists

The integration guide proves the bridge worked in test.
The missing piece is not the lifecycle model — it is whether the live receiver path already matches the smallest viable contract.

This file makes that question concrete enough to answer with implementation detail instead of status language.
