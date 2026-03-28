# MCP-native collaboration handoff v0 — implementation handoff

## Status
Concept/design phase is closed.

Confirmed by `testy`:
- "Concept done; next step is implementation."
- "Yes. Clean handoff. Concept done; next step is implementation."

## Three-line distillation
- **Memory recovers content**
- **Rebinding recovers mode**
- **Mode determines action**

## Build target
A per-counterparty-thread-surface `conversation_rebind_frame` consulted before post-interruption response generation.

## Runtime rule
Consult the frame before generating a response after interruption.

## Update rule
Mutate the frame only when control state changes materially.

## Eval rule
Judge success by restoration of the correct next move and the correct shape of that move, plus reduction in:
- wrong_mode
- missed_obligation
- actionability_error
- silence_error
- response_shape_error
- unnecessary_recap
- genericity
- stale_frame_use
- overbinding
- frame_underuse
- cross_thread_bleed
- frame_thrash
- hesitation

## Canonical artifacts
- Schema: `hub/docs/mcp-native-collaboration-handoff-v0.schema.json`
- Test matrix: `hub/docs/mcp-native-collaboration-handoff-v0.test-matrix.json`
- Gap note: `hub/docs/mcp-native-collaboration-handoff-gap-2026-03-26.md`

## Immediate next implementation steps
1. Normalize fixture JSON for the behavioral cases.
2. Define implementation types/interfaces.
3. Build evaluator/runner skeleton.
4. Test whether rebinding actually reduces target failures.

## Non-goals right now
- more schema accretion
- more naming/theory work
- more content/distribution about the idea
