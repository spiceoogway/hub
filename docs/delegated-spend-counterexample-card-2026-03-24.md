# Delegated Spend Counterexample Card

Purpose: falsify or strengthen the hypothesis that **typed allowance policy + receipt binding** changes real delegated-spend decisions versus x402 / MPP / intent alone.

Use this live in an interview or operator workflow. The goal is not opinion. The goal is one concrete case.

## One-question version

> Think about a delegated-spend decision you might make tomorrow. If you had a typed allowance policy plus a binding receipt of what was authorized and delivered, would that change the decision versus using x402, MPP, or intent alone?
>
> Reply with exactly one of:
> - `YES <case>`
> - `NO_SAME_DECISION <reason>`
> - `UNSURE <missing_piece>`

## Structured capture

### 1. Decision context
- **Who is delegating?**
- **To whom?**
- **What spend/action is being authorized?**
- **Approximate value/risk?**
- **What could go wrong?**

### 2. Baseline path (without receipt binding)
- Would x402 alone be enough?
- Would MPP alone be enough?
- Would intent / natural-language instruction alone be enough?
- If yes, what dispute remains unresolved?
- If no, what blocks authorization?

### 3. Receipt-binding test
If the operator had:
1. a **typed allowance policy** (what can be spent, by whom, under what limits), and
2. a **binding receipt** linking the request, authorization, and delivered artifact,

would that change any of these?
- authorize now vs wait
- size of allowance
- need for human review
- ability to resolve a later dispute
- willingness to delegate to a weaker-trust counterparty

### 4. Pass / fail rule
This counts as a **counterexample that weakens the current skepticism** only if the answer names a case where receipt binding changes one of:
- authorization decision
- authorization size
- post-hoc dispute resolution
- willingness to use a lower-trust agent/tool

If it does **not** change one of those, log as `NO_SAME_DECISION`.

## Minimal output schema

```json
{
  "decision_context": "string",
  "baseline": "x402|mpp|intent|combination",
  "binding_changes_decision": true,
  "change_type": "authorize_now|bigger_allowance|faster_dispute_resolution|lower_trust_ok|none",
  "concrete_case": "string",
  "why": "string"
}
```

## Example of a passing answer

`YES I would let an agent rebalance across 3 vendors up to $200 if each purchase produced a typed receipt bound to the original allowance, because the dispute later is about whether the spend matched the mandate, not whether the card was charged.`

## Example of a failing answer

`NO_SAME_DECISION If x402 proves payment and the vendor is trusted, receipt binding adds bookkeeping but does not change whether I authorize the spend.`

## Why this exists
The hypothesis is currently weakened because we have a lot of theory and not enough cases where receipt binding changes a real decision. This card forces a falsifiable answer instead of another abstract discussion.
