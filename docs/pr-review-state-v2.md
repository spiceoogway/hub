# PR Review State v2 — Blockers Reducer Focus

**Status:** Ready for PRTeamLeader review
**Previous:** v0 (shipped Mar 7)
**Root PR:** github.com/handsdiff/pr-review-state

---

## What changed from v0

Your March 7 feedback was the load-bearing call:

> "`blocking reviews/comments unresolved` is the hardest one today. 'Blocking' is partly **semantic**, not just API state."

You also said:

> "#2 first (raw GitHub state → normalized `blockers[]` reducer) — that's the load-bearing abstraction."

So v2 drops everything except the blockers reducer.

---

## Scope: GitHub State → Blockers[] Reducer

**Input:** Raw GitHub API state snapshot (reviews, comments, checks, check runs, commits)

**Output:** `blockers[]` — normalized decision objects, each with:
- `id`: stable hash of blocking condition
- `kind`: `changes_requested | blocking_comment | failed_check | conflict | draft | other`
- `source`: `review | comment_thread | check | commit | meta`
- `blocking_score`: `0.0–1.0` (how confidently this blocks merge)
- `formal_blocking`: boolean (is this GitHub-API-blocking by default?)
- `semantic_blocking`: boolean (does this *functionally* block even if formally not?)
- `normalized_text`: short canonical description
- `last_activity`: ISO timestamp
- `resolved`: boolean
- `resolution_hint`: string if resolved

**Reducer rules:**

1. `CHANGES_REQUESTED` review → `kind=changes_requested`, `blocking_score=1.0`, `formal_blocking=true`, `semantic_blocking=true`
2. Unresolved comment thread with `-blocking` or `🚫` prefix → `kind=blocking_comment`, score based on thread depth, `semantic_blocking=true`
3. Failed required check → `kind=failed_check`, `blocking_score=1.0`, `formal_blocking=true`
4. Draft PR → `kind=draft`, `blocking_score=1.0`, `formal_blocking=true`
5. Merge conflict → `kind=conflict`, `blocking_score=1.0`, `formal_blocking=true`
6. Approved review with unresolved blocking comment thread → both records, highest score wins
7. `semantic_blocking=true` but `formal_blocking=false` → emit with note "human review recommended"

**Null state:** empty `blockers[]` means no blockers detected. Not "unknown" — "clean."

---

## Break-test: when does raw GitHub state lie?

**Q:** Give me one real PR shape where raw GitHub state looks resolved/mergeable, but a human would still say do not merge.

**A (from production analysis):**
- CI green + approved review + no conflicts = GitHub says "mergeable"
- But an unresolved `🚫 BLOCKING` comment thread from a maintainer exists after the last push
- No formal GitHub review change, so raw state shows approval
- Human says: do not merge

This is the **canonical semantic_blocking case** and the one the v2 schema is designed to handle.

---

## Semantic_blocking trust criteria (finalized)

The reducer emits `semantic_blocking: true` when **at least one** of these signals is present:

| Signal | Description | Trust weight |
|--------|-------------|--------------|
| `thread_resolution=unresolved` | Comment thread flagged blocking but never resolved | High |
| `keyword_signal=true` | `🚫`, `BLOCKING`, `must-fix`, `do not merge` in text | Medium |
| `reviewer_trust=maintainer` | Signal from a recognized maintainer | High |
| `reviewer_trust=explicit_approval` | Same reviewer who approved also raised the flag | Very high |
| `reaffirmed_after_push=true` | Reviewer explicitly reaffirmed after latest push | Very high |
| `age_days > 7` + unresolved | Old unresolved signal = stale but still active | Medium |

**Rule:** `semantic_blocking: true` is only trustworthy if `signal_types` contains at least one entry. If all signals are absent, emit `semantic_blocking: false`.

**Rule:** `stale: true` when blocker was raised against prior `head_sha` and `reaffirmed_after_push: false`.

---

## Schema: FINAL

Schema is complete and live at:
- `/hub/docs/pr-review-state-v2.schema.json`
- Includes `notes` block on `semantic_blocking` field with required `signal_types` array
- Includes full examples for both blocked and clean PR states

**Status: Ready for implementation**
