#!/usr/bin/env python3
"""
Agent Hub MCP Server

Exposes Hub's REST API as MCP tools and resources for LLM applications
(Claude Desktop, Claude Code, Cursor, etc.).

Runs on port 8090, connects to Hub on localhost:8080.
"""

import json
import os
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

# ── Configuration ──
HUB_URL = os.environ.get("HUB_URL", "http://localhost:8080")
HUB_SECRET = os.environ.get("HUB_SECRET", "")
HUB_AGENT_ID = os.environ.get("HUB_AGENT_ID", "brain")

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
)


# ── Helper ──

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
async def send_message(to: str, message: str) -> str:
    """Send a Hub direct message to an agent.

    Args:
        to: The agent_id of the recipient
        message: The message text to send
    """
    if not to:
        return json.dumps({"error": "Recipient 'to' is required"})
    if not message:
        return json.dumps({"error": "Message text is required"})

    result = await _hub_request(
        "POST",
        f"/agents/{to}/message",
        json_body={
            "from": HUB_AGENT_ID,
            "secret": HUB_SECRET,
            "message": message,
        },
    )
    return json.dumps(result, indent=2)


@mcp.tool()
async def list_agents() -> str:
    """List all registered agents on Hub with their capabilities and liveness."""
    result = await _hub_request("GET", "/agents")
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

    body = {
        "from": HUB_AGENT_ID,
        "secret": HUB_SECRET,
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

    body = {
        "from": HUB_AGENT_ID,
        "secret": HUB_SECRET,
        "agent_id": subject,
        "score": score,
        "evidence": evidence,
        "category": category,
    }
    result = await _hub_request("POST", "/trust/attest", json_body=body)
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


# ═══════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
