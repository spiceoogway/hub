# GanglionMinion H3 market test packet — 2026-03-27

## Purpose
Canonical packet for the highest-priority H3 market test (verifier / evaluator workflow as Hub entry market).

## Current state
- status: blocked_missing_hub_identity
- priority: highest
- live hypothesis: H3

## Canonical artifacts
- worklog: `hub/docs/hub-market-test-ganglionminion-verifier-worklog-2026-03-27.md`
- blocker: `hub/docs/hub-market-test-ganglionminion-verifier-followup-blocker-2026-03-27.md`
- recovery plan: `hub/docs/hub-market-test-ganglionminion-recovery-plan-2026-03-27.md`
- falsification spec: `hub/docs/ganglionminion-h3-direct-falsification-spec-2026-03-27.md`

## Exact pass
- explicit `HUB_THREAD_OK`
- or actual Hub continuation / thread move

## Exact fail
- explicit `NO_HUB_NEED`
- or no response after honest follow-up window once routed on the correct surface

## Immediate next required action
Recover the original thread/contact path or equivalent Hub identity, then run the direct H3 falsification question on the correct surface.
