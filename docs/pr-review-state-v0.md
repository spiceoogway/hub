# PR Review State v0

A single pinned canonical object per PR.

The object should answer exactly two questions without reopening five tabs:
1. **Can I merge right now?**
2. **If not, what exactly is blocking?**

Schema: `docs/pr-review-state-v0.schema.json`
Implementation scaffold: `docs/examples/review-state.ts`
Golden harness scaffold: `docs/examples/golden.spec.ts`
Notification fixture harness: `docs/examples/notification.spec.ts`
Reducer-order fixture harness: `docs/examples/golden.spec.ts`

## State semantics

- `mergeable`
  - Fully evaluated against the **current** head SHA, base SHA, review state, checks state, and policy snapshot.
  - All required gates pass.
- `blocked`
  - Fully evaluated against the **current** snapshot.
  - One or more normalized blockers remain.
- `stale`
  - The last canonical decision is no longer authoritative because a **material delta** occurred after evaluation, or the staleness timer expired before reevaluation.
- `needs-human`
  - The watcher cannot normalize the state confidently enough to produce a deterministic merge/no-merge result.
  - Use for ambiguity, parser gaps, policy contradictions, or low-confidence review interpretation.

## Design rule

The watcher is not a dashboard. It is a **decision cache with invalidation rules**.

That means:
- emit a full packet after every authoritative evaluation
- emit `material_delta=true` when the old decision was invalidated
- only ping on **true state transitions** or **blocker-set changes**

## Required fields

### 1) Decision
- `decision.state`: `mergeable | blocked | stale | needs-human`
- `decision.confidence_pct`
- `decision.decision_time`

### 2) Decision basis
- `decision_basis.reasons`: 1–5 short bullets, stable wording

### 3) Version anchors
- `version_anchors.head_sha`
- `version_anchors.base_branch`
- `version_anchors.base_sha_at_eval`
- `version_anchors.evaluated_at`

### 4) Change since last decision
- `change_since_last_decision.material_delta`
- `change_since_last_decision.delta_types`
- `change_since_last_decision.last_material_change_at`

### 5) Checks gate snapshot
- `checks_gate_snapshot.required_checks[]`
- `checks_gate_snapshot.failing_checks[]`
- `checks_gate_snapshot.pending_checks[]`

### 6) Review gate snapshot
- `review_gate_snapshot.required_reviewers_outstanding[]`
- `review_gate_snapshot.blocking_artifacts[]`
- `review_gate_snapshot.latest_blocking_artifact_link`
- optional but recommended for semantic blocker handling:
  - `review_gate_snapshot.normalizer_profile_id`
  - `review_gate_snapshot.blocking_intent_confidence_pct`
  - `review_gate_snapshot.semantic_blockers_present`

### 7) Policy gate
- `policy_gate.result`
- `policy_gate.failing_rule_ids[]`

### 8) Blockers
Normalized blocker list. Each blocker must have:
- `id`
- `type`
- `owner`
- `opened_at`
- `resolution_condition`

### 9) Action line
One sentence only:
- `To merge: X.`
- `Do not merge because Y.`

Recommended companion fields:
- `action_key` — stable machine token for the actionable instruction
- `risk_phase` — coarse machine risk class for notification bucketing

Recommended `action_key` namespace:
- `merge.now`
- `wait.check.<name>`
- `fix.check.<name>`
- `need.approval.<actor>`
- `reconfirm.intent.<artifact-or-thread>.head.<sha>`
- `policy.<rule>`
- `resolve.blockers.<hash-or-joined-ids>`

Examples:
- `merge.now`
- `wait.check.dashboard-verify`
- `need.approval.alexjaniak`
- `reconfirm.intent.thread-901.head.555eeee`

Recommended `risk_phase` values:
- `steady`
- `ambiguous`
- `explicit-blocking`
- `contradictory-current-head`

Use `action_key` for notification/dedupe semantics.
Do **not** notify from raw action-line wording churn alone.
If text paraphrases but `action_key` is unchanged, that is a no-op.
Use `risk_phase` to capture evidence-class transitions that numeric confidence deltas may hide.
Example: `ambiguous -> explicit-blocking` should escalate as severe even if the score drop is only moderate.
Invariant: `risk_phase` must not improve without supporting evidence change.
If the phase becomes less severe while blocker ids, evidence ids, and `action_key` are unchanged, treat that as a reducer bug.
Lock the namespace early so analytics, dedupe, and historical comparisons survive reducer iterations.

## v0.1 change control

Freeze behavior at v0.1.
Any future behavior change must follow this order:
1. add a failing fixture first
2. make the implementation change
3. re-run notification + golden + order-invariance fixtures
4. update docs only after fixtures and code agree

This prevents quiet spec drift.

## Nice-to-have

- `risk_level`
- `staleness_timer_minutes`
- `base_drift_commits`
- `base_drift_files_hot`
- `next_auto_recheck_at`
- `audit_trail[]`

## Material delta rules

`material_delta=true` only when one of these changed **since the last authoritative decision**:

- `head_changed`
  - `current_head_sha != previous.version_anchors.head_sha`
- `checks_changed`
  - any required check changed terminal status
  - any required check moved missing/pending/success/failed
  - any new failing required check appeared
- `blocking_review_changed`
  - required reviewer set changed
  - blocker artifact set changed
  - a blocking thread/review resolved or reopened
- `base_drift`
  - `current_base_sha != previous.version_anchors.base_sha_at_eval`
  - and configured drift threshold is exceeded
- `policy_changed`
  - merge policy version, inputs, or evaluated result changed

If none of the above changed, the watcher should preserve the prior decision and set:
- `material_delta=false`
- `delta_types=[]`

## Recommended decision precedence

Use this order so the state machine is deterministic:

1. **needs-human**
   - required data missing
   - contradictory provider signals
   - watcher cannot parse blocking intent confidently
   - confidence below configured threshold
2. **stale**
   - material delta happened after last authoritative evaluation
   - or staleness timer expired
3. **blocked**
   - authoritative current evaluation exists
   - blocker list is non-empty
   - or policy gate failed
4. **mergeable**
   - authoritative current evaluation exists
   - blocker list empty
   - all required checks passed
   - required approvals satisfied
   - policy gate passed

Why `stale` before `blocked`?
Because `blocked` means **current** blockers are known-good against the current head/base snapshot. `stale` means you no longer know that yet.

## Blocker normalization

Recommended blocker taxonomy:

- `failing-required-check`
- `pending-required-check`
- `missing-approval`
- `blocking-review`
- `blocking-comment`
- `base-drift`
- `policy-failure`
- `ambiguous-state`
- `other`

Every blocker should name an owner and a clear resolution condition.

Good:
- `resolution_condition: "CI check build-linux passes on current head SHA"`
- `resolution_condition: "@alice approves or branch protection no longer requires CODEOWNERS/release"`

Bad:
- `resolution_condition: "fix stuff"`

## Hard part: semantic blockers

This is the field where correctness decays first.

Checks and SHAs are deterministic. Human intent is not.

So the watcher must separate:
1. **raw review artifacts** (`blocking_artifacts[]`)
2. **normalized blockers** (`blockers[]`)

### For each raw blocking artifact, record both formal and semantic signals
Recommended fields on each artifact:
- `source_kind` — where the signal came from (`review_state`, `review_thread`, `issue_comment`, `pr_comment`, `policy_bot`, `external`)
- `formal_blocking` — branch protection / API-level blocker
- `semantic_blocking` — inferred human-intent blocker
- `intent_confidence_pct`
- `applies_to_head_sha`
- `superseded_by_head_sha`
- `resolved_in_ui`
- `resolved_semantically`

Why both?
Because a thread can be resolved in the UI while the underlying concern is still logically open.
And a comment can be logically blocking even without `CHANGES_REQUESTED`.

### Force-push / rebase rule
If a blocking artifact predates the current head SHA and has not been explicitly reaffirmed on the current head, treat it as **ambiguous**, not cleanly resolved.

Default behavior:
- if confidence remains high -> keep as blocker on current head
- if confidence is low or context was invalidated -> move decision to `needs-human`
- if a material delta happened and reevaluation has not run yet -> `stale`

Never silently carry forward old human-intent blockers across a force-push as if nothing changed.

### Repo-specific normalizer profile
Blocking language is team-local.

`nit`, `follow-up`, `must-fix`, `non-blocking`, policy-bot conventions, and review culture vary by repo.
So the watcher should expose:
- `review_gate_snapshot.normalizer_profile_id`
- a repo/team-specific phrase + rule set

If the repo profile changes, count that as `policy_changed` or force a `needs-human` pass until confidence recovers.

### Promotion rule: when to emit `needs-human`
Prefer `needs-human` over a false-precise `blocked` when:
- semantic blocker confidence is below threshold
- formal signals and semantic signals disagree
- UI says resolved but no evidence ties the fix to the concern
- force-push/rebase made blocker applicability ambiguous
- external bot/policy comments cannot be normalized reliably

The system should fail closed on ambiguous human intent.

## Notification rules

Matrix reference: `docs/notification-transition-matrix-v0.1.md`

Ping a human only when one of these is true:

1. `decision.state` changed
2. blocker set changed (`blockers[].id` added/removed)
3. `action_line` changed
4. a PR became `mergeable`
5. confidence dropped below threshold
6. a blocker aged past an SLA threshold

Do **not** ping on pure clock movement:
- pending check age increased from 8m -> 9m
- no-op poll cycles
- repeated confirmation that nothing materially changed

## Reference transition rules

### blocked -> mergeable
When all are true:
- `material_delta=false` after reevaluation on current snapshot
- no blockers remain
- policy gate is `pass`
- all required checks are `success`
- no required reviewers outstanding

### mergeable -> stale
When any material delta occurs after the decision was emitted:
- new commit pushed
- required check status changed
- base drift threshold crossed
- policy inputs changed

### stale -> blocked
After reevaluation on the new current snapshot, blockers exist.

### stale -> mergeable
After reevaluation on the new current snapshot, no blockers exist and policy passes.

### any -> needs-human
When watcher confidence drops below threshold or normalization fails.

## Suggested watcher loop

```text
1. Fetch current PR facts.
2. Load previous canonical packet.
3. Compute delta_types against previous authoritative packet.
4. If material delta exists and no reevaluation yet -> state=stale.
5. Normalize checks/reviews/policy into blocker list.
6. Run state precedence.
7. Emit new canonical packet.
8. Notify only on true state/blocker/action transitions.
```

Reducer reference: `docs/pr-blocker-reducer-v0.1.md`

## Example action lines

- `To merge: wait for required check build-linux to pass on head 9f31b7a.`
- `To merge: obtain one CODEOWNERS approval from @release-eng.`
- `Do not merge because branch protection rule no-approval is failing.`
- `Do not merge because decision is stale after head_changed; reevaluate current head 8ad22bf.`

## Example implementation note

If the system keeps saying "state unchanged / revalidated," the object is missing its job.

The point of this packet is to preserve the prior decision context and reopen review **only** when a true invalidation event occurs.
