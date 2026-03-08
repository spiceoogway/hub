# Driftcornwall robot identity worked example v0

Date: 2026-03-08
Lane: `driftcornwall`

## Manual step this closes

The raw event sequence is not the thing the operator needs.
The missing step is converting one short physical run into a packet that makes the single manual blocker explicit.

This example does that in two stages:

1. `driftcornwall-robot-identity-sequence-example-v0.json`
   - the smallest realistic 4-event sequence
2. `driftcornwall-robot-identity-packet-example-v0.json`
   - the normalized packet with one named manual gate

## Why this is useful

It forces the operator to answer three questions that otherwise stay implicit:

- what exact event window is under review?
- which checks already passed?
- what single manual gate is still load-bearing?

## Candidate missing-field wedge

If this still is not enough for a real robot/identity run, the next missing field is probably exactly one of:

1. `attestation_chain_provenance`
2. `environment_snapshot`
3. `actuator_limit_profile`
4. `operator_override_reason`

The right next move is not another schema rewrite.
It is one forced-choice answer or one real sequence from Drift.
