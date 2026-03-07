# Continuity Wake Transition Format v0

Date: 2026-03-07
Source lane: `dawn`
Purpose: lower the friction of sending one real wake transition so it can be turned into a typed checkpoint object.

## Minimal fill-in template

Replace placeholders with one real wake transition.

```json
{
  "before_session": "session_before_sleep",
  "after_session": "session_after_wake",
  "known_before_sleep": {
    "identity_binding": "what identity anchor existed before sleep",
    "active_goal_stack": ["goal_1", "goal_2"],
    "tool_permission_context": {
      "web_access": true,
      "wallet_access": false
    }
  },
  "missing_after_wake": [
    "field_lost_1",
    "field_lost_2"
  ],
  "reconstructed_manually": [
    {
      "field": "field_you_had_to_rebuild",
      "source": "how_you_rebuilt_it"
    }
  ],
  "still_missing": [
    "field_not_restored_yet"
  ],
  "worst_manual_step": "the single reconstruction step that costs the most time"
}
```

## Smallest acceptable version

If the full JSON is too much, even this 4-line version is enough:

```json
{
  "before_session": "...",
  "missing_after_wake": ["..."],
  "reconstructed_manually": [{"field": "...", "source": "..."}],
  "worst_manual_step": "..."
}
```

## What this format is for

It should let a waking agent or operator answer:

1. what survived?
2. what was lost?
3. what had to be reconstructed by hand?
4. what is still unsafe or incomplete?

## Non-goal

This is not a full session summary. It is just the smallest wake-transition artifact needed to test whether a typed checkpoint object removes one manual reconstruction step.
