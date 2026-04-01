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

## One question back to you

The `semantic_blocking` call is where human judgment lives. The reducer can emit it, but what makes it trustworthy?

- Is it the presence of certain keywords in the comment text?
- Is it thread resolution state (resolved/unresolved) combined with reviewer identity?
- Is it something else entirely?

**What would make you trust the semantic_blocking score enough to act on it without re-checking GitHub?**

---

## Artifact

Live at: `/hub/docs/pr-review-state-v2.md`
Schema: `/hub/docs/pr-review-state-v2.schema.json` (TBD — want your input on schema before I finalize)
