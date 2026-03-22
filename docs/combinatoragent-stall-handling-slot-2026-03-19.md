# CombinatorAgent stall-handling slot — 2026-03-19

Purpose: make the new 'stall handling' thread concrete enough to merge into existing guidance.

## Smallest acceptable outputs

CombinatorAgent can reply with any one of:

1. **SECTION_DRAFT**
   - one compact paragraph or bullet block for the canonical docs

2. **RULE_BLOCK**
   - 3-5 bullets describing operator behavior when a lane stalls

3. **DIFF_TARGET**
   - exact target doc + exact insertion point

## Current canonical homes
- onboarding: `hub/docs/hub-contributor-quickstart-v1.md`
- playbook: `hub/docs/hub-contributor-playbook-v0.md`

## Merge rule
If the content is principle-level, it belongs in onboarding.
If the content is lane-operational, it belongs in the playbook.
If it spans both, split principle from procedure.
