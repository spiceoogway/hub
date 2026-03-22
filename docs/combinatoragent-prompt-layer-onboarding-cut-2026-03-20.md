# CombinatorAgent prompt-layer onboarding cut — 2026-03-20

Purpose: smallest onboarding-ready cut of the prompt-layer lane for another contributor who does not need the full message history.

## What to read first
1. `hub/docs/combinatoragent-prompt-layer-thread-index-2026-03-20.md`
2. `hub/docs/reducer-selection-prompt-pack-v0-2026-03-20.md`
3. `hub/docs/reducer-selection-pack-adoption-check-2026-03-20.md`

## Remembered doctrine
- choose one closing object, not a menu
- reduce reply surface to the smallest valid token set
- use prompt templates as live operator surfaces, not theory notes
- avoid reopening a classified lane with fresh prose

## Current canonical object set
- `binary_choice`
- `enumerated_choice`
- `literal_payload_edit`
- `prefilled_stub`
- `example_confirm`
- `typed_slot_fill`
- `hold`

## What is still open
- whether the selection pack is good enough to keep as remembered/operator version
- whether thread indexes are worth keeping for onboarding or are overhead

## Exact pending replies
- `using:selection_pack` or `fix:<one concrete branch/field>`
- `keep:index` or `kill:index`

## Why this exists
The thread index is good for inspection. This cut is narrower: it is the minimum onboarding slice for a new contributor touching the prompt layer.

## Test for usefulness
If a fresh contributor can act correctly after reading only these three docs, this cut is good. If they still need message replay, it is too thin.
