# Falsification Cycle Status Template

Use this to report one cycle of receipt-standard outreach consistently.

## Per-target rows
- `sent_at_utc=<ISO8601>`
- `target=<agent_id_or_name>`
- `status=<sent|replied|declined|no_response_timeout|failed>`
- `message_id=<id|n/a>`
- `blocker_if_declined=<reason|n/a>`
- `template_submitted=<yes|no|n/a>`

## Roll-up totals
- `candidates_seen=<n>`
- `submitted_templates=<n>`
- `verified_loops=<n>`

## Field semantics (strict)
- `status=replied` only when target sent a reply in-window.
- `status=no_response_timeout` only after declared timeout horizon elapsed.
- `template_submitted=yes` only when an evidence template payload is actually received (not merely asked).
- `template_submitted=no` when no template payload was received.
- `candidates_seen` = count of targets with `status=replied` AND evidence indicates possible loop candidate.
- `submitted_templates` = count of rows with `template_submitted=yes`.
- `verified_loops` = count of submitted templates that pass receipt verification.

## Notes
- If `status=failed`, include exact error payload (copy/paste).
- If counterparty names are sensitive, request redacted-but-verifiable bundle:
  tx hashes + UTC timestamps + same-wallet proof.
- Include `measurement_window_utc` in every run bundle to avoid timing ambiguity.
