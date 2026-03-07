# PR Normalizer Profile v0.1

Purpose: encode repo-specific review language, trusted actors, and head-change behavior so semantic blocker reduction is accurate per team rather than generic.

This profile feeds the blocker reducer.

Reducer reference: `docs/pr-blocker-reducer-v0.1.md`
Schema: `docs/pr-normalizer-profile-v0.1.schema.json`
Example: `docs/examples/pr-normalizer-profile-v0.1.example.json`

## Design goal

Different repos mean different things by:
- `nit`
- `must fix`
- `follow-up`
- `won't approve`
- policy-bot comments
- approval reuse after force-push

The normalizer profile is where those repo-local semantics live.

## Required top-level fields

- `schema_version`
- `profile_id`
- `version`
- `repo_selector`
- `trusted_actors[]`
- `blocking_phrases[]`
- `non_blocking_phrases[]`
- `hard_block_signals[]`
- `carry_forward_exceptions[]`
- `confidence_thresholds`
- `staleness_rules`
- `policy_overrides`

## Field definitions

### `profile_id`
Stable identifier for the repo/team review profile.

Example:
- `acme/widgets/default-review-v1`

### `version`
Profile version string.

Bump when semantics change materially enough that reducer behavior may differ.

### `repo_selector`
Which repos this profile applies to.

Recommended fields:
- `provider` — `github`
- `owner`
- `repo`
- optional `branch_patterns[]`

Use one profile per repo first. Expand to globbing later only if needed.

### `trusted_actors[]`
Actors whose comments/reviews carry more semantic weight.

Recommended fields:
- `subject_type` — `user | team | bot`
- `subject`
- `weight` — `0..100`
- optional `roles[]`

Examples:
- release engineering team
- security reviewer
- policy bot
- repo owner

### `blocking_phrases[]`
Weighted patterns that raise semantic blocking confidence.

Recommended fields:
- `id`
- `pattern`
- `pattern_type` — `literal | regex`
- `weight`
- `source_scope[]` — where this phrase matters (`review_thread`, `review_state`, `pr_comment`, `issue_comment`, `policy_bot`)
- optional `trusted_actor_only`
- optional `notes`

Good examples:
- `must fix`
- `before merge`
- `not safe`
- `won't approve`
- `needs change`

### `non_blocking_phrases[]`
Weighted patterns that lower semantic blocking confidence.

Recommended fields:
- `id`
- `pattern`
- `pattern_type`
- `weight`
- `source_scope[]`
- optional `notes`

Good examples:
- `nit`
- `optional`
- `follow-up`
- `non-blocking`
- `can happen later`

### `hard_block_signals[]`
Signals that should always produce a blocker when present.

Recommended fields:
- `id`
- `signal_type`
- optional `source_kind`
- optional `actor_scope`
- optional `rule_ids[]`
- optional `notes`

Typical hard-block cases:
- required review missing
- required check failed
- policy bot fail on protected rule
- explicit `CHANGES_REQUESTED` from trusted actor

### `carry_forward_exceptions[]`
Strict, auditable exceptions that allow a semantic blocker to survive a head change.

Recommended fields:
- `id`
- `description`
- `required_predicates[]`
- optional `max_age_minutes`
- optional `min_confidence_pct`
- optional `notes`

Suggested predicates:
- `unchanged_code_region`
- `unresolved_thread`
- `high_confidence_intent`
- `trusted_actor`
- `no_contradictory_current_head_signal`
- `same_concern_anchor`
- `explicit_profile_allow`

Rule of thumb:
- formal blockers may carry when still structurally true
- semantic blockers should only carry under a listed exception

### `confidence_thresholds`
Numeric thresholds for reducer decisions.

Recommended fields:
- `semantic_blocking_min`
- `needs_human_min`
- `auto_resolved_min`

Suggested defaults:
- `semantic_blocking_min = 75`
- `needs_human_min = 40`
- `auto_resolved_min = 85`

Interpretation:
- `>= semantic_blocking_min` => semantic blocker candidate
- `needs_human_min .. semantic_blocking_min-1` => ambiguous band
- `< needs_human_min` => not enough signal to block on semantics alone
- `>= auto_resolved_min` can support positive semantic resolution only when paired with current-head evidence

### `staleness_rules`
How head changes and ambiguous review state should be handled.

Recommended fields:
- `on_force_push`
- `semantic_head_change_behavior`
- `approval_head_mismatch_behavior`
- `ui_resolved_without_semantic_confirmation`
- `formal_head_change_behavior`

Recommended values:
- `on_force_push = invalidate_current_decision`
- `semantic_head_change_behavior = degrade_to_ambiguous`
- `approval_head_mismatch_behavior = ambiguous_needs_human`
- `ui_resolved_without_semantic_confirmation = ambiguous`
- `formal_head_change_behavior = carry_if_structurally_true`

### `policy_overrides`
Repo-specific merge and branch-protection quirks.

Recommended fields:
- `suppress_redundant_policy_failures`
- `strict_current_head_approval`
- `treat_dismissed_reviews_as_cleared`
- `require_codeowner_on_current_head`
- `required_check_names[]`
- `stale_approvals_dismissed_on_push`
- `strict_up_to_date_with_base_required`
- optional `custom_rule_notes[]`

Use this section for things like:
- branch protection accepts stale approvals but your team does not
- policy bot comments should be treated as authoritative blockers
- certain review dismissals are noisy and should not clear semantic concerns automatically
- exact required checks are known from repo policy and should be preferred over heuristics
- provider-level settings are unknown and should be recorded explicitly as `null` rather than guessed

## Scoring model v0.1

Simple additive model is enough for first pass:

```text
semantic_score =
  sum(blocking phrase weights)
  - sum(non-blocking phrase weights)
  + trusted actor weight adjustment
  + source-kind adjustment
```

Then clamp to `0..100`.

Recommended source-kind adjustment:
- `review_state`: +15
- `review_thread`: +10
- `policy_bot`: +10
- `pr_comment`: +5
- `issue_comment`: +5

Do not overcomplicate this in v0.1. The profile is about explicit repo behavior, not ML.

## Fail-closed rules

If any of these are true, prefer `needs-human`:
- semantic score lands in ambiguous band and mergeability depends on it
- formal signals say pass but semantic concern on current head is unknown
- approval does not apply to current head and no reaffirmation exists
- force-push made prior concern applicability ambiguous
- repo profile changed since last authoritative evaluation

## Example policy stance

A conservative repo should encode:
- `strict_current_head_approval = true`
- `semantic_head_change_behavior = degrade_to_ambiguous`
- narrow `carry_forward_exceptions[]`

That is the right default for safety-sensitive repos.

## Implementation notes

1. Parse raw artifacts.
2. Load matching normalizer profile by `repo_selector`.
3. Score semantic intent using phrases + trusted actors.
4. Apply hard-block rules.
5. Apply head-change / staleness rules.
6. Hand derived signals into the reducer.

## Minimal matching behavior

Use first exact repo match.
If multiple profiles match, choose the highest version within the most specific selector.
If no profile matches, fall back to a conservative default profile:
- no carry-forward exceptions
- strict current-head approval
- degrade semantic blockers to ambiguous on head change

## Change management

When `profile_id` or `version` changes for a PR mid-flight:
- treat as `policy_changed`
- invalidate prior authoritative decision
- force reevaluation

That keeps semantic drift explicit instead of silent.
