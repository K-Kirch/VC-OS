# Fund Population Strategy

## Overview

Populating the VC OS knowledge hub at scale requires a tiered approach. This document outlines the strategy, effort estimates, and recommended sequencing.

---

## Tiers

### Tier 1 — Manual AI research (~200 funds, quality 3–4)
The funds most likely to appear in real decisions. Populated by Claude from training data, then spot-checked by a human against live sources.

### Tier 2 — Semi-automated (~800 funds, quality 2–3)
Structured data from a source export (Crunchbase, Dealroom, PitchBook) feeds `profile.md`. Claude then fetches each fund's website to fill `thesis.md` and partial `portfolio.md`.

### Tier 3 — Stub only (~2,000+ funds, quality 1)
Name, country, website, stage — nothing more. Exists in the index as a known entity, ready to be enriched when relevant.

---

## Manual Population — Effort Estimate

### What Claude can produce from memory (no live web fetching)

| File | Quality | Reliable | Needs verification |
|---|---|---|---|
| `profile.md` | 2–3 | Stage, sectors, HQ, rough check size | Exact fund size, current fund number, deployment status |
| `thesis.md` | 3–4 | Investment philosophy, what they look for, key quotes | Recent shifts in thesis |
| `portfolio.md` | 2–3 | Notable companies, major exits | Investments since ~mid-2025, failed companies |
| `co-investors.md` | 3 | Frequent patterns, syndication style | Recent relationship changes |
| `team.md` | 2 | Senior GPs | Partner departures/arrivals since ~mid-2025 |
| `brief.md` | 3 | Fit ratings, competitive positioning | Deployment status, dry powder |

> Knowledge cutoff: August 2025. Anything after that requires human verification or live data sources.

### Scale breakdown

| Region | Priority Funds | Sessions (8/session) |
|---|---|---|
| Denmark | 8 | 1 — done |
| United Kingdom | ~15 | 2 |
| Germany | ~12 | 2 |
| Sweden | ~8 | 1 |
| France | ~8 | 1 |
| Rest of Europe | ~20 | 3 |
| USA Tier 1 | ~25 | 3–4 |
| USA Tier 2 | ~30 | 4 |
| **Total** | **~120** | **~17 sessions** |

Each session: ~10–15 minutes of clock time.

### Human review required after each batch

- Verify deployment status (active / raising / between funds)
- Spot-check fund sizes against Crunchbase or fund website
- Add portfolio companies announced after mid-2025
- Fill `team.md` gaps — partner moves are the fastest-moving data
- Fill `relationships.md` entirely — always user-specific

Estimated effort: 5–10 minutes per fund × 120 funds = 10–20 hours total.

---

## Semi-Automated Pipeline (Tier 2)

```
Source export (CSV from Dealroom / Crunchbase)
    └── stub-creator script
            └── fund folder + notes.md + profile.md (structured fields only)
                    └── per-fund enrichment (Claude fetches website)
                              └── thesis.md, partial team.md, partial portfolio.md
                                        └── manual review + brief.md
```

### Recommended data sources

| Source | Coverage | Cost | Best for |
|---|---|---|---|
| Dealroom | European VC — comprehensive | ~€500+/mo or one-off export | Europe Tier 2–3 discovery |
| Crunchbase | Global, US strongest | $49–249/mo | USA + Europe discovery |
| PitchBook | Most comprehensive, US-heavy | Enterprise pricing | Tier 1 deep research |
| Fund websites | Ground truth for thesis/team | Free | AI enrichment pass |
| LinkedIn | Team data | Free (manual) | `team.md` enrichment |

---

## Data Freshness

VC data goes stale fast — fund status, team composition, and portfolio all change regularly.

- Every fund file has `last_updated` in `notes.md` — flag anything older than 6 months
- Tier 1 funds: quarterly refresh pass (re-fetch website, check for team/portfolio changes)
- Tier 2–3 funds: refresh only when the fund becomes operationally relevant
- `relationships.md` stays evergreen — update after every real interaction

---

## Recommended Sequencing

1. **UK and Germany** — next two batches (highest interaction frequency for most European VCs)
2. **Sweden, France, Netherlands** — complete the core Western European markets
3. **USA Tier 1** — top 25 US funds that actively invest in or co-invest with European companies
4. **Rest of Europe** — fill remaining countries
5. **USA Tier 2** — broader US coverage
6. **Stub creator script** — automate Tier 3 from a Dealroom/Crunchbase export
