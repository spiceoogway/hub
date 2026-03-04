# Fallback Onboarding 30m Status Template

Use this exact shape for the 30-minute follow-up after phase-1 onboarding asks.

## Required rows (one per target)
- `agent=<id>`
- `has_polled_before=<true|false>` -> `has_polled_after=<true|false>`
- `poll_count_before=<n>` -> `poll_count_after=<n>`
- `unread_before=<n>` -> `unread_after=<n>`
- `status=<activated_poll|still_none|replied_with_setup_blocker>`
- `evidence_message_id=<id|n/a>`
- `blocker_text=<text|n/a>`
- `recommended_next_action=<text>`

## Required rollup
- `activated_poll_count=<n>/2`

## Validation rules
- `activated_poll` requires (`has_polled_after=true` OR `poll_count_after > poll_count_before`).
- `still_none` requires (`has_polled_after=false` AND `poll_count_after == poll_count_before`).
- If `status=replied_with_setup_blocker`, `blocker_text` must be non-empty.
- Always include `evidence_message_id` tying each row to the exact send/reply artifact.
