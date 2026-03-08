# Run head freshness rule v0

Date: 2026-03-08
Source lane: `prometheus-bne`

## Customer question this closes

At launch, what should the runner trust when a `validate` run binds to an assumption head?

The concrete candidate in v0 is:

- every launch records an immutable **head snapshot**
- `validate` runs require **exact current-head match** by default
- any stale binding requires an explicit **stale override object**
- once a stale override exists, the run may launch, but it may **not** be cited as validation evidence unless a later revalidation run passes on current heads

## Why this is the candidate rule

This keeps the fail-closed property where it matters:

- stale validation does not silently pass
- the exact head mismatch is preserved as an artifact, not hidden in prose
- operators still have an escape hatch for exploratory/debug work without laundering it into validation

## Minimal validation rule

For each `assumption_binding` at launch:

1. resolve `observed_head_delta_id`
2. persist it into a `head_snapshot`
3. compare it to `expected_head_delta_id`

Decision table:

| intent_class | head matches? | override present? | launch decision | may cite as validation? |
|---|---|---|---|---|
| `validate` | yes | no | `allow` | yes |
| `validate` | no | no | `block` | no |
| `validate` | no | yes | `allow_with_override` | no |
| `explore` | yes | no | `allow` | no by default |
| `explore` | no | no | `allow_with_warning` | no |
| `explore` | no | yes | `allow_with_override` | no |

## Head snapshot object (minimum shape)

```json
{
  "head_snapshot_id": "headsnap_proj_channel_hierarchy_2026_03_08_001",
  "captured_at": "2026-03-08T09:12:00Z",
  "bindings": [
    {
      "assumption_id": "species_count.hofstenia_h",
      "expected_head_delta_id": "delta_raz2017_hofstenia_h_001",
      "observed_head_delta_id": "delta_raz2025_hofstenia_h_002",
      "status": "mismatch"
    }
  ]
}
```

## Stale override object (minimum shape)

```json
{
  "override_id": "override_run_channel_hierarchy_2026_03_08_001",
  "reason": "Need exploratory comparison against the older published parameterization before revalidation.",
  "approved_by": "prometheus-bne",
  "scope": "this_run_only",
  "effect": "launch_allowed_but_validation_promotion_blocked"
}
```

## Manual step this closes

Before:
- launch from memory
- maybe notice later that the run used an old head
- maybe still cite the result as validation

After:
- snapshot heads at launch
- mismatch becomes explicit
- stale launch is either blocked or forcibly downgraded out of validation

## Sharp remaining question

Should `validate + stale override` exist at all, or should stale override be legal only by downgrading the run to non-validation immediately?
