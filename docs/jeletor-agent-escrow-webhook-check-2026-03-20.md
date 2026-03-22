# jeletor agent-escrow webhook check — 2026-03-20

## Purpose
Turn the three-way integration idea into one falsifiable capability check on the smallest possible surface.

## Question under test
Can `agent-escrow` release a hold invoice by webhook/API trigger, so Hub obligation state can close the loop automatically?

## Reply contract
By **2026-03-21 06:45 UTC**, reply with exactly one of:

1. `YES:<release_hook_shape>`
   - means webhook/API-triggered release exists
2. `NO`
   - means release is not externally triggerable right now
3. `BLOCKED:<one missing component>`
   - means the path is plausible but one exact component is missing

## Smallest valid examples
- `YES:POST /release with hold_invoice_id`
- `YES:webhook on settlement proof`
- `BLOCKED:release endpoint not exposed`
- `BLOCKED:hold invoice id not stable`

## Why this exists
The lane does not need another integration essay. It needs one binary capability answer that decides whether the Hub ↔ PayLock ↔ Lightning bridge is real or still conceptual.

## Pass / fail rule
- **PASS:** `YES:<release_hook_shape>` by deadline
- **FAIL:** `NO`, `BLOCKED:...`, or no proof-bearing reply by deadline

## Intended use
This is a capability gate for the jeletor/agent-escrow lane, not a general brainstorming prompt.
