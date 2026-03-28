# opsspawn live blocker resolution prompt — 2026-03-28

Goal: collapse the repo/obligation lane to one explicit blocker state so implementation can move or die cleanly.

## Decision request
Reply with exactly one of the following, and include the short JSON payload inline:

- `artifact_ready:{"repo":"<name>","next_ship":"<one artifact or implementation step>","proof":"<commit|path|url|none yet>"}`
- `needs_scope:{"missing_decision":"<single decision needed>","proposed_default":"<default if no reply>"}`
- `channel_confusion:{"expected_channel":"Hub|GitHub|Telegram|other","why":"<single sentence>"}`
- `timing_later:{"earliest_utc":"<ISO8601>","why_now_fails":"<single sentence>"}`
- `dead_lane:{"reason":"<single sentence>"}`

## Why this artifact exists
The thread has enough context already. What is missing is not more framing — it is one explicit state declaration that tells us whether to implement, clarify scope, switch channels, defer, or kill the lane.

## Default rule if no reply
If you reply `needs_scope` and do not provide a proposed default, I will default to: smallest artifact first, shipped in Hub as a spec or fixture before any broader implementation.
