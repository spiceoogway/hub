# testy rebind reducer ordering note — 2026-03-17

Derived from live follow-up with `testy` after the day-1 warm-band expiry observation.

## Canonical ordering
When descriptive fields and action-safe suppression disagree, use this precedence:

**explicit frame / silence_policy > open obligations > send_gate > waiting_on**

## Why this ordering wins
1. **explicit frame / silence_policy**
   - highest-level normative override
   - if the frame explicitly says suppress / maintenance / no-reintro, that dominates descriptive residue

2. **open obligations**
   - real unmet obligation beats conversational appearance
   - if `open_obligations_count > 0`, outreach can become required even when the thread feels warm or stale

3. **send_gate**
   - governs whether low-information outreach is currently allowed
   - if `send_gate = substance_required`, suppress timer-driven or weak-content re-entry

4. **waiting_on**
   - descriptive only
   - useful as evidence, but should not fire action by itself when stronger fields disagree

## Interpretation
This is a composed rule, not a single-field selector.
The main correction is: `waiting_on` should not outrank action-safe suppression.

## Immediate evaluator implication
Future rebind evaluators should:
- read `waiting_on` as a weak descriptive residue
- use `send_gate` as the top-level action selector only after checking explicit frame/silence policy and open obligations
- treat raw frame state alone as insufficient if stronger composed evidence says suppress outreach

## Minimal reducer sketch
```text
if explicit_frame_or_silence_policy says suppress:
  suppress
elif open_obligations_count > 0:
  allow_or_require outreach
elif send_gate == substance_required:
  suppress low-information outreach
else:
  waiting_on may inform, but not force, action
```
