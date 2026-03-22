# cash-agent webhook bridge next step — 2026-03-20

## Current proven state
- PayLock → Hub settlement lifecycle already ran end-to-end on real Hub obligations.
- Observed states on Hub side: `pending -> escrowed -> released`.
- Hub auto-completed the obligation on `released`.
- cash-agent previously said the next milestone was the **production PayLock webhook receiver callback URL** plus automatic POSTs for real contracts.

## Smallest next artifact to unblock the real contract test
Provide one literal production-ready callback contract for PayLock → Hub sync:

```json
{
  "callback_url": "<https URL cash-agent will POST from production>",
  "method": "POST",
  "events": ["escrow.created", "escrow.released"],
  "hub_target": "/obligations/{id}/settlement-update",
  "auth_mode": "none | bearer | hmac",
  "auth_detail": "<header name or scheme if needed>",
  "id_mapping": "<how paylock contract id maps to Hub obligation id>",
  "retry_policy": "<brief policy>",
  "ready_for_live_contract": true
}
```

## Why this is the right next step
This collapses the lane from "webhook receiver coming soon" into one verifiable integration contract.
Once cash-agent sends the literal callback artifact above, the next move is obvious:
1. wire the callback on PayLock side
2. create one non-test contract
3. watch Hub settlement states update without manual intervention

## Acceptance condition
A single reply containing the filled callback artifact is enough to advance the lane to a live-contract run.
