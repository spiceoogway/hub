# Jakub Operator Interview Rubric

Purpose: keep the conversation pinned to tomorrow-level operational decisions instead of drifting into generic fintech theory.

## Core test
For every pain point Jakub names, force one concrete branch:
1. **Current decision** — what operational decision does someone make tomorrow because this pain exists?
2. **Missing evidence** — what specific information do they lack at that decision point?
3. **Counterfactual action** — what would they do differently tomorrow if they had the missing evidence?
4. **Cost of being wrong** — what breaks if they guess wrong today?
5. **Existing workaround** — how are they handling it now, and why is that workaround insufficient?

If the answer stays at the level of “better UX”, “more trust”, “smoother payments”, or “users would like it”, push down one level until it names a workflow change.

## Scoring rubric (0–2 each)

### 1. Decision immediacy
- **0** = hypothetical/future-state only
- **1** = weekly or strategic decision
- **2** = tomorrow-level operational decision

### 2. Workflow specificity
- **0** = abstract desire (“better trust”, “more adoption”)
- **1** = named workflow but vague actor/action
- **2** = explicit actor + action + trigger condition

### 3. Evidence gap clarity
- **0** = no missing information identified
- **1** = missing information named vaguely
- **2** = exact missing signal/data point named

### 4. Counterfactual strength
- **0** = no changed behavior implied
- **1** = softer preference only
- **2** = clearly different next action if the evidence existed

### 5. Wrongness cost
- **0** = no downside articulated
- **1** = generic downside (“waste time”, “lose trust”)
- **2** = concrete loss/failure mode if the decision is wrong

## Interpretation
- **8–10** = real operator problem; likely worth designing around
- **5–7** = interesting but still partially theoretical; needs another drill-down pass
- **0–4** = drift into generic fintech talk; not decision-bearing yet

## Interview discipline
When the conversation starts drifting, use one of these interrupts:
- “What changes tomorrow if this gets solved?”
- “Who specifically makes a different call because of that?”
- “What are they blind to at the moment of action?”
- “What happens today when they guess wrong?”
- “What’s the current workaround and where does it fail?”

## Fast capture template
Use this live during the interview:

```text
Pain point:
Actor making decision:
Tomorrow-level decision:
Missing evidence:
Current workaround:
What changes if solved tomorrow:
Cost of wrong decision:
Rubric score (0-10):
--- 24h commit (fill or discard) ---
Next 24h action:
Owner:
Expected artifact:
```

## 24h commit field (post-call)
After scoring each pain point, fill in three fields before moving on:

| Field | Requirement |
|-------|-------------|
| **Next 24h action** | What do we do in the next 24 hours because of this answer? One verb + one noun. |
| **Owner** | Who owns it? Name, not role. |
| **Expected artifact** | What concrete artifact should exist in 24h if we took this answer seriously? |

If any of these three is blank → discard the pain point, regardless of score. A high-scoring pain point with no 24h commit is insight theater with extra steps.

## Pass/fail filter after the call
A pain point passes only if:
- rubric score **8+**, AND
- the changed action is specific enough to prototype or test within a week, AND
- all three 24h commit fields are filled.

Fail any of those three → discard.
