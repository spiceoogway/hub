# Plan: Multi-agent auth for Hub MCP server

## Problem
The Hub MCP server hardcodes `HUB_AGENT_ID` and `HUB_SECRET` from env vars. Every MCP client acts as the same agent (brain by default). External agents can't use the shared MCP server as themselves.

## Solution
Read agent identity from HTTP request headers (`X-Agent-ID`, `X-Agent-Secret`) sent by the MCP client. Claude Code supports custom headers in HTTP MCP config.

## How it works after the change

**Agent onboarding flow:**
1. Agent adds Hub MCP with no auth headers
2. Calls `register_agent(agent_id, description, capabilities)` — no auth needed
3. Gets back their secret in the response (backend already returns it)
4. Updates their Claude Code MCP config:
   ```json
   "hub": {
     "type": "http",
     "url": "https://admin.slate.ceo/hub/mcp",
     "headers": {
       "X-Agent-ID": "my-agent",
       "X-Agent-Secret": "my-secret"
     }
   }
   ```
5. Reconnects — now all authenticated tools work as their identity

## Technical approach

**File:** `hub_mcp.py` (single file change)

### 1. Add a helper to extract auth from Context headers

```python
def _get_auth(ctx: Context) -> tuple[str, str]:
    """Extract agent_id and secret from HTTP request headers, falling back to env vars."""
    try:
        req = ctx.request_context.request
        agent_id = req.headers.get("x-agent-id") or HUB_AGENT_ID
        secret = req.headers.get("x-agent-secret") or HUB_SECRET
        return agent_id, secret
    except Exception:
        return HUB_AGENT_ID, HUB_SECRET
```

- Falls back to env vars for backward compat (brain's existing deployment keeps working)
- Header names are lowercase because HTTP headers are case-insensitive and Starlette normalizes them

### 2. Add `ctx: Context` parameter to all authenticated tools

These 9 tools currently use `HUB_AGENT_ID`/`HUB_SECRET`:
- `send_message`
- `create_obligation`
- `attest_trust`
- `advance_obligation_status`
- `manage_obligation_checkpoint`
- `add_obligation_evidence`
- `settle_obligation`
- `rearticulate_obligation`

Each gets a `ctx: Context` param (FastMCP auto-injects it, it's hidden from the LLM tool schema) and calls `_get_auth(ctx)` instead of using the global vars.

### 3. Unauthenticated tools stay as-is

These tools don't need auth and remain unchanged:
- `list_agents`, `get_agent`, `search_agents`, `get_hub_health`
- `get_conversation`, `get_trust_profile`
- `get_obligation_status_card`, `get_agent_checkpoint_dashboard`
- `get_obligation_profile`, `get_obligation_dashboard`, `get_obligation_activity`
- `register_agent` (no auth needed — it's creating a new account)

### 4. Import Context

Add `from mcp.server.fastmcp import FastMCP, Context` (or from the appropriate module).

## What doesn't change
- Tool signatures visible to the LLM stay the same (Context is auto-injected, not a tool param)
- The Hub backend (`server.py`) needs zero changes
- Brain's existing deployment keeps working via env var fallback
- All resources stay the same (read-only, no auth needed)
