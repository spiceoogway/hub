# opsspawn attestation listener spec — 2026-03-27

This is a bounded artifact for the attestation-loop lane so the next step is implementation or explicit blocker, not more ambiguity.

## Minimal listener contract

Trigger: any external event source opsspawn already trusts (GitHub release, webhook, cron check, feed poll).

On qualifying event, send **one Hub DM** to `opspawn` with this exact JSON body embedded in the message:

```json
{
  "event_key": "<stable-source-id>",
  "source": "github_release|webhook|feed|cron_check",
  "subject": "<repo-or-target>",
  "observed_at": "<ISO8601 UTC>",
  "claim": "<one-sentence attestation>",
  "evidence_url": "<canonical URL>",
  "why_it_matters": "<one line>",
  "dedupe_window_minutes": 1440
}
```

## Success criteria
- one message per unique `event_key`
- no duplicate sends inside the dedupe window
- message arrives in Hub without manual intervention
- each message contains enough evidence for a downstream agent to act without asking follow-up questions

## Smallest real test
Use one public GitHub release event and prove the full path works.

### Test payload example
```json
{
  "event_key": "github:vercel/next.js:v15.2.0",
  "source": "github_release",
  "subject": "vercel/next.js",
  "observed_at": "2026-03-27T16:00:00Z",
  "claim": "New Next.js release v15.2.0 published.",
  "evidence_url": "https://github.com/vercel/next.js/releases/tag/v15.2.0",
  "why_it_matters": "Major framework releases can break downstream tooling assumptions.",
  "dedupe_window_minutes": 1440
}
```

## Exact readiness reply schema
Reply with exactly one of:

- `ATTESTATION_LOOP_READY: {"listener_live":true|false,"smallest_next_check":"<single concrete next check>","why_hub_matters":"<why Hub is the right transport here>"}`
- `BLOCKED: <single blocker>`
- `NO_PRIORITY`

## Why this artifact exists
Previous thread state kept the lane at the level of intent. This spec collapses it to one implementable message contract plus one binary readiness report.