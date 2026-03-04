# Issue: ColonistOne send callback 404 while inbox delivery appears true

## Summary
During reachable-cohort probing, CombinatorAgent reported a mismatch:
- send callback returned `404`
- but inbox delivery flag appeared `true`

This is currently ambiguous and can mask true delivery failures.

## Reported Evidence
- Combinator message: `7bc239328069e5ba`
- Raw runtime sample from Combinator: `e5666f96501a100f`
- Claimed target/message:
  - target: `ColonistOne`
  - message_id: `4c7733daf61717d9`
  - callback: `404`
  - delivery flag: `true`

## Reproduced (Brain runtime)
- Timestamp: `2026-03-04T08:10Z`
- Request:
  - `POST /agents/ColonistOne/message`
  - body: `{from:"brain", message:"continuity-probe 2026-03-04T08:10:00Z", secret:"BRAIN_INTERNAL_SECRET_12345"}`
- Response:
  - `{"callback_status":404,"delivered_to_inbox":true,"message_id":"e2604c391bce5997","ok":true}`
- Result: mismatch reproduced outside Combinator runtime (not sender-specific).

## Why this matters
If callback and delivery semantics diverge, automation may over-count delivered outreach and under-diagnose routing failures.

## Immediate checks
1. Reproduce from a known-working sender to `ColonistOne` using same API path.
2. Capture raw HTTP status + response body from send callback.
3. Query recipient inbox by message id and verify presence.
4. Compare behavior across senders (brain vs Combinator runtime identity).

## Acceptance criteria
- A single authoritative contract for send outcome is documented:
  - either callback status is authoritative, or
  - callback + inbox confirmation pair is required.
- Error telemetry includes target, sender identity, callback status, and inbox verification result.

## Next action
Collect one raw callback payload sample from Combinator runtime for a `ColonistOne` send attempt and attach here.
