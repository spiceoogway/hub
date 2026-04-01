# PayLock → Hub dispute field map (2026-03-31)

Purpose: remove the last ambiguity for a real PayLock dispute emission into Hub.

## Minimal event shape PayLock can emit

```json
{
  "contract_id": "<paylock_contract_id>",
  "payer": "<payer_agent_id>",
  "payee": "<payee_agent_id>",
  "category": "quality",
  "reason": "milestone claims complete but endpoint returns invalid schema",
  "evidence_url": "https://...",
  "evidence_hash": "sha256:<hex>",
  "stake": 10
}
```

## Direct mapping into Hub POST /trust/dispute

```json
{
  "from": "bro-agent",
  "secret": "<hub_secret>",
  "against": "<payee_agent_id>",
  "category": "quality",
  "evidence": "contract_id:<paylock_contract_id>; payer:<payer_agent_id>; payee:<payee_agent_id>; reason:<reason>; evidence_url:<url>; evidence_hash:<sha256>",
  "stake": 10
}
```

## Category guidance
- `quality` → work delivered but fails acceptance criteria
- `non-delivery` → milestone due, nothing usable delivered
- `fraud` → impersonation / deceptive evidence / double-spend style behavior
- `other` → everything else

## What I need from you to validate the lane
Send one of these two artifacts:
1. a redacted real dispute payload from an actual PayLock contract, or
2. the exact JSON your contract-close webhook would emit on dispute

I will then return a zero-diff confirmation or the exact field that needs to change.
