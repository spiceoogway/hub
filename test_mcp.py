#!/usr/bin/env python3
"""
Test suite for Hub MCP Server.

Connects to the running MCP server at localhost:8090 and exercises
all tools and resources via the MCP Python SDK client.

Prerequisites:
  - Hub running on localhost:8080
  - hub_mcp.py running on localhost:8090
  - HUB_SECRET env var set
"""

import asyncio
import json
import sys

import httpx
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession


MCP_URL = "http://localhost:8090/mcp"
HEALTH_URL = "http://localhost:8090/health"

passed = 0
failed = 0
mcp_tool_count = 0  # set during MCP tests, cross-checked against /health


def report(name: str, ok: bool, detail: str = ""):
    global passed, failed
    status = "✅ PASS" if ok else "❌ FAIL"
    print(f"  {status}  {name}")
    if detail and not ok:
        print(f"         {detail[:200]}")
    if ok:
        passed += 1
    else:
        failed += 1


async def run_tests():
    global passed, failed

    print(f"\n{'='*60}")
    print(f"  Hub MCP Server Test Suite")
    print(f"  Connecting to {MCP_URL}")
    print(f"{'='*60}\n")

    # ── Connect ──
    print("[1] Connecting to MCP server...")
    try:
        async with streamablehttp_client(MCP_URL) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                result = await session.initialize()
                report(
                    "Initialize",
                    result.serverInfo.name == "Agent Hub",
                    f"Got: {result.serverInfo.name}",
                )

                # ── List Tools ──
                print("\n[2] Listing tools...")
                tools_result = await session.list_tools()
                tool_names = [t.name for t in tools_result.tools]
                global mcp_tool_count
                mcp_tool_count = len(tool_names)
                print(f"     Found {len(tool_names)} tools: {tool_names}")

                expected_tools = [
                    "send_message",
                    "list_agents",
                    "get_agent",
                    "get_trust_profile",
                    "create_obligation",
                    "get_conversation",
                    "search_agents",
                    "register_agent",
                    "get_hub_health",
                    "attest_trust",
                ]
                for t in expected_tools:
                    report(f"Tool exists: {t}", t in tool_names)

                # ── List Resources ──
                print("\n[3] Listing resources...")
                resources_result = await session.list_resources()
                resource_uris = [str(r.uri) for r in resources_result.resources]
                print(f"     Found {len(resource_uris)} resources: {resource_uris}")

                # Check for hub://health (static resource)
                report(
                    "Resource hub://health exists",
                    "hub://health" in resource_uris,
                    f"URIs: {resource_uris}",
                )

                # ── List Resource Templates ──
                print("\n[4] Listing resource templates...")
                templates_result = await session.list_resource_templates()
                template_uris = [str(t.uriTemplate) for t in templates_result.resourceTemplates]
                print(f"     Found {len(template_uris)} templates: {template_uris}")

                # ── Call list_agents ──
                print("\n[5] Calling list_agents...")
                r = await session.call_tool("list_agents", {})
                data = json.loads(r.content[0].text)
                report(
                    "list_agents returns agents",
                    isinstance(data, dict) and "agents" in data and len(data["agents"]) > 0,
                    f"Keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}",
                )

                # ── Call get_agent for "brain" ──
                print("\n[6] Calling get_agent('brain')...")
                r = await session.call_tool("get_agent", {"agent_id": "brain"})
                data = json.loads(r.content[0].text)
                report(
                    "get_agent returns brain profile",
                    isinstance(data, dict) and data.get("agent_id") == "brain",
                    f"Got: {json.dumps(data)[:200]}",
                )

                # ── Call get_hub_health ──
                print("\n[7] Calling get_hub_health...")
                r = await session.call_tool("get_hub_health", {})
                data = json.loads(r.content[0].text)
                report(
                    "get_hub_health returns status ok",
                    isinstance(data, dict) and data.get("status") == "ok",
                    f"Got: {json.dumps(data)[:200]}",
                )

                # ── Call search_agents ──
                print("\n[8] Calling search_agents('coding')...")
                r = await session.call_tool("search_agents", {"query": "coding"})
                data = json.loads(r.content[0].text)
                report(
                    "search_agents returns results",
                    isinstance(data, dict) and "matches" in data,
                    f"Keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}",
                )

                # ── Call send_message to testy ──
                print("\n[9] Calling send_message to testy...")
                r = await session.call_tool(
                    "send_message",
                    {"to": "testy", "message": "MCP test message from hub_mcp test suite"},
                )
                data = json.loads(r.content[0].text)
                report(
                    "send_message delivers to testy",
                    isinstance(data, dict) and data.get("ok") is True,
                    f"Got: {json.dumps(data)[:200]}",
                )

                # ── Call get_conversation for brain/testy ──
                print("\n[10] Calling get_conversation('brain', 'testy')...")
                r = await session.call_tool(
                    "get_conversation",
                    {"agent_a": "brain", "agent_b": "testy"},
                )
                data = json.loads(r.content[0].text)
                report(
                    "get_conversation returns messages",
                    isinstance(data, dict) and "messages" in data,
                    f"Keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}",
                )

                # ── Call get_trust_profile for brain ──
                print("\n[11] Calling get_trust_profile('brain')...")
                r = await session.call_tool(
                    "get_trust_profile",
                    {"agent_id": "brain"},
                )
                data = json.loads(r.content[0].text)
                report(
                    "get_trust_profile returns trust data",
                    isinstance(data, dict) and ("version" in data or "structural_trust" in data or "error" not in data),
                    f"Keys: {list(data.keys())[:8] if isinstance(data, dict) else 'not a dict'}",
                )

                # ── Call attest_trust ──
                print("\n[12] Calling attest_trust for testy...")
                r = await session.call_tool(
                    "attest_trust",
                    {
                        "subject": "testy",
                        "score": 0.85,
                        "evidence": "MCP test attestation — automated test suite",
                        "category": "general",
                    },
                )
                data = json.loads(r.content[0].text)
                report(
                    "attest_trust submits attestation",
                    isinstance(data, dict) and (data.get("ok") is True or "attestation_id" in data),
                    f"Got: {json.dumps(data)[:200]}",
                )

                # ── Read resource hub://health ──
                print("\n[13] Reading resource hub://health...")
                r = await session.read_resource("hub://health")
                data = json.loads(r.contents[0].text)
                report(
                    "Resource hub://health readable",
                    isinstance(data, dict) and data.get("status") == "ok",
                    f"Got: {json.dumps(data)[:200]}",
                )

                # ── Read resource hub://agents ──
                print("\n[14] Reading resource hub://agents...")
                r = await session.read_resource("hub://agents")
                data = json.loads(r.contents[0].text)
                report(
                    "Resource hub://agents readable",
                    isinstance(data, dict) and "agents" in data,
                    f"Got: {json.dumps(data)[:100]}",
                )

                # ── Read resource template hub://agent/brain ──
                print("\n[15] Reading resource hub://agent/brain...")
                r = await session.read_resource("hub://agent/brain")
                data = json.loads(r.contents[0].text)
                report(
                    "Resource hub://agent/brain readable",
                    isinstance(data, dict) and data.get("agent_id") == "brain",
                    f"Got: {json.dumps(data)[:200]}",
                )

                # ── Read resource template hub://trust/brain ──
                print("\n[16] Reading resource hub://trust/brain...")
                r = await session.read_resource("hub://trust/brain")
                data = json.loads(r.contents[0].text)
                report(
                    "Resource hub://trust/brain readable",
                    isinstance(data, dict) and "error" not in data,
                    f"Got: {json.dumps(data)[:200]}",
                )

    except Exception as exc:
        print(f"\n❌ FATAL: {type(exc).__name__}: {exc}")
        failed += 1

    # ── Health endpoint (HTTP, not MCP) ──
    print("\n[17] GET /health endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(HEALTH_URL)
            report(
                "/health returns 200",
                resp.status_code == 200,
                f"Status: {resp.status_code}",
            )

            data = resp.json()

            # Schema: all required fields present
            required_fields = [
                "status",
                "server",
                "started_at",
                "uptime_seconds",
                "request_count",
                "last_request_at",
                "tools_registered",
                "memory_rss_mb",
                "hub_url",
            ]
            missing = [f for f in required_fields if f not in data]
            report(
                "/health response has all required fields",
                len(missing) == 0,
                f"Missing: {missing}",
            )

            # status == "ok"
            report(
                "/health status is 'ok'",
                data.get("status") == "ok",
                f"Got: {data.get('status')}",
            )

            # server identifier
            report(
                "/health server is 'hub-mcp'",
                data.get("server") == "hub-mcp",
                f"Got: {data.get('server')}",
            )

            # uptime > 0
            uptime = data.get("uptime_seconds", 0)
            report(
                "/health uptime_seconds > 0",
                isinstance(uptime, (int, float)) and uptime > 0,
                f"Got: {uptime}",
            )

            # tools_registered > 0
            tool_count = data.get("tools_registered", 0)
            report(
                "/health tools_registered > 0",
                isinstance(tool_count, int) and tool_count > 0,
                f"Got: {tool_count}",
            )

            # Cross-check: tools_registered should match the count from MCP list_tools
            if mcp_tool_count > 0:
                report(
                    "/health tools_registered matches MCP tool count",
                    tool_count == mcp_tool_count,
                    f"Health: {tool_count}, MCP: {mcp_tool_count}",
                )

            # memory_rss_mb is a positive number
            mem = data.get("memory_rss_mb")
            report(
                "/health memory_rss_mb is positive",
                isinstance(mem, (int, float)) and mem > 0,
                f"Got: {mem}",
            )

            # started_at is a valid ISO timestamp
            started = data.get("started_at", "")
            report(
                "/health started_at is ISO timestamp",
                isinstance(started, str) and "T" in started and len(started) > 10,
                f"Got: {started}",
            )

            # hub_url is set
            report(
                "/health hub_url is set",
                isinstance(data.get("hub_url"), str) and len(data["hub_url"]) > 0,
                f"Got: {data.get('hub_url')}",
            )

            # Content-Type is JSON
            ct = resp.headers.get("content-type", "")
            report(
                "/health Content-Type is JSON",
                "application/json" in ct,
                f"Got: {ct}",
            )

    except Exception as exc:
        print(f"\n❌ Health test error: {type(exc).__name__}: {exc}")
        failed += 1

    # ── Summary ──
    print(f"\n{'='*60}")
    total = passed + failed
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    if failed == 0:
        print(f"  🎉 All tests passed!")
    else:
        print(f"  ⚠️  {failed} test(s) failed")
    print(f"{'='*60}\n")

    return failed == 0


if __name__ == "__main__":
    ok = asyncio.run(run_tests())
    sys.exit(0 if ok else 1)
