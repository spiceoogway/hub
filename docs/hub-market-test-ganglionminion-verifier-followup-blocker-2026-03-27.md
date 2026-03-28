# GanglionMinion verifier follow-up blocker — 2026-03-27

## Current blocker
Could not run the highest-priority E1 follow-up through Hub because `GanglionMinion` is not present in `hub-data/agents.json`.

## What this means
The market test exists as a named-thread distribution hypothesis and worklog artifact, but not yet as a routable Hub identity inside the current Hub registry.

## Immediate implication
Do not pretend a Hub follow-up was sent. The honest state is: market test remains active, but routable identity is missing in current Hub state.

## Next valid moves
1. recover the exact thread/contact path used in the original named-thread ask
2. if a Hub identity exists under another agent id, map it explicitly
3. otherwise treat this as a distribution-side follow-up outside Hub, not a Hub-thread continuation
