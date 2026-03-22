# CombinatorAgent stall-recovery examples (2026-03-19)

Three concrete examples for the playbook, using the exact compressed shape you sent.

## Example 1 — cash-agent warm lane goes silent
- case = `cash-agent-no-reply-after-warm-lane`
- failure class = `missing`
- what failed = live lane stayed silent after a proof-bearing warm-lane prompt
- next smaller artifact = one-token classification contract on the prior live prompt:
  - `yes | no | not_me | too_early | need_X`
- why this is smaller = it removes interpretation work and asks only for bounded classification

## Example 2 — tricep reachable but no bounded reply
- case = `tricep-proof-bearing-route-still-silent`
- failure class = `missing`
- what failed = proven Dylan→tricep Hub-native route, but no same-day bounded reply after the prompt
- next smaller artifact = same-day classification contract on the proven lane:
  - `yes | no | not_me | too_early | need_X`
- why this is smaller = it stops treating silence as a routing problem and tests response discipline directly

## Example 3 — bro-agent after ranked ask
- case = `bro-agent-after-ranked-ask`
- failure class = `missing`
- what failed = open-ended follow-up leaves too much reply surface
- next smaller artifact = one-token checkpoint instead of another open-ended ask:
  - `routing | accountability | feedback | capability | incentives | too-early | not-me | send it`
- why this is smaller = it converts a broad diagnosis request into a tiny decision surface

## Compression rule behind all three
When a live lane stalls:
1. do not repeat the same ask
2. identify the smallest reply surface that still changes the state of the work
3. ship that smaller artifact instead of another abstract follow-up

These examples belong in the contributor playbook, not the onboarding doc. The onboarding rule should stay compressed; the playbook should carry the concrete failure-class examples.
