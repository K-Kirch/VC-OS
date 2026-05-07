# Live Data Integration Strategy

## Overview

To keep fund data current at scale, the VC OS hub needs live data integrations. This document outlines the three integration paths, data source options, and a recommended approach.

---

## Integration Options

### Option 1 — MCP Server (recommended)

Build a custom MCP (Model Context Protocol) server that wraps one or more data sources. Since VC OS is operated via Claude Code — which natively supports MCP — this integrates directly into the workflow with no context switching.

```
Claude Code session
    ↕ MCP Protocol
VC OS MCP Server
    ├── Crunchbase API  ← portfolio, team, fund size
    ├── Dealroom API    ← European coverage (better than Crunchbase for EU)
    └── SQLite cache    ← avoid re-fetching, store last_updated
```

**Tools the server would expose:**

| Tool | Description |
|---|---|
| `search_fund(name, country)` | Find a fund and return structured profile data |
| `get_portfolio(fund_name)` | Return portfolio companies mapped to our schema |
| `get_team(fund_name)` | Return partners and principals |
| `refresh_fund(slug)` | Fetch latest data and write directly to the fund's markdown files |
| `find_funds(stage, sector, geography)` | Discovery queries for new funds to add |

When populating or refreshing a fund, Claude calls the MCP tool and receives live data back — mapped to our schema — rather than relying on training data.

**Pros:** Integrates natively into Claude Code sessions; interactive; works for both initial population and ongoing refresh; extensible
**Cons:** Requires building and hosting the server (~300–500 lines of code)

---

### Option 2 — Scheduled enrichment script

A standalone Python script that runs on a cron schedule (weekly or monthly):

```
funds/*/notes.md
    └── reads last_updated dates
            └── flags stale funds (>90 days)
                    └── fetches from Crunchbase / Dealroom API
                            └── diffs against current markdown
                                    └── updates changed fields + bumps last_updated
```

**Pros:** No infrastructure required; runs headlessly; easy to audit what changed
**Cons:** Not interactive — cannot be queried live during a session; requires separate tooling to trigger

---

### Option 3 — Direct API calls within sessions

Use WebFetch or a Bash script during a Claude Code session to pull from Crunchbase before populating a fund. No build required.

```bash
curl "https://api.crunchbase.com/api/v4/entities/organizations/<fund-slug>" \
  -H "X-cb-user-key: $CRUNCHBASE_KEY" | jq '.properties'
```

**Pros:** Zero build effort; immediate
**Cons:** Manual; no schema mapping; not scaleable for bulk refresh

---

## Data Source Comparison

| Source | EU Coverage | US Coverage | API Access | Cost | Best for |
|---|---|---|---|---|---|
| **Crunchbase** | Good | Excellent | Yes — REST API, well documented | $49–249/mo | Portfolio, funding rounds, team |
| **Dealroom** | Excellent | Limited | Yes — partnership/enterprise tier | €500+/mo | European fund discovery, investor data |
| **PitchBook** | Excellent | Excellent | Yes — enterprise only | Very expensive | Deep research, fund financials |
| **LinkedIn** | Good | Good | Unofficial only | — | Team data, partner backgrounds |
| **Fund websites** | Source of truth | Source of truth | Scraping only | Free | Thesis, current team |

---

## Recommendation

**Build the MCP server backed by Crunchbase as the primary source**, with fund website scraping as fallback for thesis and team data that Crunchbase does not cover well. Add Dealroom later if Crunchbase coverage proves insufficient for European funds.

**Why MCP over the alternatives:**
1. Integrates directly into Claude Code — live data flows into the session with no manual steps
2. Handles both initial population and ongoing refresh from the same interface
3. Extensible — additional sources (Dealroom, LinkedIn) can be added without changing the workflow
4. The schema mapping layer lives in the server, keeping fund files clean

---

## Build Specification (when ready)

**Stack:** Python or Node.js
**Primary data source:** Crunchbase REST API
**Caching:** SQLite (keyed by fund slug + date, TTL 7 days)
**Schema mapping:** Crunchbase fields → VC OS fund schema fields
**Hosting:** Local (dev) or small VPS (production)
**Configuration:** API key via environment variable (`CRUNCHBASE_KEY`)

**Required before build:**
- Crunchbase API key (Basic tier sufficient to start)
- Decision on language: Python or Node.js
