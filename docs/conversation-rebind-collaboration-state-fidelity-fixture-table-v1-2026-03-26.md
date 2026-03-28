# collaboration-state fidelity fixture table v1 — 2026-03-26

Derived from live discussion with `testy`.

- **Umbrella property:** collaboration-state fidelity
- **Evaluator sentence:** rebind quality is the fidelity with which a system reconstructs and resumes the live collaboration state

## Axis vocabulary
- `mode_fidelity`
- `obligation_continuity`
- `shipment_inference`
- `work_advancement_fidelity`

## Canonical pass bar
A successful rebind:
- restores the right interaction mode
- preserves still-live obligations
- infers the correct next move type
- advances the work rather than merely extending the conversation

## Fixture table

| id | scenario | pass | fail | primary_axis | secondary_axis | failure_label |
| --- | -------- | ---- | ---- | ------------ | -------------- | ------------- |
| 1 | straightforward_frame_use_in_stable_thread | Recovers the obvious next move in the same live thread and resumes work without requiring narrative replay. | Fails to recover the live next move even though the thread, counterparty, and work lane are stable. | `work_advancement_fidelity` | `none` | `missed_stable_next_move` |
| 2 | obligation_continuity_across_pause | Preserves what is still owed or in flight across a pause and resumes from that obligation state. | Resumes the thread while omitting still-live owed work or treating it as resolved without basis. | `obligation_continuity` | `work_advancement_fidelity` | `obligation_amnesia_after_pause` |
| 3 | weak_invalidation_but_still_locally_usable | Detects mild staleness, updates cautiously, and still uses the frame where it remains locally safe. | Either over-trusts a mildly stale frame as fully current or over-invalidates a still-usable frame and loses usable local continuity. | `mode_fidelity` | `none` | `weak_invalidation_miscalibration` |
| 4 | strong_invalidation_of_unsafe_frame | Recognizes that the prior frame is unsafe to act from and refuses confident continuation from it. | Continues acting from a frame whose purpose, assumptions, or state have changed enough to make it unsafe. | `mode_fidelity` | `none` | `unsafe_frame_reuse` |
| 5 | silence_waiting_state_preservation | Correctly represents a waiting state where the right move is no action yet, without fabricating progress or rewriting the collaboration state. | Invents action, escalates prematurely, or treats silence as a cue to collapse the waiting state into a different work state. | `mode_fidelity` | `none` | `waiting_state_corruption` |
| 6 | reroute_to_different_thread_or_surface | Detects that the active work moved elsewhere and stops using the old local frame as if it were still governing the interaction. | Reuses the old frame after the work has clearly shifted threads or surfaces, causing routing or context smearing. | `mode_fidelity` | `none` | `missed_reroute_after_context_shift` |
| 7 | valid_frame_irrelevant_to_current_task | Leaves a valid historical frame unloaded because it is irrelevant to the present task. | Loads and applies a valid but irrelevant frame, contaminating the current task with the wrong local context. | `mode_fidelity` | `none` | `irrelevant_frame_intrusion` |
| 8 | cross_surface_divergence_without_smearing | Keeps separate local frames for the same counterparty across different surfaces and uses the one that matches the current work surface. | Collapses distinct surface-local contexts into one blended frame and acts as if they were the same interaction state. | `mode_fidelity` | `none` | `cross_surface_frame_smearing` |
| 9 | interaction_mode_recovery_after_rebind | Restores the correct relationship stance for the resumed thread, such as spec iteration vs bug triage vs negotiation. | Sounds continuous but adopts the wrong conversational or decision posture for the actual resumed collaboration mode. | `mode_fidelity` | `none` | `wrong_interaction_mode_after_rebind` |
| 10 | response_shape_matches_work_state | Produces the right kind of move for the work state, not just plausible content, brevity, or tone. | Gives a stylistically plausible response whose shape is wrong for the live collaboration state. | `work_advancement_fidelity` | `shipment_inference` | `response_shape_without_work_state_fit` |
| 11 | live_subtopic_response_with_prior_obligation_carry_forward | Addresses the current subtopic, briefly surfaces the still-open prior obligation, and either ships it if cheap or explicitly marks it as still owed. | Responds coherently to the live subtopic while silently dropping still-active owed work from the earlier branch. | `obligation_continuity` | `work_advancement_fidelity` | `subtopic_continuity_with_obligation_amnesia` |
| 12 | commentary_vs_shipment_transition | Recognizes that the brief affirming turn closes deliberation and that the next correct move is artifact delivery or shipment rather than more analysis. | Continues analytical or agreeable commentary even though prior context already established that the right next move is to ship. | `shipment_inference` | `work_advancement_fidelity` | `missed_shipment_transition` |

## Notes
These fixtures are intentionally aimed at failures where the system can appear locally coherent while failing operationally.

They distinguish:
- conversational continuation from collaboration resumption
- thread coherence from obligation carry-forward
- stylistic fit from correct work-state transition

The key invariant they enforce is:

> preserving thread feel is not enough; the system must preserve and advance the work.
