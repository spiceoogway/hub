# collaboration-state fidelity evaluator rubric v1 — 2026-03-26

Derived from:
- `hub/docs/conversation-rebind-collaboration-state-fidelity-fixture-table-v1-2026-03-26.md`
- `hub/docs/examples/conversation-rebind-collaboration-state-fidelity-fixtures-v1-2026-03-26.json`

This file is interpretive.
It is **not** the canonical case definition.
Canonical definitions live in the markdown table and its isomorphic JSON projection.

## Umbrella property
**collaboration-state fidelity**

## Evaluator sentence
**Rebind quality is the fidelity with which a system reconstructs and resumes the live collaboration state.**

## Canonical pass bar
A successful rebind:
- restores the right interaction mode
- preserves still-live obligations
- infers the correct next move type
- advances the work rather than merely extending the conversation

## Axis meanings

### `mode_fidelity`
Does the system recover the correct local interaction frame for the resumed collaboration?
Examples:
- right thread / surface
- right relationship stance
- right waiting vs active state
- right invalidate / trust / ignore behavior

### `obligation_continuity`
Does the system preserve prior owed work that remains live?
Examples:
- unresolved artifacts still recognized as owed
- in-flight commitments not silently dropped
- older obligations briefly surfaced when current subtopic motion might hide them

### `shipment_inference`
Does the system infer when the collaboration has crossed from deliberation into execution?
Examples:
- brief affirming turn means ship now
- commentary is no longer the right move type
- analysis should end because work-state already implies delivery

### `work_advancement_fidelity`
Does the system make the move that correctly advances the shared work?
This is about operational fit, not style.
Examples:
- recovering the next move
- choosing the correct response shape for the work state
- resuming from obligation state rather than merely sounding continuous

## Secondary axis rule
Use `secondary_axis` only when it captures a **distinct residual failure** that can remain after success on the primary axis.
Otherwise use `none`.

Test:
> If the case were solved perfectly on its primary axis, could it still fail on the secondary axis in a distinct way?

If no, the secondary axis should be `none`.

## Fixture-family split
The suite contains two broad families:

### 1. State reconstruction failures
These test whether the system reconstructs the right local collaboration frame.
Mostly single-axis.
Typical cases:
- reroute
- irrelevant frame intrusion
- cross-surface smearing
- waiting-state corruption
- wrong interaction mode

### 2. Post-reconstruction advancement failures
These test whether the system advances correctly once enough state has been reconstructed.
More likely to be dual-axis.
Typical cases:
- obligation carry-forward across pause
- response shape vs work-state fit
- subtopic continuity with obligation amnesia
- missed shipment transition

## Evaluation discipline
When grading a case:
1. Judge the behavioral move, not the explanatory prose.
2. Prefer operational equivalence over wording match.
3. Do not reward stylistic coherence if the work-state move is wrong.
4. Do not penalize terse correct action because it is terse.
5. Distinguish “sounded continuous” from “resumed the work correctly.”

## Canonical failure interpretation

### Single-axis cases
Interpret these as failures centered on one diagnostic surface.
Do not inflate them into dual-axis failures unless the residual overlap is independently visible.

### Dual-axis cases
Interpret these as cases where one surface can be recovered while another still fails.
Examples:
- obligation preserved in principle but resumed in the wrong work shape
- response shape broadly plausible but wrong about whether shipment is now warranted

## Migration rule
If legacy fixture assets require extra explanatory notes, store those notes in the evaluator layer or migration metadata.
Do **not** add theory prose back into the canonical fixture definitions.
