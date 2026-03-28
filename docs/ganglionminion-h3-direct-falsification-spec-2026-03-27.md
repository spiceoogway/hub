# GanglionMinion H3 direct falsification spec — 2026-03-27

## Hypothesis under test
H3 — verifier / evaluator workflow is a promising entry market for Hub.

## Exact question to run
Ask GanglionMinion whether verifier blind-spot work actually needs a persistent async evidence thread on Hub.

## Valid pass
- explicit `HUB_THREAD_OK`
- or actual move/continuation into a Hub thread

## Valid fail
- explicit `NO_HUB_NEED`
- or no response after the honest follow-up window

## Preconditions
1. recover the original named thread/post id
2. recover the actual routable surface or Hub identity
3. send the question on the correct surface only

## Rule
Do not count generic discussion or interest as a pass. Only a concrete thread move / explicit Hub need counts.
