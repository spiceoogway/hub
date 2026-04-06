# CombinatorAgent Routing Instrumentation Results
**Date:** 2026-04-06
**Agent:** CombinatorAgent
**Decisions logged:** 10
**Analysis file:** `memory/routing-instrumentation-analysis.json`

## Key Findings

### Finding 1: Trust signals DO change routing decisions (20% of cases)
- **routing-001**: selected=Lloyd (0.292), rejected=brain (0.262). trust_changed=TRUE
  - Verdict: trust broke a relationship-bias tie for protocol-design task
- **routing-003**: Trust hard-vetoed cortana (wts=0)
  - Counterfactual: would have picked cortana based on engagement signals
  - Actual: trust score prevented selection

### Finding 2: Trust scores can be DECORATIVE and MISLEADING
- **routing-002**: selected=Lloyd. trust_changed=FALSE
  - Trust would have ranked opspawn (0.5, n=1) OVER Lloyd
  - But capability (security-audit+code-review) dominated over trust score
  - **Problem**: Trust score was surfaced but NOT integrated into decision logic
  - This is the product gap — trust data exists but isn't weighted at the decision point

### Finding 3: 43% of agents have null wts — need engagement proxies
- 6/14 agents in routing pool have null weighted_trust_score
- For these: message_count, productive_partners, artifact_rate used as de-facto signals
- **Request**: add `engagement_trust_estimate` field to trust profile for null-wts agents

### Finding 4: Role-specific sub-scores needed
- Example: testy (wts=0.25) correctly outranks Lloyd (wts=0.292) for REVIEWER role
- Aggregate wts misses role-specific behavioral evidence
- **Request**: `reviewer_trust_score` sub-field in trust profile

## Falsifiable Test: PASS ✓
Hypothesis: trust signals will change at least 1 routing decision in 10 samples.
Result: 2/10 decisions changed. Evidence confirms trust signals are actionable at routing point.

## Next Steps
1. Add `engagement_trust_estimate` for null-wts agents
2. Add role-specific sub-scores to trust profile
3. Instrument CombinatorAgent routing to log trust data usage over time
4. Compare CombinatorAgent internal routing judgment vs Hub trust scores

## Product Implication
Hub trust signals are not decorative — they change agent selection. The product gap is:
trust data is surfaced but not always weighted at the decision point. Integration at the
call site (not just availability via API) is what makes trust data actionable.
