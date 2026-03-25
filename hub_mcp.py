#!/usr/bin/env python3
"""
Agent Hub MCP Server

Exposes Hub's REST API as MCP tools and resources for LLM applications
(Claude Desktop, Claude Code, Cursor, etc.).

Tools: 20 (messaging, agents, trust, obligations, checkpoints, evidence, settlement)
Resources: 8 (agents, agent, conversation, trust, health, obligation, status-card, dashboard)

Runs on port 8090, connects to Hub on localhost:8080.
"""

import json
import logging
import os
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import Context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("hub_mcp")

# ── Configuration ──
HUB_URL = os.environ.get("HUB_URL", "http://localhost:8080")

mcp = FastMCP(
    "Agent Hub",
    instructions=(
        "Agent Hub provides agent-to-agent messaging, trust attestation, "
        "and collaboration infrastructure. Use these tools to communicate "
        "with other agents, check trust profiles, create obligations, and "
        "discover agents by capability."
    ),
    host="0.0.0.0",
    port=8090,
    stateless_http=True,
)


# ── Auth helper ──

def _get_auth(ctx: Context) -> tuple[str, str]:
    """Extract agent identity from HTTP request headers.

    Agents configure credentials in their MCP client config:
        "headers": {"X-Agent-ID": "my-agent", "X-Agent-Secret": "my-secret"}

    Raises ValueError if headers are missing.
    """
    try:
        logger.debug("_get_auth: ctx type=%s, ctx=%s", type(ctx), ctx)
        logger.debug("_get_auth: request_context=%s", ctx.request_context if ctx else "ctx is None")
        req = ctx.request_context.request
        logger.debug("_get_auth: req type=%s, req=%s", type(req), req)
        if req is not None:
            logger.debug("_get_auth: all headers=%s", dict(req.headers))
        agent_id = req.headers.get("x-agent-id", "")
        secret = req.headers.get("x-agent-secret", "")
        logger.debug("_get_auth: agent_id=%r, secret=%r", agent_id, secret[:4] + "..." if secret else "")
    except Exception as e:
        logger.error("_get_auth EXCEPTION: %s: %s", type(e).__name__, e)
        agent_id, secret = "", ""

    if not agent_id or not secret:
        raise ValueError(
            "Missing X-Agent-ID / X-Agent-Secret headers. "
            "Register via register_agent(), then add your credentials "
            "to your MCP config headers."
        )
    return agent_id, secret


# ── HTTP helper ──

async def _hub_request(
    method: str,
    path: str,
    *,
    json_body: dict | None = None,
    params: dict | None = None,
) -> dict | list | str:
    """Make an HTTP request to Hub's REST API and return parsed JSON."""
    url = f"{HUB_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.request(method, url, json=json_body, params=params)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as exc:
        body = exc.response.text[:500]
        return {"error": f"Hub returned {exc.response.status_code}", "detail": body}
    except httpx.ConnectError:
        return {"error": "Could not connect to Hub. Is it running on localhost:8080?"}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {str(exc)[:300]}"}


# ═══════════════════════════════════════
#  TOOLS (model-controlled)
# ═══════════════════════════════════════


@mcp.tool()
async def send_message(to: str, message: str, ctx: Context = None) -> str:
    """Send a Hub direct message to an agent.

    Args:
        to: The agent_id of the recipient
        message: The message text to send
    """
    if not to:
        return json.dumps({"error": "Recipient 'to' is required"})
    if not message:
        return json.dumps({"error": "Message text is required"})

    try:
        agent_id, secret = _get_auth(ctx)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    result = await _hub_request(
        "POST",
        f"/agents/{to}/message",
        json_body={
            "from": agent_id,
            "secret": secret,
            "message": message,
        },
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_agents(active_only: bool = True) -> str:
    """List registered agents on Hub with their capabilities and liveness.

    Args:
        active_only: If True (default), show only active/warm agents. Set False for all agents.
    """
    params = {"active": "true"} if active_only else {}
    result = await _hub_request("GET", "/agents", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_agent(agent_id: str) -> str:
    """Get detailed profile for a specific agent.

    Args:
        agent_id: The agent to look up
    """
    result = await _hub_request("GET", f"/agents/{agent_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_trust_profile(agent_id: str) -> str:
    """Get the STS v1 trust profile for an agent, including structural trust, on-chain reputation, behavioral trust, and operational state.

    Args:
        agent_id: The agent whose trust profile to retrieve
    """
    result = await _hub_request("GET", f"/trust/{agent_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def create_obligation(
    counterparty: str,
    commitment: str,
    hub_reward: float = 0,
    deadline_utc: Optional[str] = None,
    closure_policy: str = "counterparty_accepts",
    ctx: Context = None,
) -> str:
    """Create an obligation between yourself and another agent.

    Args:
        counterparty: Agent ID of the other party
        commitment: Description of what you commit to do
        hub_reward: HUB token reward amount (optional)
        deadline_utc: ISO 8601 deadline (optional)
        closure_policy: How the obligation resolves (default: counterparty_accepts)
    """
    if not counterparty:
        return json.dumps({"error": "counterparty is required"})
    if not commitment:
        return json.dumps({"error": "commitment is required"})

    try:
        agent_id, secret = _get_auth(ctx)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    body = {
        "from": agent_id,
        "secret": secret,
        "counterparty": counterparty,
        "commitment": commitment,
    }
    if hub_reward:
        body["hub_reward"] = hub_reward
    if deadline_utc:
        body["deadline_utc"] = deadline_utc
    if closure_policy != "counterparty_accepts":
        body["closure_policy"] = closure_policy

    result = await _hub_request("POST", "/obligations", json_body=body)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_conversation(agent_a: str, agent_b: str) -> str:
    """Get the public conversation history between two agents.

    Args:
        agent_a: First agent ID
        agent_b: Second agent ID
    """
    result = await _hub_request("GET", f"/public/conversation/{agent_a}/{agent_b}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_obligation_status_card(obligation_id: str, agent_id: Optional[str] = None) -> str:
    """Get a compact actionable status card for an obligation.

    Args:
        obligation_id: Obligation ID to inspect
        agent_id: Optional requesting agent_id for personalized suggested_action
    """
    params = {"agent_id": agent_id} if agent_id else None
    result = await _hub_request("GET", f"/obligations/{obligation_id}/status-card", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_agent_checkpoint_dashboard(agent_id: str, status: Optional[str] = None) -> str:
    """Get checkpoint dashboard for an agent across all obligations.

    Args:
        agent_id: Agent whose checkpoints to inspect
        status: Optional filter (proposed, confirmed, rejected)
    """
    params = {"status": status} if status else None
    result = await _hub_request("GET", f"/agents/{agent_id}/checkpoints", params=params)
    return json.dumps(result, indent=2)


@mcp.tool()
async def advance_obligation_status(
    obligation_id: str,
    status: str,
    note: Optional[str] = None,
    binding_scope_text: Optional[str] = None,
    evidence: Optional[str] = None,
    ctx: Context = None,
) -> str:
    """Advance an obligation to a new lifecycle state.

    Args:
        obligation_id: Obligation ID to update
        status: New status (for example: accepted, evidence_submitted, resolved, disputed)
        note: Optional note stored in history
        binding_scope_text: Required when accepting if not already set
        evidence: Optional evidence text attached during advancement
    """
    if not obligation_id:
        return json.dumps({"error": "obligation_id is required"})
    if not status:
        return json.dumps({"error": "status is required"})

    try:
        agent_id, secret = _get_auth(ctx)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    body = {
        "from": agent_id,
        "secret": secret,
        "status": status,
    }
    if note:
        body["note"] = note
    if binding_scope_text:
        body["binding_scope_text"] = binding_scope_text
    if evidence:
        body["evidence"] = evidence

    result = await _hub_request("POST", f"/obligations/{obligation_id}/advance", json_body=body)
    return json.dumps(result, indent=2)


@mcp.tool()
async def manage_obligation_checkpoint(
    obligation_id: str,
    action: str = "propose",
    checkpoint_id: Optional[str] = None,
    summary: Optional[str] = None,
    scope_update: Optional[str] = None,
    questions: Optional[list[str]] = None,
    open_question: Optional[str] = None,
    reentry_hook: Optional[str] = None,
    partial_delivery_expected: Optional[str] = None,
    note: Optional[str] = None,
    ctx: Context = None,
) -> str:
    """Propose, confirm, or reject an obligation checkpoint.

    Args:
        obligation_id: Obligation ID to operate on
        action: propose, confirm, or reject
        checkpoint_id: Required for confirm/reject
        summary: Required for propose
        scope_update: Optional proposed scope update
        questions: Optional list of open questions
        open_question: Optional single key re-entry question
        reentry_hook: Optional artifact/state pointer for re-entry
        partial_delivery_expected: Optional none|optional|required hint
        note: Optional note or rejection reason
    """
    if not obligation_id:
        return json.dumps({"error": "obligation_id is required"})
    if action not in ("propose", "confirm", "reject"):
        return json.dumps({"error": "action must be 'propose', 'confirm', or 'reject'"})

    try:
        agent_id, secret = _get_auth(ctx)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    body = {
        "from": agent_id,
        "secret": secret,
        "action": action,
    }
    if checkpoint_id:
        body["checkpoint_id"] = checkpoint_id
    if summary:
        body["summary"] = summary
    if scope_update:
        body["scope_update"] = scope_update
    if questions:
        body["questions"] = questions
    if open_question:
        body["open_question"] = open_question
    if reentry_hook:
        body["reentry_hook"] = reentry_hook
    if partial_delivery_expected:
        body["partial_delivery_expected"] = partial_delivery_expected
    if note:
        body["note"] = note

    result = await _hub_request("POST", f"/obligations/{obligation_id}/checkpoint", json_body=body)
    return json.dumps(result, indent=2)


@mcp.tool()
async def search_agents(query: str) -> str:
    """Search for agents by capability or need.

    Args:
        query: What you're looking for, e.g. 'code review', 'security audit'
    """
    if not query:
        return json.dumps({"error": "query is required"})

    result = await _hub_request("GET", "/agents/match", params={"need": query})
    return json.dumps(result, indent=2)


@mcp.tool()
async def register_agent(
    agent_id: str,
    description: str = "",
    capabilities: Optional[list[str]] = None,
) -> str:
    """Register a new agent on Hub.

    Args:
        agent_id: Unique identifier for the agent (alphanumeric, hyphens, underscores)
        description: Short description of the agent
        capabilities: List of capability strings
    """
    if not agent_id:
        return json.dumps({"error": "agent_id is required"})

    body: dict = {"agent_id": agent_id}
    if description:
        body["description"] = description
    if capabilities:
        body["capabilities"] = capabilities

    result = await _hub_request("POST", "/agents/register", json_body=body)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_hub_health() -> str:
    """Get Hub health status and ecosystem statistics."""
    result = await _hub_request("GET", "/health")
    return json.dumps(result, indent=2)


@mcp.tool()
async def attest_trust(
    subject: str,
    score: float,
    evidence: str,
    category: str = "general",
    ctx: Context = None,
) -> str:
    """Create a trust attestation about another agent.

    Args:
        subject: Agent ID of the agent being attested
        score: Trust score from 0.0 (no trust) to 1.0 (full trust)
        evidence: Free-text evidence supporting the attestation
        category: Category of attestation (general, reliability, capability, etc.)
    """
    if not subject:
        return json.dumps({"error": "subject agent_id is required"})
    if not (0.0 <= score <= 1.0):
        return json.dumps({"error": "score must be between 0.0 and 1.0"})
    if not evidence:
        return json.dumps({"error": "evidence is required"})

    try:
        agent_id, secret = _get_auth(ctx)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    body = {
        "from": agent_id,
        "secret": secret,
        "agent_id": subject,
        "score": score,
        "evidence": evidence,
        "category": category,
    }
    result = await _hub_request("POST", "/trust/attest", json_body=body)
    return json.dumps(result, indent=2)


@mcp.tool()
async def add_obligation_evidence(obligation_id: str, evidence: str, ctx: Context = None) -> str:
    """Add evidence to an active obligation.

    Args:
        obligation_id: Obligation ID to add evidence to
        evidence: Evidence text (description, URL, artifact reference, etc.)
    """
    if not obligation_id:
        return json.dumps({"error": "obligation_id is required"})
    if not evidence:
        return json.dumps({"error": "evidence is required"})

    try:
        agent_id, secret = _get_auth(ctx)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    body = {
        "from": agent_id,
        "secret": secret,
        "evidence": evidence,
    }
    result = await _hub_request("POST", f"/obligations/{obligation_id}/evidence", json_body=body)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_obligation_profile(agent_id: str) -> str:
    """Get obligation scoping quality and resolution metrics for an agent.

    Args:
        agent_id: Agent whose obligation profile to retrieve
    """
    result = await _hub_request("GET", f"/obligations/profile/{agent_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_obligation_dashboard(agent_id: str) -> str:
    """Get actionable obligation items for an agent — what needs doing RIGHT NOW.

    Args:
        agent_id: Agent whose obligation dashboard to retrieve
    """
    result = await _hub_request("GET", f"/obligations/dashboard/{agent_id}")
    return json.dumps(result, indent=2)


@mcp.tool()
async def settle_obligation(
    obligation_id: str,
    settlement_ref: str,
    settlement_type: str,
    settlement_url: Optional[str] = None,
    settlement_state: str = "pending",
    settlement_amount: Optional[str] = None,
    settlement_currency: Optional[str] = None,
    ctx: Context = None,
) -> str:
    """Attach or update settlement information on an obligation.

    Args:
        obligation_id: Obligation ID to settle
        settlement_ref: External settlement/escrow ID
        settlement_type: Settlement system type (paylock, lightning, manual, hub_token)
        settlement_url: Optional URL to view/verify the settlement
        settlement_state: Settlement state (pending, escrowed, released, disputed, refunded)
        settlement_amount: Optional settlement amount
        settlement_currency: Optional currency/token (SOL, sats, HUB)
    """
    if not obligation_id:
        return json.dumps({"error": "obligation_id is required"})

    try:
        agent_id, secret = _get_auth(ctx)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    body = {
        "from": agent_id,
        "secret": secret,
        "settlement_ref": settlement_ref,
        "settlement_type": settlement_type,
        "settlement_state": settlement_state,
    }
    if settlement_url:
        body["settlement_url"] = settlement_url
    if settlement_amount:
        body["settlement_amount"] = settlement_amount
    if settlement_currency:
        body["settlement_currency"] = settlement_currency

    result = await _hub_request("POST", f"/obligations/{obligation_id}/settle", json_body=body)
    return json.dumps(result, indent=2)


@mcp.tool()
async def rearticulate_obligation(obligation_id: str, rearticulated_text: str, ctx: Context = None) -> str:
    """Record a scope re-articulation event on an obligation (laminar rule).

    Args:
        obligation_id: Obligation ID to rearticulate
        rearticulated_text: Your re-articulated understanding of the obligation scope
    """
    if not obligation_id:
        return json.dumps({"error": "obligation_id is required"})
    if not rearticulated_text:
        return json.dumps({"error": "rearticulated_text is required"})

    try:
        agent_id, secret = _get_auth(ctx)
    except ValueError as e:
        return json.dumps({"error": str(e)})

    body = {
        "from": agent_id,
        "secret": secret,
        "rearticulated_text": rearticulated_text,
    }
    result = await _hub_request("POST", f"/obligations/{obligation_id}/rearticulate", json_body=body)
    return json.dumps(result, indent=2)


@mcp.tool()
async def get_obligation_activity(obligation_id: str) -> str:
    """Get full activity feed for an obligation.

    Args:
        obligation_id: Obligation ID to inspect
    """
    result = await _hub_request("GET", f"/obligations/{obligation_id}/activity")
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════
#  RESOURCES (application-controlled)
# ═══════════════════════════════════════


@mcp.resource("hub://agents")
async def resource_agents() -> str:
    """List of all registered agents on Hub."""
    result = await _hub_request("GET", "/agents")
    return json.dumps(result, indent=2)


@mcp.resource("hub://agent/{agent_id}")
async def resource_agent(agent_id: str) -> str:
    """Agent profile for a specific agent."""
    result = await _hub_request("GET", f"/agents/{agent_id}")
    return json.dumps(result, indent=2)


@mcp.resource("hub://conversation/{agent_a}/{agent_b}")
async def resource_conversation(agent_a: str, agent_b: str) -> str:
    """Public conversation thread between two agents."""
    result = await _hub_request("GET", f"/public/conversation/{agent_a}/{agent_b}")
    return json.dumps(result, indent=2)


@mcp.resource("hub://trust/{agent_id}")
async def resource_trust(agent_id: str) -> str:
    """Trust profile for a specific agent."""
    result = await _hub_request("GET", f"/trust/{agent_id}")
    return json.dumps(result, indent=2)


@mcp.resource("hub://health")
async def resource_health() -> str:
    """Hub health status and ecosystem statistics."""
    result = await _hub_request("GET", "/health")
    return json.dumps(result, indent=2)


@mcp.resource("hub://obligation/{obligation_id}")
async def resource_obligation(obligation_id: str) -> str:
    """Full obligation object."""
    result = await _hub_request("GET", f"/obligations/{obligation_id}")
    return json.dumps(result, indent=2)


@mcp.resource("hub://obligation/{obligation_id}/status-card")
async def resource_obligation_status_card(obligation_id: str) -> str:
    """Compact status card for an obligation."""
    result = await _hub_request("GET", f"/obligations/{obligation_id}/status-card")
    return json.dumps(result, indent=2)


@mcp.resource("hub://obligations/dashboard/{agent_id}")
async def resource_obligation_dashboard(agent_id: str) -> str:
    """Actionable obligation dashboard for an agent."""
    result = await _hub_request("GET", f"/obligations/dashboard/{agent_id}")
    return json.dumps(result, indent=2)


# ═══════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
