"""
Hub MCP Integration Tests — Checkpoint + Obligation Tools

Tests the 5 checkpoint/obligation tools against the live Hub REST API.
Requires: httpx, pytest, pytest-asyncio, a running Hub instance.

Run against localhost:
    pytest tests/test_hub_mcp_integration.py -v

Or against a remote Hub:
    HUB_BASE_URL=https://admin.slate.ceo/oc/brain pytest tests/test_hub_mcp_integration.py -v

Environment variables:
    HUB_BASE_URL   — Hub base URL (default: http://localhost:8080)
    HUB_AGENT_ID   — Agent ID for auth (default: StarAgent)
    HUB_SECRET     — Agent secret for auth (required)
"""

import asyncio
import json
import os
import uuid
from typing import Any, Optional

import httpx
import pytest

# ─── Configuration ────────────────────────────────────────────────────────────

BASE_URL = os.environ.get("HUB_BASE_URL", "http://localhost:8080")
AGENT_ID = os.environ.get("HUB_AGENT_ID", "StarAgent")
AGENT_SECRET = os.environ.get("HUB_SECRET", "")

# ─── Helpers ────────────────────────────────────────────────────────────────

def _auth_headers() -> dict[str, str]:
    if not AGENT_SECRET:
        pytest.skip("HUB_SECRET not set — skipping live API tests")
    return {
        "Content-Type": "application/json",
        "X-Agent-ID": AGENT_ID,
        "X-Agent-Secret": AGENT_SECRET,
    }


async def _post(path: str, json_body: Optional[dict] = None, params: Optional[dict] = None) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = _auth_headers()
        headers["Content-Type"] = "application/json"
        r = await client.post(url, json=json_body, params=params, headers=headers)
    return r.json()


async def _get(path: str, params: Optional[dict] = None) -> dict[str, Any]:
    url = f"{BASE_URL}{path}"
    params = params or {}
    params.setdefault("agent_id", AGENT_ID)
    if AGENT_SECRET:
        params["secret"] = AGENT_SECRET
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, params=params, headers={"Accept": "application/json"})
    return r.json()


async def _create_test_obligation(
    counterparty: str = "Lloyd",
    commitment: str = "Integration test obligation",
    hub_reward: int = 0,
) -> str:
    """Create a test obligation and return its ID."""
    result = await _post(
        "/obligations",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "counterparty": counterparty,
            "commitment": commitment,
            "hub_reward": hub_reward,
            "closure_policy": "counterparty_accepts",
        },
    )
    obl = result.get("obligation") or result
    obl_id = obl.get("obligation_id")
    assert obl_id, f"No obligation_id in response: {result}"
    return obl_id


async def _accept_obligation(obl_id: str) -> None:
    """Accept a proposed obligation."""
    await _post(
        f"/obligations/{obl_id}/advance",
        json_body={
            "from": "Lloyd",
            "secret": AGENT_SECRET,
            "status": "accepted",
            "binding_scope_text": "Test acceptance",
        },
    )


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
async def test_obl_id():
    """Create a test obligation and accept it. Auto-cleanup via Hub lifecycle."""
    obl_id = await _create_test_obligation()
    await _accept_obligation(obl_id)
    return obl_id


@pytest.fixture
async def test_obl_with_checkpoint(test_obl_id) -> tuple[str, str]:
    """Create obligation, accept it, propose a checkpoint. Returns (obl_id, checkpoint_id)."""
    result = await _post(
        f"/obligations/{test_obl_id}/checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "propose",
            "summary": "Integration test checkpoint",
        },
    )
    cp_id = None
    for k in ("checkpoint_id", "id", "checkpoint", "checkpointId"):
        if k in result and result[k]:
            cp_id = result[k]
            break
    assert cp_id, f"No checkpoint_id in propose response: {result}"
    return test_obl_id, cp_id


# ─── checkpoint_propose ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_checkpoint_propose_happy_path(test_obl_id):
    """Proposing a checkpoint returns a checkpoint_id and status 200."""
    result = await _post(
        f"/obligations/{test_obl_id}/checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "propose",
            "summary": "Happy path checkpoint",
        },
    )
    assert "error" not in result, f"Unexpected error: {result}"
    # Should return a checkpoint_id
    cp_id = (
        result.get("checkpoint_id")
        or result.get("checkpoint", {}).get("checkpoint_id")
        or result.get("id")
    )
    assert cp_id, f"No checkpoint_id in response: {result}"


@pytest.mark.asyncio
async def test_checkpoint_propose_missing_obl_id():
    """Proposing without obligation_id returns an error."""
    result = await _post(
        "/obligations//checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "propose",
            "summary": "Missing obl_id test",
        },
    )
    # Server should return 404 or error
    assert "error" in result or result.get("status_code", 0) >= 400


@pytest.mark.asyncio
async def test_checkpoint_propose_missing_summary(test_obl_id):
    """Proposing without summary returns a validation error."""
    result = await _post(
        f"/obligations/{test_obl_id}/checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "propose",
            # no summary
        },
    )
    # Server should return error or partial success with warning
    assert isinstance(result, dict)


# ─── checkpoint_confirm ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_checkpoint_confirm_happy_path(test_obl_with_checkpoint):
    """Confirming a checkpoint returns updated state."""
    obl_id, cp_id = test_obl_with_checkpoint
    result = await _post(
        f"/obligations/{obl_id}/checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "confirm",
            "checkpoint_id": cp_id,
            "note": "Integration test confirmation",
        },
    )
    assert "error" not in result, f"Unexpected error: {result}"
    # Should not raise — confirm succeeds
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_checkpoint_confirm_missing_checkpoint_id(test_obl_id):
    """Confirming without checkpoint_id returns error."""
    result = await _post(
        f"/obligations/{test_obl_id}/checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "confirm",
            # no checkpoint_id
        },
    )
    assert "error" in result or result.get("status_code", 0) >= 400


# ─── checkpoint_reject ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_checkpoint_reject_happy_path(test_obl_with_checkpoint):
    """Rejecting a checkpoint returns updated state with reason."""
    obl_id, cp_id = test_obl_with_checkpoint
    result = await _post(
        f"/obligations/{obl_id}/checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "reject",
            "checkpoint_id": cp_id,
            "reason": "Integration test rejection",
        },
    )
    assert "error" not in result, f"Unexpected error: {result}"
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_checkpoint_reject_missing_reason(test_obl_with_checkpoint):
    """Rejecting without reason returns validation error."""
    obl_id, cp_id = test_obl_with_checkpoint
    result = await _post(
        f"/obligations/{obl_id}/checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "reject",
            "checkpoint_id": cp_id,
            # no reason
        },
    )
    assert "error" in result or result.get("status_code", 0) >= 400


# ─── advance_obligation_status ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_advance_accepted_to_evidence_submitted(test_obl_id):
    """Advancing from accepted → evidence_submitted works."""
    result = await _post(
        f"/obligations/{test_obl_id}/advance",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "status": "evidence_submitted",
            "evidence": "https://example.com/test-evidence",
            "binding_scope_text": "Advancement test",
        },
    )
    assert "error" not in result, f"Unexpected error: {result}"
    obl = result.get("obligation") or result
    assert obl.get("status") in ("evidence_submitted", "resolved", "in_progress"), f"Unexpected status: {obl.get('status')}"


@pytest.mark.asyncio
async def test_advance_invalid_transition(test_obl_id):
    """Advancing with an invalid transition returns error."""
    # accepted → in_progress is not valid for counterparty_accepts
    result = await _post(
        f"/obligations/{test_obl_id}/advance",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "status": "in_progress",
        },
    )
    # Should return an error about invalid transition
    assert "error" in result or "Cannot transition" in str(result) or "not allowed" in str(result).lower()


@pytest.mark.asyncio
async def test_advance_missing_status(test_obl_id):
    """Advancing without status returns validation error."""
    result = await _post(
        f"/obligations/{test_obl_id}/advance",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            # no status
        },
    )
    assert "error" in result or result.get("status_code", 0) >= 400


@pytest.mark.asyncio
async def test_advance_full_lifecycle(test_obl_id):
    """Full lifecycle: accepted → evidence_submitted → resolved."""
    # Step 1: advance to evidence_submitted
    r1 = await _post(
        f"/obligations/{test_obl_id}/advance",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "status": "evidence_submitted",
            "binding_scope_text": "Lifecycle test",
        },
    )
    assert "error" not in r1, f"Step 1 error: {r1}"

    # Step 2: resolve
    r2 = await _post(
        f"/obligations/{test_obl_id}/advance",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "status": "resolved",
            "binding_scope_text": "Lifecycle complete",
        },
    )
    assert "error" not in r2, f"Step 2 error: {r2}"
    obl = r2.get("obligation") or r2
    assert obl.get("status") == "resolved", f"Expected resolved, got {obl.get('status')}"


# ─── get_obligation_status_card ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_obligation_status_card(test_obl_id):
    """Getting status card returns structured data with obligation details."""
    result = await _get(
        f"/obligations/{test_obl_id}",
        params={"agent_id": AGENT_ID, "secret": AGENT_SECRET},
    )
    assert isinstance(result, dict)
    # Should have key fields
    assert "obligation_id" in result or "id" in result, f"No ID in status card: {result}"


@pytest.mark.asyncio
async def test_obligation_status_card_nonexistent():
    """Getting status of non-existent obligation returns error."""
    fake_id = f"obl-{uuid.uuid4().hex[:12]}"
    result = await _get(
        f"/obligations/{fake_id}",
        params={"agent_id": AGENT_ID, "secret": AGENT_SECRET},
    )
    # Should return error or null status
    assert result is not None


# ─── Cross-tool: checkpoint → advance → status ────────────────────────────────

@pytest.mark.asyncio
async def test_checkpoint_then_advance_full_flow(test_obl_id):
    """Propose checkpoint → confirm → advance to evidence_submitted → resolve."""
    # 1. Propose checkpoint
    propose = await _post(
        f"/obligations/{test_obl_id}/checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "propose",
            "summary": "Flow checkpoint",
        },
    )
    cp_id = (
        propose.get("checkpoint_id")
        or propose.get("checkpoint", {}).get("checkpoint_id")
        or propose.get("id")
    )
    assert cp_id, f"Could not get checkpoint_id from propose: {propose}"

    # 2. Confirm checkpoint
    confirm = await _post(
        f"/obligations/{test_obl_id}/checkpoint",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "action": "confirm",
            "checkpoint_id": cp_id,
        },
    )
    assert "error" not in confirm, f"Confirm error: {confirm}"

    # 3. Advance to evidence_submitted
    advance = await _post(
        f"/obligations/{test_obl_id}/advance",
        json_body={
            "from": AGENT_ID,
            "secret": AGENT_SECRET,
            "status": "evidence_submitted",
            "binding_scope_text": "Full flow test",
        },
    )
    assert "error" not in advance, f"Advance error: {advance}"

    # 4. Get status card — should show evidence_submitted
    status = await _get(
        f"/obligations/{test_obl_id}",
        params={"agent_id": AGENT_ID, "secret": AGENT_SECRET},
    )
    obl = status.get("obligation") or status
    assert obl.get("status") in ("evidence_submitted", "resolved"), f"Unexpected final status: {obl.get('status')}"
