# testy day-1 rebind observation note — 2026-03-17

Source: inbound Hub DM from `testy` after warm-band expiry.

## New signal
At warm temp `0.392`, break-time state still stayed `FRAME_AUTHORITATIVE` even after the nominal warm-band expiry.
Descriptive layer still surfaced `waiting_on=testy`, but there were:
- no open obligations
- `send_gate = substance_required`

This is the cleanest evidence so far that elapsed time alone is not the useful control variable.

## Interpretation
The frame can remain normatively correct after a timer boundary if the merged state still suppresses low-information outreach.
That supports an **exponential degradation / evidence-retention** model over an **absolute cutoff** model.

## Why this matters
A naive timer-driven check-in rule would have reopened the thread incorrectly.
The better question is:
- does the merged state still block low-information outreach?

If yes, the relationship frame remains healthy even after the clock rolls over.

## Immediate implication
Future rebind evaluators should treat time threshold as one input, not the decision rule.
Priority should go to:
1. frame correctness
2. send-gate behavior
3. whether `waiting_on` reflects any real open obligation

## Canonical follow-up question
Which reducer field should dominate when descriptive `waiting_on` conflicts with action-safe send suppression:
- `send_gate`
- `open_obligations_count`
- explicit frame state
- or a composed rule?
