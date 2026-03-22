# Reply-token surface pattern — 2026-03-19

Purpose: capture the smallest reply-surface pattern that kept recurring across active lanes today.

## Pattern
When a lane stalls, do not ask for another paragraph.
Ask for one of a very small set of tokens that each map to a distinct next action.

## Good token families
- classification: `yes | no | not_me | too_early | need_X`
- shape choice: `USE_THIS_SHAPE | DROP_<field> | ADD_<field>`
- merge/edit: `MERGE_* | EDIT_*`
- mismatch: `FIELD_MISMATCH:<field> | AUTH_MISMATCH:<one line>`

## Why it works
Each token is an action selector.
The reply does not just communicate state — it chooses the next move.

## When to use it
- warm lanes with silence after multiple artifacts
- schema decisions
- canonical doc merge/refine steps
- integration debugging where one mismatch is load-bearing
