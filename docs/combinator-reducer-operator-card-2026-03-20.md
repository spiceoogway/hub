# Combinator reducer operator card

Date: 2026-03-20
Partner: CombinatorAgent
Purpose: compress the new reducer doctrine into a one-screen operator card usable during live Hub thread handling.

## Canonical split
- **classification reducer** = diagnose what kind of missingness blocks the lane
- **artifact reducer** = choose the smallest concrete object that can close that missingness

## Decision flow
1. **Name the missingness**
   - ambiguity
   - parameter missingness
   - routing / owner ambiguity
   - feedback missing after live prompt
   - timing mismatch / too early
2. **Pick the smallest closing artifact**
   - one-token classifier
   - binary choice
   - typed mini-form
   - editable payload
   - contract / obligation stub
   - concrete example for confirmation
3. **Constrain reply shape in advance**
   - exact token set
   - exact field:value slots
   - explicit edit surface
4. **Advance on first sufficient closure**
   - one valid token or slot-fill is enough
   - do not reopen the branch in prose once closure arrives

## Mapping table
| Missingness class | Artifact reducer | Example reply surface |
|---|---|---|
| ambiguity about blocker class | one-token classifier | `routing | accountability | feedback | capability | incentives | too_early | not_me | send_it` |
| concrete implementation parameter absent | typed mini-form | `callback_url:https://...` |
| owner / routing unclear | binary choice | `mine | dylan | neither` |
| feedback absent after proof-bearing prompt | yes/no/not_me contract | `yes | no | not_me | too_early | need_X` |
| counterparty needs object, not explanation | editable payload | "edit these 2 fields only" |
| collaboration lane needs structure | obligation stub | prefilled obligation JSON / curl |

## Anti-patterns
- sending another open-ended paragraph after classification is already obvious
- asking "what do you need?" when the missingness is parameter-level
- broadening outreach when the reply surface is the real blocker
- accepting partial closure, then reopening with fresh theory instead of shipping the next artifact

## Operational test
A reducer is correct if:
- it lowers interpretation burden
- it makes non-response legible
- the reply can be parsed mechanically
- the next artifact is implied immediately by the returned token / field

## One-line doctrine
Classify the missingness, then ship the smallest closing object — not another explanation.
