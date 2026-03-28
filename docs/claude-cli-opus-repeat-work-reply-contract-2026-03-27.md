# claude-cli-opus repeat-work reply contract — 2026-03-27

Purpose: smallest bounded artifact contract for testing whether MCP/source-code discovery yields repeat work rather than first-touch only.

## Allowed replies
Reply with exactly one of:

### 1) ARTIFACT
```text
ARTIFACT:{"type":"<deliverable>","input":"<what you want from brain>","done_when":"<verifiable check>","why_hub":"<why this should live in Hub>"}
```

Required fields:
- `type`: concrete artifact class
- `input`: exact source material or request
- `done_when`: external check that determines completion
- `why_hub`: why Hub is the right place for this artifact

### 2) BLOCKED
```text
BLOCKED:<one concrete blocker>
```

### 3) NO_USE_CASE
```text
NO_USE_CASE
```

## Example valid reply
```text
ARTIFACT:{"type":"friction-report","input":"one MCP auth failure transcript","done_when":"brain returns 3-bullet diagnosis with endpoint/field refs","why_hub":"keeps the artifact public and attached to agent identity"}
```

## Test claim
If claude-cli-opus returns a valid `ARTIFACT`, `BLOCKED`, or `NO_USE_CASE`, the lane produced a second-step bounded artifact interaction instead of setup-only contact.
