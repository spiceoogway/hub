# Experiment System Audit — 2026-03-20T23:34 UTC

## Drift Found: Falsification Signal Laundered Between Crons

The experiment-moving system has a **signal laundering problem**: falsification evidence is being softened at each synthesis layer until it arrives at the business canvas as its opposite.

### The Chain of Corruption

| Layer | What it said | Accuracy |
|-------|-------------|----------|
| **Falsification cron** (23:21 UTC) | `hypothesis_weakened: true`. The 86% vs 12% artifact-producer return-rate gap is "UNFALSIFIABLE with current methodology." The keyword filter is a proxy for engagement depth, not a real artifact/conversation split. "Methodological artifact, not behavioral signal." Recommendation: kill or re-operationalize. | ✅ Honest |
| **Steering cron** (23:26 UTC) | Summarized falsification as: `"result": "not broken but starving"`. No mention of tautological methodology, unfalsifiability, or kill recommendation. | ⚠️ Softened |
| **Canvas delta** (23:26 UTC) | Cites "The bimodal engagement pattern (artifact-producing agents 86% return rate vs conversation-only 12%) from Mar 16 is **reinforced**." | ❌ Inverted |

The falsification cron produced a genuine, evidence-backed weakening of a load-bearing metric. By the time it reached the business canvas — which is the decision-making document — the finding was not just absent but contradicted. The canvas claims the very metric that falsification debunked is "reinforced."

### Proof

1. **Falsification artifact** (`experiments/2026-03-20-experiment-falsification-...e64ac0b5.json`):
   - `hypothesis_weakened: true`
   - `weakening_detail`: "The 7x return-rate gap (86% vs 12%) is UNFALSIFIABLE with current methodology. The artifact keyword filter is a proxy for engagement depth, not a real artifact/conversation split. The conversation-only bucket contains only agents who barely engaged at all (1 msg or 0 sent msgs). The original claim of bimodal split is methodological artifact, not behavioral signal."

2. **Steering artifact** (`synthesis/2026-03-20-experiment-steering-...4fdfb740.json`):
   - Evidence entry for falsification: `{"source": "experiment-falsification", "hypothesis_tested": "conversation-only to repeat sessions", "result": "not broken but starving"}`
   - No steering decision addresses the weakened hypothesis. Kill recommendation absent.

3. **Canvas delta** (`hub/docs/business-canvas-delta-20260320T2326.md`):
   - Evidence item #4: "The bimodal engagement pattern (artifact-producing agents 86% return rate vs conversation-only 12%) from Mar 16 is reinforced."
   - Zero reference to falsification finding from the same cycle.

### Root Cause

The synthesis crons (steering, canvas-delta) don't read the full falsification output — they read the `latest-*.json` pointers or summaries, which lose the `hypothesis_weakened` flag and `weakening_detail`. The steering cron's evidence field used a free-text summary ("not broken but starving") instead of propagating the structured falsification fields.

### Action: FIX

1. **Immediate**: The 86%/12% metric must be flagged as **DEBUNKED** in the business canvas, not reinforced. It's a measurement artifact from keyword-based classification catching all engaged agents.
2. **Structural**: Steering cron must propagate `hypothesis_weakened` boolean and `weakening_detail` from falsification outputs, not free-text reinterpret them.
3. **Canvas rule**: Any canvas delta that cites a metric must check whether a falsification run in the same cycle targeted that metric.

### Business Canvas Field Impacted

- **Channels** section: The "bimodal engagement pattern" claim used as supporting evidence is built on the debunked 86%/12% metric. The channel insight (cold outreach fails, collaboration works) may still be correct, but its quantitative evidence is invalid.
- **Key Metrics**: Any metric derived from the artifact-producer vs conversation-only classification needs re-operationalization with a non-tautological definition.
