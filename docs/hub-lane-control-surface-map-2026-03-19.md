# Hub lane control surface map — 2026-03-19

Purpose: one compact map of how the day’s lane-management artifacts fit together.

## 1. Diagnose the lane
Use the **classification reducer** to decide what kind of missingness exists.
Reference: `hub/docs/missingness-reducer-split-note-2026-03-19.md`

## 2. Choose the smallest closing object
Use the **artifact / stall-handling reducer** to pick the smallest object that can close the missingness.
Reference: `hub/docs/friction-cutting-artifact-pattern-2026-03-19.md`

## 3. Constrain the reply surface
Use the smallest token family that maps directly to next actions.
Reference: `hub/docs/reply-token-surface-pattern-2026-03-19.md`

## 4. Reuse template rules when the lane needs structure
Reference: `hub/docs/structured-fill-in-template-rules-2026-03-19.md`

## Summary
- first diagnose
- then shrink the object
- then shrink the reply surface
- then verify the live state
