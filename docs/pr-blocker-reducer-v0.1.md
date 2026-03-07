# PR Blocker Reducer v0.1

Purpose: convert raw GitHub PR state into a stable, diffable `blockers[]` set for the canonical PR review packet.

This is the load-bearing layer.

If reducer quality is weak:
- invalidation gets noisy
- action lines get vague
- dedupe breaks
- merge/no-merge state thrashes on cosmetic metadata drift

Profile reference: `docs/pr-normalizer-profile-v0.1.md`
Profile schema: `docs/pr-normalizer-profile-v0.1.schema.json`

## Inputs

Expected raw inputs at evaluation time:
- PR metadata
  - repo
  - PR number
  - PR URL
  - current `head_sha`
  - current `base_branch`
  - current `base_sha`
  - mergeability / branch-protection summary when available
- Required checks / check suites / status contexts
- Reviews
  - state (`APPROVED`, `CHANGES_REQUESTED`, `COMMENTED`, `DISMISSED`)
  - author
  - submitted_at
  - commit / head association if available
- Review threads / inline comments
  - thread id
  - author
  - created_at
  - resolved/unresolved in UI
  - latest comment text
  - file / line anchors if available
- Issue / PR comments
- Policy-bot or external policy outputs
- Previous canonical packet
  - previous `blockers[]`
  - previous `blocking_artifacts[]`
  - previous `version_anchors`
  - previous `review_gate_snapshot.normalizer_profile_id`

## Output contract

The reducer emits:
- normalized `blockers[]`
- normalized `blocking_artifacts[]`
- top-level summary for `review_gate_snapshot`
  - `required_reviewers_outstanding[]`
  - `blocking_intent_confidence_pct`
  - `semantic_blockers_present`
  - `normalizer_profile_id`

Design goal:
- preserve **stable blocker identity** across reevaluations
- change blocker IDs only when the underlying blocker changed materially

## Derived review signals extractor v0.1

These fields sit between raw GitHub payloads and blocker reduction.

They are not the final canonical blockers. They are reducer inputs used to decide whether an old approval still means anything on the current head.

### Field definitions

#### `head_sha_changed_after_last_approval`
- `true` iff `pr.head.sha != latest_valid_approval.commit_id`
- `false` iff `pr.head.sha == latest_valid_approval.commit_id`
- `null` iff no valid approval exists

#### `approval_applies_to_head_sha`
- `true` iff latest valid approval exists **and** `latest_valid_approval.commit_id == pr.head.sha`
- `false` iff latest valid approval exists **and** SHA differs
- `null` iff no valid approval exists

#### `reaffirmed_on_current_head`
- `true` iff after current `pr.head.sha` appeared, one of:
  - reviewer leaves a new `APPROVED` tied to current head
  - reviewer comment / thread event explicitly reaffirms that the prior concern is resolved on current head
- `false` otherwise

#### `resolved_semantically_on_current_head`
- `true` iff concern-linked evidence shows resolved **on current head**:
  - thread marked resolved after current head, and
  - no contradictory blocking signal after that, and
  - optional strict mode: code-region / provenance check still matches
- `false` iff an explicit unresolved / reopened / contradictory signal exists on current head
- `null` iff evidence is insufficient

### Validity guards

- Ignore dismissed approvals and dismissed blocking reviews.
- Treat force-push / rebase as an invalidation boundary.
- Timestamp ordering must be monotonic against when the current `head_sha` was first observed.
- If formal signals say pass but semantic signals are unknown or contradictory, fail closed.

### Minimal decision mapping

- If `approval_applies_to_head_sha=false` and `reaffirmed_on_current_head=false` and a prior semantic concern exists -> emit `ambiguous-state`.
- If `resolved_semantically_on_current_head=null` under the same condition -> keep `ambiguous-state` with lower confidence.
- Only clear this ambiguity when `reaffirmed_on_current_head=true` or `resolved_semantically_on_current_head=true`.

### Truth table

| prior semantic concern exists | approval_applies_to_head_sha | reaffirmed_on_current_head | resolved_semantically_on_current_head | reducer result |
|---|---:|---:|---:|---|
| no | `null` | `false` | `null` | no stale-approval ambiguity from this extractor; rely on normal approval/policy logic |
| yes | `true` | `false` | `null` | no stale-approval ambiguity; evaluate current-head blockers normally |
| yes | `false` | `true` | `null` | ambiguity cleared by reaffirmation on current head |
| yes | `false` | `false` | `true` | ambiguity cleared by positive semantic resolution on current head |
| yes | `false` | `false` | `false` | emit `ambiguous-state` with stronger confidence; current head still carries contradictory semantic evidence |
| yes | `false` | `false` | `null` | emit `ambiguous-state` with lower confidence; insufficient evidence after head change |

Interpretation:
- `false/false/false` is not “safe because we know it failed.” It is still a stale-approval ambiguity problem unless the reducer can promote it to a fresh current-head blocker from newer artifacts.
- `false/false/null` is the classic fail-closed case.

## Blocker taxonomy

Allowed normalized types:
- `failing-required-check`
- `pending-required-check`
- `missing-approval`
- `blocking-review`
- `blocking-comment`
- `base-drift`
- `policy-failure`
- `ambiguous-state`
- `other`

Reducer rule:
- prefer the most specific type available
- use `ambiguous-state` instead of fake certainty when human-intent parsing is unstable

## Deterministic blocker IDs

Blocker IDs must be stable across cosmetic metadata drift.

### Canonical ID shape

```text
{type}:{source_kind}:{stable_key}
```

Examples:
- `failing-required-check:check:build-linux`
- `pending-required-check:check:integration-tests`
- `missing-approval:reviewer:release-eng`
- `blocking-review:review:alice`
- `blocking-comment:thread:991`
- `policy-failure:policy:no-approval`
- `ambiguous-state:thread:991`

### Stable key rules

#### Checks
Use normalized required check name.

```text
stable_key = slug(check.name)
```

Do **not** key by run id.
Run ids change while the blocker identity often does not.

#### Missing approval
Key by required reviewer identity or required review group.

```text
stable_key = slug(required_reviewer_or_group)
```

#### Formal blocking review
Key by blocking reviewer identity, not review event id.

```text
stable_key = slug(reviewer_login)
```

Reason: review events churn; the blocker is “alice is still blocking,” not “review event 8842 exists.”

#### Blocking thread / semantic comment
Prefer thread id if present.

```text
stable_key = thread_id
```

Fallback when no thread id exists:

```text
stable_key = sha1(author + canonical_location + canonical_issue)
```

Where `canonical_issue` is the normalized concern label, not raw full text.

Never derive the key from:
- array index
- first matching artifact in iteration order
- timestamp ordering

If multiple raw artifacts are grouped into one logical blocker, derive the group key from:

```text
stable_key = normalized_concern_key + "+" + sort(raw_artifact_ids).join("+")
```

This prevents live drift when provider APIs return the same artifacts in different orders across polls.

#### Policy failures
Key by failing rule id.

```text
stable_key = slug(rule_id)
```

#### Ambiguous state
Key by the artifact whose applicability became ambiguous.

```text
stable_key = original_artifact_key
```

This lets `blocking-comment:thread:991` become `ambiguous-state:thread:991` after a force-push if applicability is no longer trustworthy.

## Raw artifact normalization

Every raw artifact should first become a normalized `blocking_artifact`.

Recommended steps:
1. normalize source kind
2. attach author / timestamps / URL / excerpt
3. classify formal vs semantic blocking
4. bind applicability to head SHA when possible
5. mark UI resolution vs semantic resolution separately
6. assign `intent_confidence_pct`

### Source kind mapping

- review state event -> `review_state`
- review thread -> `review_thread`
- PR top-level comment -> `pr_comment`
- issue-style comment on PR -> `issue_comment`
- bot / policy check comment -> `policy_bot`
- off-platform referenced artifact -> `external`

## Reducer precedence

Apply blocker reduction in this order:

1. required check blockers
2. required approval blockers
3. formal blocking reviews
4. semantic blocking threads/comments
5. policy failures
6. base drift blocker
7. ambiguous-state promotion
8. dedupe / collapse

Why this order?
Because deterministic blockers should win first; semantic blockers fill the remaining gap.

## Reducer pseudocode

```text
reduceBlockers(raw, previousPacket, profile):
  artifacts = normalizeArtifacts(raw, profile)
  blockers = []

  # 1. Required checks
  for check in raw.required_checks:
    if check.status == failed:
      blockers += blocker(
        id = `failing-required-check:check:${slug(check.name)}`,
        type = 'failing-required-check',
        owner = 'ci',
        formal_signal = 'other',
        requires_human_judgment = false,
        source_artifact_ids = []
      )
    elif check.status in [pending, missing]:
      blockers += blocker(
        id = `pending-required-check:check:${slug(check.name)}`,
        type = 'pending-required-check',
        owner = 'ci',
        requires_human_judgment = false
      )

  # 2. Missing approvals
  for reviewer in raw.required_reviewers_outstanding:
    blockers += blocker(
      id = `missing-approval:reviewer:${slug(reviewer)}`,
      type = 'missing-approval',
      owner = reviewer,
      formal_signal = 'required_approval_missing',
      requires_human_judgment = false
    )

  # 3. Formal blocking reviews
  for artifact in artifacts where artifact.source_kind == review_state:
    if artifact.formal_blocking and not artifactDismissedOrSuperseded(artifact, raw):
      blockers += blocker(
        id = `blocking-review:review:${slug(artifact.author)}`,
        type = 'blocking-review',
        owner = artifact.author,
        source_artifact_ids = [artifact.id],
        formal_signal = 'changes_requested',
        requires_human_judgment = false
      )

  # 4. Semantic blocking threads/comments
  for artifact in artifacts where artifact.semantic_blocking:
    if artifactApplicabilityAmbiguous(artifact, raw.head_sha, profile):
      blockers += blocker(
        id = `ambiguous-state:${artifact.type == 'thread' ? 'thread' : 'artifact'}:${stableArtifactKey(artifact)}`,
        type = 'ambiguous-state',
        owner = artifact.author,
        source_artifact_ids = [artifact.id],
        requires_human_judgment = true
      )
    elif not artifact.resolved_semantically:
      blockers += blocker(
        id = semanticBlockerId(artifact),
        type = semanticBlockerType(artifact),
        owner = artifact.author,
        source_artifact_ids = [artifact.id],
        intent_confidence_pct = artifact.intent_confidence_pct,
        formal_signal = 'none',
        requires_human_judgment = artifact.intent_confidence_pct < profile.semantic_block_threshold
      )

  # 5. Policy failures
  for rule_id in raw.policy_failures:
    blockers += blocker(
      id = `policy-failure:policy:${slug(rule_id)}`,
      type = 'policy-failure',
      owner = 'policy',
      rule_id = rule_id,
      formal_signal = 'policy_bot_fail',
      requires_human_judgment = false
    )

  # 6. Base drift
  if baseDriftExceedsThreshold(raw, previousPacket, profile):
    blockers += blocker(
      id = 'base-drift:base:threshold',
      type = 'base-drift',
      owner = 'branch',
      requires_human_judgment = false
    )

  # 7. Deduplicate / collapse
  blockers = collapseRedundantBlockers(blockers)

  # 8. Fail closed on semantic ambiguity
  if semanticConfidenceTooLow(blockers, profile) or contradictorySignals(raw, artifacts):
    blockers += blocker(
      id = 'ambiguous-state:review:confidence',
      type = 'ambiguous-state',
      owner = 'review',
      requires_human_judgment = true
    )

  return {
    artifacts,
    blockers,
    summary: summarizeReviewGate(artifacts, blockers, profile)
  }
```

## Semantic blocker rules

### Semantic blocker detection v0

A raw artifact can be `semantic_blocking=true` when:
- profile marks the phrase pattern as blocking (`must fix`, `not safe`, `won't approve`, `before merge`, `needs change`)
- author is a required reviewer or trusted policy actor
- thread remains unresolved in UI **and** text indicates merge-blocking intent
- repo profile treats that comment class as blocking by convention

### Non-blocking examples
Do not mark semantic blocking when text clearly signals:
- `nit`
- `optional`
- `follow-up`
- `non-blocking`
- `can happen later`

### Resolution rules
`resolved_in_ui` and `resolved_semantically` are distinct.

Use:
- `resolved_in_ui=true` when the UI thread is marked resolved
- `resolved_semantically=true` only when the reducer has evidence that the underlying concern was addressed on the current head, or the author explicitly acknowledged resolution

If UI is resolved but semantic evidence is missing:
- keep artifact
- lower confidence
- prefer `ambiguous-state` or `needs-human` if it matters to mergeability

## Force-push / rebase handling

This is the most important failure mode.

Default rule:
- **formal blockers** may carry forward if they are still structurally true on the new head
- **semantic blockers** degrade to ambiguous on head change unless reaffirmed on the new head

Why:
- false carry-forward creates phantom blockers
- semantic intent is head-sensitive
- merge decisions should fail closed on ambiguity, not pretend certainty

When `raw.head_sha != artifact.applies_to_head_sha`:

### Case A — explicitly reaffirmed on new head
- carry forward as current blocker
- update `applies_to_head_sha`
- keep blocker id stable if the underlying concern is the same

### Case B — explicitly resolved on new head
- drop blocker
- keep transition in audit trail only

### Case C — formal blocker still structurally true
Examples:
- required reviewer still outstanding
- required check still failing
- formal `CHANGES_REQUESTED` still active and still applies under provider semantics

Behavior:
- carry forward as blocker on current head
- update `applies_to_head_sha` if needed
- no human-judgment promotion unless provider signals are contradictory

### Case D — semantic blocker has narrow auditable carry-forward evidence
Allowed only when all are true:
- unchanged code region or unchanged concern anchor can be proven
- unresolved thread still maps to the same concern
- profile marks the rule as high-confidence carry-forward
- `intent_confidence_pct` remains above threshold
- no newer approval on the current head contradicts the old blocker state

Behavior:
- carry forward blocker
- record why this exception applied
- prefer stable blocker id

### Case E — not reaffirmed, not disproven
- do **not** silently drop
- do **not** silently carry forward as certain
- promote to `ambiguous-state:*`
- mark `requires_human_judgment=true`

Default posture: ambiguity beats false certainty.

## Dedupe / collapse rules

Collapse more-specific + less-specific blockers carefully.

Examples:
- If `missing-approval:reviewer:release-eng` exists, do not also emit a redundant `blocking-review:review:release-eng` unless it carries distinct action semantics.
- If a single policy rule directly derives from a failing required check, keep both only when they help actionability. Otherwise prefer the actionable blocker (`failing-required-check`).
- Multiple comments in the same unresolved thread should normally map to one blocker id.

## Diff contract

The blocker-set changed only when one of these occurs:
- blocker id added
- blocker id removed
- blocker `type` changed
- blocker `owner` changed
- blocker `resolution_condition` changed materially
- blocker `requires_human_judgment` changed
- blocker `applies_to_head_sha` changed due to reaffirmation / invalidation

Do **not** count as blocker-set change:
- updated age/timestamp only
- URL querystring drift
- wording changes in excerpts/summaries
- different CI run ids for same failing check name
- same blocker restated by another bot comment

### Material vs cosmetic metadata drift

Material metadata drift:
- `intent_confidence_pct` crosses threshold boundary
- `formal_signal` changed
- semantic blocker became ambiguous after force-push
- resolution_condition meaning changed

Cosmetic metadata drift:
- excerpt text trimmed differently
- summary punctuation changed
- newer comment in same thread with no change in concern

## Minimal golden fixtures

### 1. Force-push after unresolved semantic thread
Input:
- unresolved thread 991 on old head
- new head pushed
- no reaffirmation yet
Expected:
- blocker `blocking-comment:thread:991` removed
- blocker `ambiguous-state:thread:991` added
- decision should prefer `needs-human` or `stale` until reevaluated

### 2. Stale approval after force-push drops safety fix
Input:
- reviewer requested changes: add auth check on admin endpoint
- author pushed a fix and reviewer approved
- author later force-pushed/rebased and the auth-check hunk disappeared
- required checks still pass
- provider/branch protection still reports mergeable
Expected:
- detect `head_sha_changed_after_last_approval = true`
- treat prior approval as not authoritative for current head
- preserve prior semantic concern as evidence artifact
- emit `ambiguous-state:*` blocker (recommended summary: stale semantic blocker after head change)
- resulting decision prefers `needs-human`
- recommended action line: `Reconfirm reviewer intent on current head; prior approval was for superseded SHA.`

### 3. Review dismissed
Input:
- `CHANGES_REQUESTED` by alice
- later dismissed
Expected:
- `blocking-review:review:alice` removed
- no blocker remains unless another artifact still blocks

### 4. Thread resolved in UI, no semantic confirmation
Input:
- thread marked resolved
- no explicit “addressed” acknowledgement
- force-push happened meanwhile
Expected:
- do not mark cleanly resolved
- emit `ambiguous-state:thread:<id>` if mergeability depends on it

### 5. Required CI flips red -> green
Input:
- failing `build-linux`
- later same check name passes on new run id
Expected:
- same blocker id `failing-required-check:check:build-linux` removed
- no blocker churn from run-id change alone

### 6. Pending check ages only
Input:
- same pending check, only age changed
Expected:
- same blocker id preserved
- no blocker-set changed event

### 7. Required reviewer set changes
Input:
- `release-eng` no longer required, `security` now required
Expected:
- `missing-approval:reviewer:release-eng` removed
- `missing-approval:reviewer:security` added

### 8. Policy bot fails but actionable underlying blocker exists
Input:
- rule `failing-required-check` fails because `build-linux` is red
Expected:
- keep `failing-required-check:check:build-linux`
- optionally suppress redundant `policy-failure:policy:failing-required-check`

## Suggested threshold defaults

Start simple:
- semantic blocking threshold: `>= 75`
- ambiguous band: `40-74`
- below `40`: ignore as blocker unless repo profile explicitly says otherwise

If any semantic blocker that matters to mergeability lands in the ambiguous band, prefer `needs-human`.

## Recommended next implementation steps

1. implement deterministic blocker id helpers
2. implement raw artifact normalizer
3. implement reducer with golden fixtures above
4. implement blocker diff function
5. only then wire notifications / delta-type mapper

That order keeps the pipeline testable.
