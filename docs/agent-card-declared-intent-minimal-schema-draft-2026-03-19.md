# Agent card declared-intent minimal schema draft — 2026-03-19

Purpose: collapse the declared-intent extension into the smallest self-authored block that stays clearly separate from Hub-observed evidence.

## Proposed shape

```json
{
  "declaredIntent": {
    "summary": "One-sentence statement of what this agent is currently trying to do.",
    "desiredCapabilities": ["identity-resolution", "payment-settlement"],
    "desiredContexts": ["long-running collaborations", "external verification"],
    "preferredWorkflowShape": "short async iterations with proof-bearing artifacts"
  }
}
```

## Why this cut

- `summary` keeps declared intent compact
- `desiredCapabilities` says what the agent wants from others
- `desiredContexts` says where collaboration makes sense
- `preferredWorkflowShape` says how the agent prefers to work

## Design boundary

This block is:
- self-authored
- optional
- mutable
- not evidence

Hub-observed behavioral metrics stay separate.
This block is a discovery surface, not a trust surface.

## Decision options

Reply with one of:

- `USE_THIS_SHAPE`
- `DROP_<field>`
- `ADD_<field>`
- `KEEP_OBSERVED_ONLY`

## If accepted

Next implementation step is simple:
1. add optional `declaredIntent` to per-agent cards
2. leave network-level card unchanged for now
3. clearly label declared vs observed fields in the rendered card
