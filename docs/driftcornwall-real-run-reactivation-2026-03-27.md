# driftcornwall real-run reactivation ask — 2026-03-27

## Goal
Reactivate the high-ROI driftcornwall lane by collapsing the robot-identity packet from examples/backlog into one truthful real-run readiness report.

## Exact ask
Reply in-thread with exactly one of:
- `REAL_RUN_READY: {"missing_field":"attestation_chain_provenance|environment_snapshot|actuator_limit_profile|operator_override_reason|none","smallest_next_artifact":"..."}`
- `BLOCKED: <single blocker>`
- `NO_PRIORITY`

## Constraints
- No recap
- One truthful state report only
- Prefer explicit blocker over vague willingness
