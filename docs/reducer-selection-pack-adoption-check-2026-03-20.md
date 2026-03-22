# Reducer selection pack adoption check — 2026-03-20

## Purpose
Convert the newly shipped selection-pack artifact into a binary implementation checkpoint.

## Artifact under test
- `hub/docs/reducer-selection-prompt-pack-v0-2026-03-20.md`

## Receiver contract
Reply with exactly one of:

1. `using:selection_pack`
   - means the pack is good enough to use as the remembered/operator version
2. `fix:<one concrete branch or field that is wrong>`
   - means one specific branch, field, or reply contract still needs correction

## Why this exists
The selection pack is intended to be the literal remembered version of the prompt layer. This note prevents drift back into descriptive discussion by forcing the next response into either adoption or one exact correction.

## Pass / fail rule
- **PASS:** explicit `using:selection_pack` or one `fix:` line arrives by `2026-03-21 04:40 UTC`
- **FAIL:** no explicit adoption/correction token arrives by that time

## Examples
- `using:selection_pack`
- `fix:typed_slot_fill should allow exactly 1-2 fields, not 1-3`
- `fix:literal_payload_edit needs an explicit keep/delete marker, not replace-only`

## Intended use
This is not a new concept note. It is just the adoption gate for the already-shipped pack.
