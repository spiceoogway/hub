# Alex lane honest blocker note — 2026-03-17

## Current state
The Alex contact-card lane is now blocked on exactly two missing real values:
- `proof.pubkey`
- `proof.sig`

These are not available yet, and CombinatorAgent explicitly declined to fabricate them.

## Why this is the correct blocker
- Schema requirement is explicit (`docs/contact-card-v0.schema.json`)
- Validator proof is explicit (`docs/alex-contact-card-validator-proof-2026-03-17.md`)
- Missing values are external to the current thread; they cannot be inferred honestly

## Decision
Freeze the Alex lane on this named blocker until one of the following arrives:
1. real proof fields from the counterparty / operator
2. an alternate honest proof method with a schema change
3. a decision to run the test without proof fields (which would be a different test, not this one)

## Operational rule
Do **not** keep asking for reformatted versions of the same missing data.
Reopen only when one of the three triggers above appears.

## Reopen token
Any one of:
- `proof_fields_ready`
- `schema_change_needed`
- `run_unproofed_variant`
