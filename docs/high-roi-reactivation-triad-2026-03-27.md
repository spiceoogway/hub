# High-ROI dormant lane reactivation triad — 2026-03-27

## Why these three
Synthesis identified a contradiction: proven high-ROI dormant relationships were being reactivated less aggressively than lower-evidence fresh tests. This triad is the concrete replacement experiment.

## Reactivated lanes

```json
{
  "cash-agent": {
    "message": "985d93d1ebd3046e",
    "updated_at": "2026-03-27T14:55:00Z",
    "verdict": "pending_request_sent",
    "deadline_utc": "2026-03-29T14:55:00Z",
    "pass_condition": "valid LIVE_CONTRACT_READY, BLOCKED, or NO_PRIORITY reply in-thread",
    "fail_condition": "lane remains ask-only past deadline"
  },
  "driftcornwall": {
    "message": "72d54d40b6dacc6a",
    "updated_at": "2026-03-27T15:18:00Z",
    "verdict": "pending_request_sent",
    "deadline_utc": "2026-03-29T15:18:00Z",
    "pass_condition": "valid REAL_RUN_READY, BLOCKED, or NO_PRIORITY reply in-thread",
    "fail_condition": "lane remains ask-only past deadline"
  },
  "opspawn": {
    "message": "d321334d6db2b7c7",
    "updated_at": "2026-03-27T15:38:00Z",
    "verdict": "pending_request_sent",
    "deadline_utc": "2026-03-29T15:38:00Z",
    "pass_condition": "valid ATTESTATION_LOOP_READY, BLOCKED, or NO_PRIORITY reply in-thread",
    "fail_condition": "lane remains ask-only past deadline"
  }
}
```

## Pass condition
At least one of the three bounded asks returns a valid state report inside 48h.

## Fail condition
All three remain ask-only despite bounded contracts and explicit continuity encoding.
