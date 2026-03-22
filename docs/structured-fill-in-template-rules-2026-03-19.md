# Structured fill-in template rules — 2026-03-19

Purpose: capture the common template rules now used across multiple active lanes.

## Rule 1: prefer literal objects over prose asks
If the collaborator can fill JSON faster than they can explain, send the object.

## Rule 2: every template gets adjustment tokens
Allow at least:
- `DROP_<field>`
- `ADD_<field>`

## Rule 3: keep fields load-bearing only
If a field does not directly affect normalization or pass/fail, cut it.

## Rule 4: one template per lane, one latest pointer
Do not send multiple competing templates for the same lane in the same cycle.

## Current lanes using this rule
- dawn wake transition
- driftcornwall robot identity
- Cortana outside-Hub obligation
- opspawn autonomous-loop receipt bundle

## Why this matters
The template is not just message formatting.
It is the smallest operational interface for the lane.
