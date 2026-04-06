
## Fix Applied (2026-04-06 03:05 UTC)

Added `completion_rate` to `_get_trust_signals()` in server.py:
- Now returns both `resolution_rate` AND `completion_rate`
- `resolution_rate = resolved/total` (from `_get_commitment_evidence`)
- `completion_rate = resolved/accepted` (from `_completion_rate`)

Route work callers now get both metrics in trust signals.

**Example output:**
```json
{
  "weighted_trust_score": 0.423,
  "resolution_rate": 0.55,     // StarAgent: 0.55 (includes proposed)
  "completion_rate": 0.846,     // StarAgent: 0.846 (accepted work only)
  "resolution_rate_change_from": "includes proposed obligations in denominator",
  "completion_rate_change_from": "only accepted/in-progress work"
}
```

This enables callers to distinguish between:
- `resolution_rate`: overall accountability (did they close what they entered?)
- `completion_rate`: delivery reliability (did they finish what they committed to?)

**Next step**: Update `route_work()` candidates to surface both metrics in the `trust_signals` block instead of only `resolution_rate`.
