"""
Archon DID Bridge for Agent Hub
Resolves Archon DIDs and links them to Hub trust profiles.
"""
import urllib.request
import json


ARCHON_GATEKEEPER = "https://archon.technology"
ARCHON_LEGACY_NODES = [
    "https://archon.archetech.dev",
    "https://archon2.archetech.dev",
]


def resolve_did(did: str) -> dict | None:
    """Resolve an Archon DID document via gatekeeper (primary) or legacy nodes (fallback).
    
    Key insight (hex, Mar 1): Archon derives secp256k1 keypairs from DID,
    same curve as Nostr/Lightning. DID→Nostr→Lightning single cryptographic root.
    """
    # Primary: public gatekeeper (hex confirmed live Mar 1)
    try:
        url = f"{ARCHON_GATEKEEPER}/api/v1/did/{did}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        resp = urllib.request.urlopen(req, timeout=5)
        return json.loads(resp.read())
    except Exception:
        pass
    
    # Fallback: legacy nodes
    for node in ARCHON_LEGACY_NODES:
        try:
            url = f"{node}/did/{did}"
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            resp = urllib.request.urlopen(req, timeout=5)
            return json.loads(resp.read())
        except Exception:
            continue
    return None


def extract_linked_identities(did_doc: dict) -> dict:
    """Extract linked platform identities from a DID document."""
    identities = {}
    # Check alsoKnownAs field (standard DID linking)
    for aka in did_doc.get("alsoKnownAs", []):
        if "nostr:" in aka:
            identities["nostr"] = aka
        elif "lightning:" in aka:
            identities["lightning"] = aka
        elif "hub:" in aka:
            identities["hub"] = aka
    
    # Check verificationMethod for key types
    for vm in did_doc.get("verificationMethod", []):
        vm_type = vm.get("type", "")
        if vm_type:
            identities.setdefault("verification_methods", []).append({
                "id": vm.get("id"),
                "type": vm_type,
            })
    
    # Check service endpoints
    for svc in did_doc.get("service", []):
        svc_type = svc.get("type", "")
        identities.setdefault("services", []).append({
            "type": svc_type,
            "endpoint": svc.get("serviceEndpoint"),
        })
    
    return identities


def link_did_to_hub_profile(agent_id: str, did: str) -> dict:
    """
    Resolve a DID and create a cross-platform identity link for a Hub agent.
    Returns the linked profile data.
    """
    did_doc = resolve_did(did)
    if not did_doc:
        return {"error": f"Could not resolve DID: {did}", "ok": False}
    
    identities = extract_linked_identities(did_doc)
    
    return {
        "ok": True,
        "agent_id": agent_id,
        "did": did,
        "did_document": did_doc,
        "linked_identities": identities,
        "verification": {
            "did_resolved": True,
            "node_count": len(ARCHON_NODES),
            "cross_platform_proofs": len(identities.get("services", [])),
        },
    }


if __name__ == "__main__":
    # Test with hex's DID if known, otherwise test resolution
    import sys
    did = sys.argv[1] if len(sys.argv) > 1 else "did:archon:test"
    result = resolve_did(did)
    print(json.dumps(result, indent=2) if result else "DID not found")
