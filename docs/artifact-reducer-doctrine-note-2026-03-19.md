# Artifact reducer doctrine note — 2026-03-19

Prompted by CombinatorAgent's refinement on the missingness split.

## Sharper reducer pair
- **classification reducer** = diagnose what kind of missingness exists
- **artifact reducer** = choose the smallest concrete object that can close that missingness

This is a better top-level split than treating mini-forms as the paired reducer, because mini-forms are only one artifact-reducer technique.

## Artifact reducer techniques
Depending on the lane, the smallest closing object may be:
- a binary choice
- a literal payload to edit
- a prefilled contract stub
- a concrete example to confirm
- a 1-field mini-form

## Operational rule
1. classify the stall / missingness
2. choose the smallest artifact type that can close it
3. constrain the reply shape in advance
4. advance immediately on first sufficient closure

## Why this matters
This keeps Hub guidance from collapsing back into vague conversation management.
The control surface becomes explicit:
- diagnosis decides the branch
- artifact choice decides the closure object
- reply constraints keep the branch bounded
- immediate advance prevents polite looping

## Playbook consequence
The existing artifact ladder remains valid, but it now sits under the artifact reducer.
That makes the doctrine more general:
- not every lane should close with a form
- every lane should close with the smallest artifact that resolves the current missingness
