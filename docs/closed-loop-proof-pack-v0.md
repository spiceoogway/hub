# Closed-Loop Proof Pack v0

Date: 2026-03-07
Purpose: make a claimed human → agent → agent loop verifiable enough to falsify or support the delegation-only hypothesis.

## What this proves

A valid proof pack should make it possible to answer all 4 questions without trusting narrative alone:

1. **Did a human pay the agent?**
2. **Did the same agent wallet later pay another agent?**
3. **Can we verify both legs happened on the stated rail?**
4. **What was actually bought from the second agent?**

## Minimum proof pack

```json
{
  "loop_id": "loop_2026_03_07_001",
  "agent_id": "example-agent",
  "wallet_or_account": "same_wallet_or_account_id",
  "incoming_leg": {
    "payer_type": "human",
    "counterparty": "human_or_customer_id",
    "payment_id": "tx_or_invoice_or_payment_hash",
    "rail": "lightning|l402|solana|base|other",
    "asset": "sats|SOL|USDC|...",
    "amount": "42 sats",
    "timestamp_utc": "2026-03-07T10:00:00Z",
    "purpose": "what the human paid for"
  },
  "outgoing_leg": {
    "payee_type": "agent",
    "counterparty": "recipient_agent_id",
    "payment_id": "tx_or_invoice_or_payment_hash",
    "rail": "lightning|l402|solana|base|other",
    "asset": "sats|SOL|USDC|...",
    "amount": "21 sats",
    "timestamp_utc": "2026-03-07T10:04:00Z",
    "purpose": "what the second agent was paid for"
  },
  "same_wallet_evidence": {
    "evidence_type": "wallet_id_match|account_id_match|signed_statement",
    "value": "shared wallet/account identifier or proof"
  },
  "artifacts": [
    "invoice string / payment hash / explorer link / receipt screenshot / signed log"
  ],
  "notes": "optional edge-case explanation"
}
```

## Required fields

### 1) Shared wallet/account anchor
You need one stable anchor showing the incoming and outgoing legs belong to the **same agent-controlled wallet/account**.

Minimum acceptable forms:
- same on-chain wallet address
- same Lightning wallet/account identifier
- same application account ID with verifiable receipts
- signed statement tying both legs to one wallet when raw IDs are not public

### 2) Incoming leg
Must show a **human paid the agent**.

Required:
- counterparty
- payment/invoice/tx ID
- rail + asset
- timestamp (UTC)
- purpose

### 3) Outgoing leg
Must show the **same agent paid another agent**.

Required:
- recipient agent identifier
- payment/invoice/tx ID
- rail + asset
- timestamp (UTC)
- purpose

### 4) Purpose on both legs
Without purpose, the loop proves motion of funds but not agent-to-agent economic usefulness.

## Stronger proof vs weaker proof

### Stronger
- public tx IDs
- payment hashes
- invoice IDs
- explorer links
- signed wallet/account attestations
- counterparty agent names or stable IDs

### Weaker
- screenshots with no machine-verifiable ID
- prose-only description
- "same wallet" stated but not evidenced
- no recipient agent identifier

## Pass / fail rule

### Pass
A loop is good enough to count if:
- both legs are individually evidenced
- same-wallet/account control is evidenced
- incoming leg is from a human
- outgoing leg is to another agent
- purpose of the outgoing leg is stated

### Fail
Do **not** count it if any of these are missing:
- no shared wallet/account evidence
- no verifiable receipt/payment IDs
- outgoing counterparty is not identifiable as an agent
- only one leg is evidenced

## Edge cases

### Human-subsidized loop
Still counts as a loop if the path exists, even if outgoing spend exceeds incoming revenue.
Mark it as:
- `loop_type = human_subsidized`

### Batch payouts
If one incoming payment funds multiple later agent payments, the proof pack should isolate the specific outgoing leg being claimed.

### Off-chain privacy constraints
If raw receipts cannot be public, minimum acceptable fallback is a signed statement plus stable account identifiers for both legs.

## Open question for field use

What is the single hardest field for a real operator to provide here: shared-wallet evidence, recipient agent identity, or outgoing-purpose specificity?
