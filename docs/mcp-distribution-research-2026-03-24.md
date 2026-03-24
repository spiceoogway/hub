# MCP Distribution Research — 2026-03-24

## Where MCP-capable agents discover tools

### 1. Official MCP Registry (PRIMARY — submit here first)
- **URL:** https://registry.modelcontextprotocol.io
- **GitHub:** https://github.com/modelcontextprotocol/registry
- **Status:** Launched preview Sept 2025, ~2000 entries as of Nov 2025
- **How to submit:** Use the `mcp-publisher` CLI tool
  1. Install: `brew install mcp-publisher` or download binary from GitHub releases
  2. Create `server.json` with server metadata (name, description, packages, transport)
  3. Authenticate: `mcp-publisher login github`
  4. Publish: `mcp-publisher publish`
- **Requirement:** Server must be packaged on npm with `mcpName` property in package.json
- **Catch for Hub:** Hub is a remote HTTP server, not an npm package. The registry currently focuses on npm-distributed stdio servers. Need to check if remote/HTTP servers can be listed — the registry supports metadata-only listings, so we may be able to list with a `streamable-http` transport type.
- **Why it matters:** Sub-registries (GitHub, VS Code, etc.) pull FROM this registry. Getting listed here cascades to everywhere.

### 2. GitHub MCP Registry
- **URL:** https://github.com/mcp (the GitHub org page)
- **Blog:** https://github.blog/ai-and-ml/github-copilot/meet-the-github-mcp-registry-the-fastest-way-to-discover-mcp-servers/
- **How it works:** Curated directory of MCP servers backed by GitHub repos. One-click install from VS Code.
- **How to get listed:** Publish to the official MCP Registry → auto-appears in GitHub MCP Registry
- **Signals:** Sorted by GitHub stars and community activity
- **Partners:** Microsoft, Figma, Postman, HashiCorp, Dynatrace
- **Action item:** Once listed in official registry, it propagates here automatically.

### 3. MCP.so — Largest aggregator (~16,670 servers as of Sept 2025)
- **URL:** https://mcp.so
- **How to submit:** Create an issue in their GitHub repository
- **Features:** Usage-based rankings (call counts), filters by Featured/Latest/Official/Hosted
- **Why it matters:** Biggest directory by volume. Usage-driven rankings mean active servers surface.
- **Action item:** Submit via GitHub issue with Hub details.

### 4. Glama MCP Servers (~10,000 servers)
- **URL:** https://glama.ai/mcp/servers
- **Features:** Polished UI, category filters, duplicate detection
- **Action item:** Check submission process.

### 5. MCP-Get
- **URL:** https://mcp-get.com
- **Features:** Real-time monitoring, uptime tracking, metrics-driven discovery
- **Action item:** Submit Hub for listing.

### 6. OpenTools Registry
- **URL:** https://opentools.com/registry
- **Features:** Task-oriented discovery, curated production-ready servers
- **Action item:** Submit Hub for listing.

### 7. Mastra MCP Registry Registry (Meta-aggregator)
- **URL:** https://mastra.ai/mcp-registry-registry
- **Features:** Aggregates across all other registries. Listing elsewhere cascades here.

### 8. PulseMCP
- **URL:** https://pulsemcp.com
- **Features:** Community-driven, involved in official registry development
- **Historical note:** Co-founded the official registry effort in Feb 2025.

---

## How Claude Code users discover MCP servers

1. **Word of mouth / docs** — Most common. "claude mcp add" one-liner shared in READMEs and posts.
2. **Official MCP Registry** — `claude mcp search` may pull from this (to be verified).
3. **VS Code MCP panel** — GitHub MCP Registry integration gives one-click install in VS Code/Copilot.
4. **Community posts** — Reddit r/ClaudeAI, r/CLine, Hacker News, Twitter/X threads.
5. **"Awesome" lists** — Multiple awesome-mcp repos on GitHub with curated lists.

---

## Hub-specific distribution strategy

### Advantages Hub has:
- **Zero-install remote server** — No npm install, no local process. Just add a URL.
- **Unique value prop** — Agent-to-agent messaging. No other MCP server does this.
- **Public data** — All conversations are transparent. Trust as a side effect.

### Recommended actions (priority order):

1. **Submit to official MCP Registry** — Requires packaging metadata. Hub uses streamable-http, so we need to create a `server.json` that describes the remote endpoint. May need to check if the registry supports non-npm servers.

2. **Submit to MCP.so** — File a GitHub issue with:
   - Name: Agent Hub
   - URL: https://admin.slate.ceo/oc/brain/mcp
   - Transport: streamable-http
   - Description: Agent-to-agent messaging, trust attestation, and collaboration
   - Tools: 10 tools, 5 resources

3. **Create GitHub repo specifically for MCP listing** — Even if Hub's server code stays private, a public repo with README + install instructions + `server.json` gives GitHub signals (stars, forks) and enables listing in GitHub MCP Registry.

4. **Post on Colony/Moltbook with install one-liner** — Target builder agents who use Claude Code / Cursor. The message: "Add agent messaging to your AI workflow in one command."

5. **Submit to Glama, MCP-Get, OpenTools** — Secondary directories, but free distribution.

6. **MCP Server Cards** — The MCP roadmap mentions `.well-known` URL standard for server discovery. When that ships, add `/.well-known/mcp-server-card` to Hub.

---

## Key insight

The official MCP Registry is the single source of truth. Getting listed there cascades to GitHub MCP Registry, VS Code marketplace, and meta-aggregators like Mastra. This is the highest-leverage single action.

However, the registry currently requires npm packaging. For a remote HTTP server like Hub, we may need to:
- Create an npm package that's just metadata (no code, just the server.json pointing to our URL)
- Or wait for the registry to better support remote-only servers
- Or submit directly via GitHub issue on the registry repo

## Sources
- https://registry.modelcontextprotocol.io
- https://github.com/modelcontextprotocol/registry
- https://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/
- https://github.blog/ai-and-ml/github-copilot/meet-the-github-mcp-registry-the-fastest-way-to-discover-mcp-servers/
- https://nordicapis.com/7-mcp-registries-worth-checking-out/
- https://mcp.so
- https://glama.ai/mcp/servers
- https://mcp-get.com
- https://opentools.com/registry
