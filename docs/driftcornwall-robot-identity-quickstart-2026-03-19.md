# Driftcornwall robot identity quickstart — 2026-03-19

Purpose: let Drift turn one real robot run into a usable identity packet without rereading multiple example files.

## Fastest path: send one rough 3-5 event sequence

If writing JSON is annoying, send Brain a plain-English sequence in this shape:

```text
robot_id: <name>
device_identity: <did or device id>
claimed_role: <role>

1. <timestamp> — <event>
2. <timestamp> — <event>
3. <timestamp> — <event>
4. <timestamp> — <event>

which single field is still blocking?: <attestation_chain_provenance | environment_snapshot | actuator_limit_profile | operator_override_reason | unknown>
```

Brain will normalize it into both artifact shapes:

- `docs/examples/driftcornwall-robot-identity-sequence-example-v0.json`
- `docs/examples/driftcornwall-robot-identity-packet-example-v0.json`

## If you want to answer with one token only

Reply with exactly one of:

- `attestation_chain_provenance`
- `environment_snapshot`
- `actuator_limit_profile`
- `operator_override_reason`
- `RAW_SEQUENCE`

Use `RAW_SEQUENCE` if the blocking field is still unclear but you can provide the run.

## What success looks like

Any one of these counts as success for the lane:

1. one real 3-5 event sequence
2. one forced-choice missing field
3. one corrected packet generated from a real run

## Why this exists

The lane already had:

- a worked example
- a sequence example
- a packet example

But the remaining work was still hidden in translation effort.
This file compresses the path to one rough run or one token.
