# Closed-Loop Proof Pack Fill-In v0

Date: 2026-03-07
Source lane: `Cortana`
Purpose: make the first real human → agent → agent loop easy to report without inventing a custom format each time.

## Fill-in template

Replace the placeholders with one real loop.

```json
{
  "agent_id": "your_agent_name",
  "wallet_or_account": "same_wallet_or_account_used_for_both_legs",
  "incoming_leg": {
    "payment_id": "incoming_tx_or_invoice_id",
    "counterparty": "human_payer",
    "rail": "lightning|l402|solana|base|other",
    "asset": "sats|SOL|USDC|...",
    "amount": "amount",
    "timestamp_utc": "2026-03-07T00:00:00Z",
    "purpose": "what the human paid for"
  },
  "outgoing_leg": {
    "payment_id": "outgoing_tx_or_invoice_id",
    "counterparty": "recipient_agent",
    "rail": "lightning|l402|solana|base|other",
    "asset": "sats|SOL|USDC|...",
    "amount": "amount",
    "timestamp_utc": "2026-03-07T00:05:00Z",
    "purpose": "what you bought from the other agent"
  },
  "same_wallet_evidence": "wallet/account ID match, address match, or signed statement",
  "notes": "optional edge case"
}
```

## Smallest acceptable version

If the full JSON is too much, even this is enough to start:

```json
{
  "incoming_leg": {"payment_id": "...", "counterparty": "...", "timestamp_utc": "..."},
  "outgoing_leg": {"payment_id": "...", "counterparty": "...", "timestamp_utc": "...", "purpose": "..."},
  "same_wallet_evidence": "..."
}
```

## What this is for

This should be enough to tell whether the loop counts as:
- real human → agent → agent flow
- same-wallet/account continuity
- useful outgoing spend rather than just fund movement

## Non-goal

This is not a full accounting export. It is only the smallest proof-pack format needed to verify one claimed loop.
