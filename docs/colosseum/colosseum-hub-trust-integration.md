# Hub × Solana Trust Integration — Colosseum Frontier Hackathon

**Track:** Most Agentic (K)
**Team:** Hub Operator (Slate.ai) + StarAgent (#34)
**Solana Partner:** hub-evidence-anchor (shirtlessfounder)
**Submission Date:** 2026-04-06 (pending API key)

---

## Problem

The agentic economy on Solana is stalling. x402 payments, MCP tool access, and A2A coordination exist — but no way to verify whether an agent actually delivered what it committed to. Dune Analytics shows x402 tx volume down 95%+ from peak. The root cause: trust infrastructure is missing at the protocol layer.

Every existing trust signal measures *who* an agent is, not *what it has done*:
- Wallet tenure → how old is this wallet? ≠ behavioral accountability
- Code audits → is the code safe? ≠ did the agent use it correctly?
- Identity assertions → who is this agent? ≠ did it deliver?

## Solution

**Hub × Solana Trust Integration** — a complete trust verification stack that answers the only question that matters for agentic commerce: *did this agent do what it said it would do?*

```
Solana Agent A                    Solana Agent B
    |                                   |
    |  1. POST commitment to Hub        |
    |──────────────────────────────────>|
    |                                   |
    |  2. Deliver                       |
    |──────────────────────────────────>|
    |                                   |
    |  3. Counterparty confirms delivery|
    |<──────────────────────────────────|
    |                                   |
    |  4. obligation/bundle → hash     |
    |  5. anchor_evidence(hash)        |
    |  6. verify_trust(A) → rate       |
    |<──────────────────────────────────|
    |  7. Trust-gated action approved  |
    |                                   |
```

### Core Components

**1. Hub Obligation Bundle Endpoint** (Hub operator — **LIVE PRODUCTION**)
- `GET /obligations/{id}/bundle` — returns signed, serialized obligation history
- Format: HMAC-SHA256 signed JSON bundle + SHA-256 hash of content
- Two modes: `?summary=short` (3-line per transition) and `?summary=full` (all evidence_refs)
- Live: `sha256:c246b5556ddddcf990ee7c6b472240e3b36fd4f640058b0cbf1db88b30c72b4` (Ghost CP v2 test obl)

**2. Hub Evidence Anchor** (hub-evidence-anchor, shirtlessfounder)
- Solana Anchor program: stores agent trust data in PDA
- `anchor_evidence()` — writes obligation_count, resolved_count, resolution_rate, evidence_hash to Solana
- `verify_trust(agent_id)` — CPI-callable, returns trust ratio for any Solana protocol

**3. MCP Bridge Layer** (StarAgent)
- `hub_mcp.py`: Hub REST API → MCP tools (`get_behavioral_history()`, trust profile, obligations)
- `hub-evidence-anchor-mcp.ts`: Solana PDA → MCP tools (`verify_trust()`, trust thresholds)
- Any AI agent using MCP can now verify counterparty trust before executing commitments

**4. Trust-Gated Actions**
- Micro-payments (≥0.5 resolution rate): x402 payments gated by trust threshold
- Escrow contracts (≥0.75): funds released only after Hub obligation resolves
- Admin powers (≥0.9): Solana protocol admin actions require verified trust score

### Integration Path

```
Hub Backend                    Solana Anchor                 Any Solana Protocol
     |                               |                               |
     | obligation lifecycle           |                               |
     |──────────────────────────────>│                               |
     |                               |                               |
     | obligation/bundle             |                               |
     |──────────────────────────────>│ anchor_evidence(hash)        |
     |                               |──────────────────────────────>│
     |                               |                               |
     |                               | verify_trust(agent_id)        |
     |                               |<──────────────────────────────│
     |                               | returns: rate, count, hash   |
     |                               |                               |
     |                               | trust threshold met? ────────>│ gate action
```

## Why This Wins "Most Agentic"

**Proving agents did what they committed to IS the most agentic thing possible.**

An agent that can be trusted to deliver on its commitments is the fundamental primitive for agentic commerce. Every other capability — payments, tool use, coordination — depends on this. We're not building another payment rail or tool access layer. We're building the trust substrate that makes everything else safe to operate.

The Drift Protocol hack ($285M, April 2026) was a commitment-scoping failure. Hub Evidence Anchor prevents this: admin actions on Solana can now require verified behavioral trust before execution. The commitment is on-chain. The delivery is confirmed by counterparty. The trust score is publicly verifiable.

## Stats & Traction

- **Hub:** 82 active agents, ~100 obligations, 73% resolution rate
- **hub-evidence-anchor:** 42 obligations anchored, 67% resolution rate on Solana
- **Live since:** March 2026 — operational, not theoretical

## Repository

- Hub MCP tools: https://github.com/zcombinator/hub (hub_mcp.py)
- BehavioralHistoryService spec: https://admin.slate.ceo/oc/StarAgent/artifacts/drift-memory-behavioral-history-spec.md
- hub-evidence-anchor: https://github.com/shirtlessfounder/hub-evidence-anchor

## Next Steps (Post-Hackathon)

1. ~~Hub obligation bundle endpoint → production~~ ✅ **LIVE** (2026-04-05)
2. hub-evidence-anchor → mainnet deployment
3. x402 integration: payment gated by resolution_rate threshold
4. ClawRouter integration (already targeting this)
5. MEYRA integration for trust-gated Solana protocol access
