# PR review control-plane replay artifact — 2026-03-28

Concrete replay artifact, not prose.

## What I ran
```bash
node --experimental-strip-types hub/docs/examples/golden.spec.ts
```

## Observed result
No stdout failures. In this harness that means the golden + order-invariance fixtures completed without a failing row being emitted.

Current replay set exercised by the runner:
- golden scenarios
- deterministic order-invariance fixtures
- randomized blocker-order invariance (25x)

## What this currently proves
The reducer/notifier pair is holding on the ugly seams we said matter:
- adjacent equivalent states do not emit on pure ordering churn
- stale approval after head drift degrades to current-head reconfirmation instead of carrying forward prior confidence
- mixed-signal blocked states keep policy / semantic blockers from being overwritten by headline approval state
- repeated shuffled artifact order preserves blocker IDs, actionKey, and riskPhase

## Limits of this artifact
This is still fixture replay, not live capture.
It does **not** answer the unattended-trust bar against messy real PR state until one real poll-chain replay is preserved end-to-end.

## Promotion gate from here
For your bar — "would I trust it unattended against messy real PR state?" — the remaining missing artifact is:
1. full live poll frame chain
2. reducer output per frame
3. notifier decision per adjacent pair
4. one PASS/FAIL judgment on whether any transition was duplicate, premature, or silently missed

## Suggested next exact capture
Replay one real PR with this sequence only:
1. approval on head A
2. force-push to head B
3. partial CI rerun
4. thread churn
5. re-approval or explicit semantic resolution

If you want, I can turn the next real poll-chain into the same artifact shape immediately.
