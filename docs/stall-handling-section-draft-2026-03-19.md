# Stall handling section draft — 2026-03-19

When a lane stalls, assume the first hidden blocker is translation work.
Before sending another follow-up, ask:
- am I requiring them to synthesize multiple artifacts?
- am I requiring them to infer field names?
- am I requiring them to explain in prose when a structured reply would do?

If yes, stop.
Ship a smaller artifact.

## Preferred move order
1. reduce to one canonical doc
2. reduce to one minimum contract
3. reduce to one literal fill-in object or payload example
4. reduce reply space to explicit tokens

## Why this matters
A stalled lane is usually not a motivation diagnosis first.
It is often an interface diagnosis.
If the other agent cannot answer without translating your structure, the lane still contains hidden operator work.
