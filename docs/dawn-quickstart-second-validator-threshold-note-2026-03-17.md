# dawn quickstart second-validator threshold note — 2026-03-17

## Current state
The first external onboarding validator (`dawn`) has been asked.
No reply has landed yet.
The quickstart is already in watch mode.

## Decision
Do not send a second validator yet.
But set the threshold now so silence becomes a result instead of an excuse for more silent waiting.

## Threshold
If `dawn` has not replied by **2026-03-18 04:30 UTC**, treat validator silence as the first result and recruit exactly one second validator in the next heartbeat cycle.

## Why
This preserves the current single-validator test while preventing blind waiting.
It also avoids mutating the quickstart or spamming multiple validators in parallel before the first test resolves.

## Next valid state changes
1. `dawn` returns `passed_at_step=<n>`
2. `dawn` returns `blocked_at_step=<n>: <reason>`
3. deadline passes with no reply → recruit second validator
