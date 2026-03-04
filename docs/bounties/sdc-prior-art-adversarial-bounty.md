# SDC Prior-Art Adversarial Bounty (Copy/Paste Ready)

## Goal
Test the load-bearing claim with **two independent runs**:
> Is there prior art that directly names the self-describing channel class and derives T*?

## Required Output Contract (exactly 12 lines)
Use this exact parser-friendly markdown block in every submission:

```text
1) claim_id: <string>
2) run_id: <string>
3) investigator: <agent_id>
4) question: <single sentence>
5) verdict: <supports|refutes|inconclusive>
6) confidence: <0.00-1.00>
7) strongest_supporting_evidence: <one sentence + citation>
8) strongest_refuting_evidence: <one sentence + citation>
9) required_sources: <semicolon-separated URLs/DOIs>
10) decisive_missing_evidence: <one sentence>
11) reproducibility_steps: <one command or exact procedure>
12) receipt_bundle: <tx/message IDs proving work done>
```

## Copy/Paste Request Text (Run 1)
```text
Bounty request: run independent prior-art verification for this claim:
"There exists prior art that directly names the self-describing channel class and derives T*."

Please submit your result in the EXACT 12-line format below (no extra lines):
[use the 12-line contract]

Constraints:
- cite concrete sources (URL/DOI)
- include one reproducibility step
- include receipt bundle IDs (messages/txs)
```

## Copy/Paste Request Text (Run 2)
```text
Second independent run requested for the same claim:
"There exists prior art that directly names the self-describing channel class and derives T*."

Do not coordinate with run 1 output. Submit independently using the EXACT 12-line format:
[use the 12-line contract]

Constraints:
- concrete citations only
- one reproducibility step
- receipt bundle IDs included
```

## Copy/Paste Adjudication Prompt
```text
Adjudication task:
Compare Run 1 vs Run 2 strictly on citations, reproducibility, and directness to the claim.
Return:
- winner: <run_id|tie>
- reason: <2 sentences>
- blocking uncertainty: <1 sentence>
```
