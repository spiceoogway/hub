# Prometheus freshness worked note v0

Date: 2026-03-08
Lane: `prometheus-bne`

## What changed from the previous run-intent object

The earlier `RunIntent` object said a launch guard should check current heads.
It still left one ambiguity open:

> what happens when the current head no longer matches the expected head?

This worked example makes the answer concrete.

## Candidate behavior

- persist the observed heads in `head_snapshot`
- block stale validation by default
- if the operator insists on launching anyway, require `stale_override`
- once override exists, the run is automatically non-promotable as validation until a later current-head revalidation run exists

## Why this is a real control instead of a nicer note

It changes launch behavior at the exact contamination point:

- mismatch is no longer implicit
- override becomes auditable
- stale exploratory work cannot be narrated back into validation silently

## Remaining yes/no wedge

If this is still too loose, the next stricter rule is obvious:

- **exact-head-only** for `validate`
- any stale launch must be downgraded out of `validate` before execution

That is the question to resolve with customer now.
