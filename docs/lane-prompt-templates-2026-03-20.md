# Lane prompt templates — 2026-03-20

Purpose: smallest reusable prompt templates for moving stalled Hub lanes.

## 1. Missingness classification prompt
"Classify the current missingness in this lane before proposing another move. Reply with the missingness class only, not a paragraph."

## 2. Smallest-artifact prompt
"Given this lane state, what is the smallest artifact that could change the state machine in one step? Output only the artifact type and its minimal fields."

## 3. Reply-surface prompt
"Reduce the expected reply to the smallest token set that maps cleanly to distinct next actions. Output only the token set and what each token means."

## 4. Hold/exit prompt
"Decide whether this lane should hold or move. If hold, name the hold condition. If move, name the exact exit signal and the next smallest artifact."

## Why these exist
The lane-management docs now define the control surface. These prompt templates are the smallest reusable way to apply that surface in live work.
