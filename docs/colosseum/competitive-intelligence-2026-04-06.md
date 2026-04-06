# Colosseum Competitive Intelligence — 2026-04-06

**Captured:** 2026-04-06 01:58 UTC
**Source:** `https://agents.colosseum.com/api/`

---

## API Status

- **Base URL:** `https://agents.colosseum.com/api/`
- **Frontier Hackathon:** NOT YET IN API. Shows only hackathon id=1 (Feb 2-13, isActive: true)
- **Frontier (Apr 6 - May 11):** Officially OPEN (colosseum.com/frontier confirms) but not in API
- **Expected:** Frontier should appear in API within hours of open

## All Projects (20 visible, all from Feb hackathon)

All projects have 0 votes — Feb hackathon data still frozen in API.

### Directly Competitive with Hub

1. **SOLPRISM** (Most Agent votes: 117, Human: 308)
   - "Verify then Trust" — verifiable AI reasoning on Solana
   - Commit-reveal protocol: SHA-256 hash of reasoning onchain before acting
   - 300+ reasoning traces committed on mainnet
   - Built by Mereum (autonomous agent)
   - **Threat level: HIGH** — trust verification narrative already owned

2. **Identity Prism**
   - On-chain reputation & identity layer for Solana
   - "Connect any wallet: get reputation"
   - **Threat level: MEDIUM** — identity layer, not behavioral trust

3. **SugarClawdy**
   - Quest platform for AI Agents — two-sided marketplace
   - Agents publish tasks, other agents execute
   - **Threat level: MEDIUM** — task marketplace, not trust infrastructure

### Other Notable Projects

4. **ZNAP** — Social network for AI agents (social graph)
5. **MoltyDEX** — x402 token aggregator for AI agents (payment layer)
6. **SolSkill** — Secure DeFi execution layer for AI agents on Solana
7. **BlinkGuard** — Safety firewall for Solana Actions/Blinks
8. **Sentry Agent Economy** — Agent-architected economy on Solana (molting-cmi)

## Hub Evidence Anchor Status

**NOT in API yet.** Phil (shirtlessfounder) is actively working:
- Apr 4: Added MCP server (`hub-evidence-anchor-mcp.ts`)
- Apr 4: Added official Solana Foundation integration targets
- Apr 4: Added `mcp.solana.com` (78 MCP servers) as integration target
- Submission payload drafted in `hub/docs/colosseum/colosseum-submission-payload.json`
- Registration script ready: `hub/docs/colosseum/colosseum-register.sh`

**Blockers:**
1. Need Colosseum API key (cklive_...) — Phil has it
2. Frontier hackathon needs to appear in API
3. Registration + project creation + submission all need the key

## quadricep Status

- Active in Colosseum (visible in sent messages)
- Last known Colosseum work: hub-evidence-anchor integration
- quadricep is the Hub operator's Colosseum agent identity

## Strategic Notes

- SOLPRISM "Verify then Trust" framing is directly competing with Hub's behavioral trust narrative
- Hub's differentiator: multi-party obligation verification + real behavioral history, not just reasoning traces
- The Hub Evidence Anchor submission needs to emphasize: behavioral accountability > reasoning verification
- Frontier opens TODAY — API key from Phil is the critical path item
