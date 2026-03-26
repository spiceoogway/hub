#!/usr/bin/env python3
import json, re, subprocess
from datetime import datetime, UTC
from pathlib import Path
repo = Path(__file__).resolve().parents[1]
source = repo / "hub_mcp.py"
text = source.read_text()
lines = text.splitlines()

def collect(decorator_prefix: str):
    names = []
    for i, line in enumerate(lines):
        if line.strip().startswith(decorator_prefix):
            for j in range(i + 1, min(i + 8, len(lines))):
                m = re.match(r"async def\s+([A-Za-z_][A-Za-z0-9_]*)\(", lines[j].strip())
                if m:
                    names.append(m.group(1))
                    break
    return names

tools = collect("@mcp.tool")
resources = collect("@mcp.resource")
source_blob_sha = subprocess.check_output(["git", "-C", str(repo), "hash-object", str(source)]).decode().strip()
out = {
    "source_commit_sha": source_blob_sha,
    "source_file": "hub_mcp.py",
    "source_commit_semantics": "git blob sha of hub_mcp.py (stable across artifact-only commits)",
    "verification_semantics": {
        "stable_fields": [
            "source_commit_sha",
            "source_file",
            "source_commit_semantics",
            "tool_count",
            "resource_count",
            "tools",
            "resources"
        ],
        "non_verifying_fields": ["generated_at_utc"]
    },
    "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "tool_count": len(tools),
    "resource_count": len(resources),
    "tools": tools,
    "resources": resources,
}
(repo / "hub_mcp_surface.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
