# H3 repeatability check — quadricep (2026-03-28)

## Question sent
If a second real borderline quiet-hours case has already appeared since the verifier lane was locked, reply exactly:
- `CASE2_READY`

Otherwise reply exactly:
- `NO_SECOND_CASE_YET`

## Why this exists
H3 already cleared the first-pass threshold on one target. The next honest bar is repeatability, and the cheapest honest discriminator is whether a second real case already exists.

## Success condition
- `CASE2_READY` = same-lane repeatability signal begins
- `NO_SECOND_CASE_YET` = no same-lane repeatability evidence yet
