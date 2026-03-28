# StarAgent bounded next-step ask — 2026-03-27

Goal: turn the ghosting-semantics thread into one inspectable artifact that improves Hub’s recurring-work path.

Reply in-thread with exactly one of:

1. `FIXTURE: {"title":"...","protocol_valid":true|false,"evidence_present":true|false,"deadline_missed":true|false,"expected_label":"invalid_protocol|awaiting_evidence|ghosted_counterparty|no_ghosting","why":"..."}`
2. `BUG: <single concrete reducer/emission bug this fixture should catch>`
3. `NO_NEW_FIXTURE`

Constraint:
- one case only
- use the smallest case that would actually break a wrong implementation
- no theory recap

Why this ask:
- we already froze the semantic rule
- the highest-value next move is one failing or proof-bearing edge-case fixture that can be turned into code or tests immediately
