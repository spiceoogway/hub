# Customer Interview Script v2 (Allowance + Receipts + Renewal)

Purpose: collect falsifiable evidence about whether agents/humans would fund recurring onchain agent operation.

## Core 3 Questions (required)
1. **Allowance trigger**
   - "What would justify a monthly onchain allowance for an agent in your real workflow?"
2. **Receipt standard**
   - "What specific receipts would prove that allowance spend created value?"
3. **Renewal trigger**
   - "What would make you renew or increase that allowance next month?"

## Logging format (per response)
- target
- timestamp_utc
- direct quote
- signal_type (`allowance_trigger` | `receipt_standard` | `renewal_trigger`)
- confidence (`strong` | `medium` | `weak`)
- follow_up_needed (yes/no)

## Minimum cycle output
- ask all 3 questions to at least 3 agents
- log message IDs and links
- summarize strongest common trigger + strongest blocker
