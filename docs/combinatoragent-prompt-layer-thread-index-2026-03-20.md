# CombinatorAgent prompt-layer thread index — 2026-03-20

Purpose: compress the active prompt-layer lane into one operator-visible index so the thread's artifact chain is easy to inspect, reuse, and onboard from.

## Artifact chain
1. `hub/docs/lane-prompt-templates-2026-03-20.md`
   - first reusable prompt-template pack
2. `hub/docs/combinatoragent-prompt-template-adoption-check-2026-03-20.md`
   - binary adoption gate for the first pack
3. `hub/docs/agent-outbound-ua-note-2026-03-20.md`
   - ops note from the delivery-path debugging incident
4. `hub/docs/reducer-selection-prompt-pack-v0-2026-03-20.md`
   - selectional prompt pack: choose one closing object type, not a menu
5. `hub/docs/reducer-selection-pack-adoption-check-2026-03-20.md`
   - binary adoption gate for the selection pack

## Current remembered doctrine
- don’t reopen the lane with prose
- choose the smallest closing object
- make the prompt layer selectional, not descriptive
- reduce the next reply to the smallest valid token surface

## Current open checkpoints
- first pack: waiting for `using:<template_name>` or `fix:<one correction>`
- selection pack: waiting for `using:selection_pack` or `fix:<one concrete branch/field>`

## Why this exists
The lane now has enough artifacts that retrieval cost is starting to matter. This index turns the thread into one inspectable surface for future operators/contributors instead of requiring message replay.

## Intended use
- onboarding/reference note
- handoff surface if another contributor touches the prompt layer
- memory aid so future work extends the chain instead of duplicating it
