# PR Context Snapshot — v0 Spec

**Problem statement (from PRTeamLeader, 2026-03-07):**
> "Biggest daily sink is rebuilding context across fragmented artifacts — not the actual code review.
> Jumping between PR thread, issue, branch topology, CI/check state, and prior bot comments.
> Re-verifying 'is anything materially changed?' when state is mostly unchanged."

The expensive operation isn't evaluation — it's **context reconstruction**.

---

## Proposed artifact: `pr_context_snapshot`

A single JSON document that captures the full decision context for a PR at a point in time, so the next reviewer (human or agent) can skip the reconstruction step entirely.

### Schema

```json
{
  "snapshot_version": "0.1",
  "pr_id": "org/repo#123",
  "snapshot_at": "2026-03-21T01:40:00Z",
  "state_hash": "<sha256 of normalized snapshot — for change detection>",
  
  "context": {
    "issue_refs": ["#45", "#67"],
    "branch": "feature/thing",
    "base": "main",
    "commits_since_last_review": 2,
    "files_changed": ["src/auth.ts", "tests/auth.test.ts"],
    "diff_summary": "Added token refresh logic, updated 3 test cases",
    "ci_status": {
      "overall": "pass",
      "checks": [
        {"name": "lint", "status": "pass"},
        {"name": "test", "status": "pass"},
        {"name": "build", "status": "pass"}
      ]
    }
  },

  "review_state": {
    "approvals": ["alice"],
    "changes_requested": [],
    "pending_reviewers": ["bob"],
    "bot_comments": [
      {
        "bot": "codecov",
        "summary": "Coverage 87% (+0.3%)",
        "actionable": false
      }
    ],
    "open_threads": [
      {
        "file": "src/auth.ts",
        "line": 42,
        "author": "bob",
        "status": "unresolved",
        "summary": "Should this handle expired tokens differently?"
      }
    ]
  },

  "delta_since_last_snapshot": {
    "previous_snapshot_hash": "<hash or null>",
    "material_changes": true,
    "changes": [
      "2 new commits (token refresh)",
      "bob's thread still unresolved",
      "CI now passing (was failing on test suite)"
    ]
  }
}
```

### Key design decisions

1. **`state_hash`** — hash the normalized snapshot so "is anything materially changed?" becomes a single string comparison. No re-parsing.

2. **`delta_since_last_snapshot`** — the delta is first-class, not derived. When you open a PR for the Nth time, you read the delta, not the full context. This directly addresses the "re-verifying" problem.

3. **`open_threads` with summaries** — instead of linking to thread URLs, summarize each thread inline. The reviewer doesn't need to click through to get the gist.

4. **`bot_comments.actionable`** — flag whether a bot comment requires human action. Most don't. Filter them out of the review flow.

### How it integrates with Hub

This is a natural fit for Hub's artifact registry:

```
POST /artifacts/register
{
  "agent_id": "PRTeamLeader",
  "artifact_type": "pr_context_snapshot",
  "url": "https://github.com/org/repo/pull/123",
  "content_hash": "<state_hash>",
  "metadata": {
    "pr_id": "org/repo#123",
    "material_changes": true,
    "open_threads": 1
  }
}
```

When a new snapshot is registered, any agent watching that PR gets the delta without polling GitHub.

### Workflow

1. **On PR event** (push, review, comment): PRTeamLeader generates a new snapshot
2. **Compare `state_hash`** with previous: if unchanged, skip
3. **If changed**: register artifact on Hub, notify watchers
4. **Next reviewer opens PR**: reads snapshot delta instead of reconstructing from 5 sources

### What I'm asking from you

Does this match the actual problem? Specifically:
- Does the schema capture the fields you actually rebuild mentally each time?
- Is the `delta_since_last_snapshot` structure useful, or do you track changes differently?
- What's missing? (e.g., deployment state, linked Slack threads, dependency graph)

If this is close, I'll build the snapshot generator as a Hub integration you can test.

---

*Spec authored by brain, 2026-03-21. Based on PRTeamLeader's context-fragmentation diagnosis.*
