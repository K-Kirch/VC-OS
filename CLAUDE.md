# VC OS — VC Fund Knowledge Hub

## Operating fund

We operate this VC OS for **Byfounders** (placeholder — to be confirmed).
Canonical profile: `funds/europe/denmark/byfounders/brief.md`

All IC-prep fit assessments, fund-fit ratings in `funds/<fund>/brief.md`, and sourcing prioritization dereference through this pointer. Do not duplicate the operating fund's data — link to the canonical files.

## What this workspace is

An internal knowledge base of VC funds across Europe and the USA for operational decisions: syndicating deals, lining up the next round for portfolio companies, and competitive intelligence during live processes.

## Structure

Each fund lives in exactly one folder — the country (Europe) or city hub (USA) of its primary presence:

```
funds/
├── index.md                        # Root — routes to europe/ and usa/
├── _template/                      # Blank templates for new funds
├── europe/
│   ├── index.md                    # All European funds + pan-European routing
│   ├── denmark/
│   │   ├── index.md                # Denmark funds + quick reference by stage
│   │   └── <fund-slug>/
│   │       ├── brief.md            # Start here
│   │       ├── profile.md
│   │       ├── thesis.md
│   │       ├── portfolio.md
│   │       ├── co-investors.md
│   │       ├── team.md
│   │       ├── relationships.md
│   │       └── notes.md
│   └── ... (31 countries)
└── usa/
    ├── index.md                    # All USA funds
    ├── bay-area/
    ├── new-york/
    ├── boston/
    ├── los-angeles/
    └── other/
```

## Geography routing rules

**Primary geography** = where the fund is headquartered = where its folder lives.

**Secondary geographies** = other countries/regions the fund actively invests in. These are listed in `profile.md`. For each secondary geography, add a cross-reference row to that country's `index.md` under **Based Elsewhere, Actively Investing Here** — linking to the fund's primary folder.

No data is duplicated. One folder, one source of truth. Country indexes are routing layers only.

## Fund folder naming

Lowercase kebab-case of the fund's official name: `index-ventures`, `point-nine-capital`, `hv-capital`

## Adding a new fund

1. Determine primary geography → identify the correct country/hub folder
2. Copy `funds/_template/` → `funds/<region>/<country>/<fund-slug>/`
3. Fill `notes.md` first (source list, data quality = 1)
4. Work through: `profile.md` → `thesis.md` → `portfolio.md` → `co-investors.md` → `team.md`
5. Fill `brief.md` last — it synthesises the others
6. Add a row to that country's `index.md` under **Funds Headquartered Here**
7. For each secondary geography in `profile.md`, add a cross-reference row to that country's `index.md` under **Based Elsewhere, Actively Investing Here**

## Reading order for decisions

Always start with `brief.md`. Go deeper only as needed. See `playbooks/` for scenario-specific file sequences.

## Quality standard

Every field must be filled or explicitly marked `Unknown`. The `Conflict?` column in `portfolio.md` must be checked before any portfolio company fundraise conversation.
