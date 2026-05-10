# Sweden — Fund Discovery Working Document

<!-- Working document — not a canonical fund file. Use this to track research, add missing funds, and plan population. -->
<!-- Last updated: 2026-05-10 -->

---

## Status

| Category | Count |
|---|---|
| Fully populated (quality 3–4) | 5 — Creandum, EQT Ventures, EQT Growth, Luminar Ventures, Polar Structure |
| Populated (quality 1–2) | 3 — Ampli Ventures (Q2), STOAF (Q2), Greens Ventures (Q1) |
| Cross-referenced from other countries | 4 |
| Confirmed missing, not yet added | ~26 |
| New candidates from Layer 1 (SVCA), pending verification | 18 |
| Layer 7 candidates populated this session | 5 ✓ |
| Family offices identified (out-of-scope for fund folders) | 2 — Lundin, Stena |
| Geography unverified (may be cross-refs) | 1 |
| User-identified missing fund | TBD — confirm whether one of the Layer 7 finds matches |

---

## Discovery Methodology — 7-Layer Playbook

The canonical approach for identifying every active VC fund in Sweden. Run layers sequentially; each builds the master candidate list. Layer 7 is the final completeness check.

### Layer 1 — Authoritative registries (ground truth)

Legally-mandated lists. Aggregators derive from these but lag.

| Source | Yields |
|---|---|
| Finansinspektionen — AIFM register | Every licensed/registered Alternative Investment Fund Manager in Sweden |
| SVCA — Swedish Private Equity & VC Association member directory | Self-declared active VC/PE houses; catches recent joiners |
| Bolagsverket — entities with SNI code 64.302 (venture capital activity) | Legally-registered VC entities; catches micro/solo GPs |
| Invest Europe member directory (filter: Sweden) | Pan-European cross-check |

### Layer 2 — Aggregator triangulation (breadth)

Already run: Gilion, Seedtable, Shizune. Add:

- Dealroom.co — strongest Nordic coverage; filter HQ=Sweden + active status
- Crunchbase Pro — filter Investor Type=VC, HQ=Sweden, Last Investment ≤18mo
- Tracxn / PitchBook — better LP/GP data if accessible
- Nordic 9 — Nordic-specific; catches what global aggregators miss

### Layer 3 — Network harvesting (long tail)

Funds missed by aggregators usually appear as co-investors.

1. Extract co-investors from every populated fund's `portfolio.md`; filter to Sweden-HQ
2. Scrape Swedish funding rounds (24mo) — Breakit, Di Digital, Dagens Industri (Swedish trade press names local investors aggressively); Sifted, TechCrunch EU, EU-Startups for English
3. Pull Almi Invest + Saminvest co-investment partner lists; Saminvest LP positions are public and reveal new GPs

### Layer 4 — Ecosystem signals (catches the very new)

- New-fund-close press releases 2024–2026: Sifted, Breakit, Dagens Industri, EU-Startups
- Sting, Norrsken House, Antler Stockholm investor day decks / partner lists
- LinkedIn structured search: "General Partner" / "Managing Partner" + Stockholm/Gothenburg/Malmö, posts last 12mo
- EIF (European Investment Fund) Sweden commitments — public LP positions reveal new institutional GPs

### Layer 5 — Active-status filter

Apply uniformly. "Active" = at least one of:
- Made ≥1 new investment in trailing 18 months
- Closed a fund vehicle in trailing 36 months

Drops dormant vehicles, wound-down funds, family offices not deploying.

### Layer 6 — Reconciliation + dedupe

Merge all candidate lists into one working table:

| Fund | Sources confirming | HQ verified | Active (Y/N + evidence) | Status |
|---|---|---|---|---|

- ≥2 sources → high confidence, queue for population
- 1 source → verification pass (website + recent deal)
- Cross-check against existing folder + cross-ref list

### Layer 7 — Cap-table cross-referencing (Sweden-specific final check)

Sweden's company-law transparency means every fund that ever cut a check into a Swedish AB leaves a public fingerprint. Run **after** Layers 1–6 as the completeness check.

**Method:**

1. Build seed list — 200–300 Swedish startups with disclosed rounds in trailing 24 months (Dealroom, Breakit, Crunchbase)
2. Pull shareholder data per startup — Allabolag.se, Ratsit (free, aggregate Bolagsverket); Roaring.io / Vainu if premium budget; Bolagsverket annual reports as backup
3. Filter shareholders → investor candidates — keep legal-name patterns: `Capital`, `Ventures`, `Invest`, `Fund`, `Partners`, `VC`, `Holding`, `Equity`. Flag entities appearing on ≥2 cap tables → systematic investor
4. Resolve SPV → fund brand — VC legal entities often differ from market name (e.g., `Creandum Advisor AB` → Creandum). Build resolution map; manually verify ambiguous cases
5. Cross-reference against master list — entities on cap tables but absent from Layers 1–6 = discovery yield

**What this catches that earlier layers miss:**
- Funds with no website or marketing
- Solo GPs operating via holding company
- Family offices deploying like VCs (≥2 startup investments) but not in any VC list
- Foreign funds using Swedish SPVs (Sweden-active cross-ref candidates)
- Stealth funds that haven't announced

**Caveats:**
- Reporting lag — annual reports filed ~6–7mo after fiscal year end; most recent rounds may not yet show
- SPV obfuscation — some funds use one-off SPV per investment; resolution layer is manual
- Signal ≠ active — combine with Layer 5 filter (presence in 2021 ≠ still deploying)

---

## Layer 1 Results — 2026-05-10

### Sources

| Source | Status |
|---|---|
| SVCA Ordinary Members (`svca.se/ordinarie-medlemmar`) | ✓ Extracted — 31 VC + 7 Growth + 28 Buyout + 1 Infra + 6 LP |
| Finansinspektionen AIFM register (`fi.se` Company Register) | ⚠ Deferred — interactive advanced-search only; no list URL. Run dedicated query session per AIFM category |
| Invest Europe members (`investeurope.eu/about-us/members`) | ⚠ Deferred — 403 on public fetch; likely auth-gated |
| Bolagsverket SNI 64.302 | ⏭ Skipped — paid query interface; covered by Allabolag.se in Layer 7 |

### New Sweden candidates surfaced by SVCA — 18 funds

Not present in any prior discovery list. Verify HQ + active status (Layer 5) before promoting to Confirmed Missing tiers.

| Fund | Website | First-pass note |
|---|---|---|
| Backstage Invest | https://backstage.se | Generic VC |
| Butterfly Ventures | https://butterfly.vc | Verify HQ — likely Finland |
| Curitas Ventures | https://curitasventures.com | Generic VC |
| Eir Ventures | https://eirventures.eu | Likely life-sciences (Eir = Norse healing) |
| Endeit Capital | https://endeit.com | Verify HQ — likely Netherlands |
| First Venture | https://first-venture.se | Generic VC |
| Goose Valley Ventures | https://goosevalley.vc | Generic VC |
| GU Ventures | https://guventures.com | Gothenburg University tech transfer |
| Inception Fund | https://inceptionfund.vc | Generic VC |
| Ingka GreenTech | https://ingka.com/what-we-do/ingka-investments | IKEA/Ingka CVC — climate |
| Klint Ventures | https://klintventures.com | Generic VC |
| Node Ventures | https://node.vc | Generic VC |
| Nordic Game Ventures | https://nordicgameventures.com | Gaming specialist |
| Norrsken Accelerator | https://accelerator.norrsken.org | Distinct from Norrsken VC (T1) |
| Oxx | https://oxx.vc | Generic VC — verify SaaS focus |
| Rymdkapital | https://rymdkapital.se | "Rymd" = space; verify space-tech focus |
| Segulah Medical Acceleration | https://segulahmedical.com | Medtech specialist |
| SLU Holding | https://slu.se/sluholding | SLU (agriculture) tech transfer |

### Cross-references confirmed Sweden-active by SVCA membership

| Fund | Primary HQ | Action |
|---|---|---|
| Alliance Venture | Oslo | Promote from "Geography Unverified" → Norway primary, Sweden cross-ref confirmed |
| Antler | Singapore | Promote from "Geography Unverified" → Singapore primary, Sweden cross-ref confirmed |
| Northzone Ventures | London | Already cross-referenced — confirmed |
| Verdane (Growth) | Oslo | Promote from "Geography Unverified" → Norway primary, Sweden cross-ref confirmed |

### Confirmed Missing tier candidates corroborated by SVCA

Almi Invest (T1), Industrifonden (T1), HealthCap (T2), Spintop Ventures (T2), Chalmers Ventures (T3), Course Corrected (T3), Fairpoint Capital (T3), Navigare Ventures (T3) — all confirmed as active SVCA members.

### Notable absences from SVCA (still confirmed missing via other sources)

Norrsken VC, Kinnevik, Wellstreet, BackingMinds, J12 Ventures, NFT Ventures, Pale Blue Dot, Peak Capital, Inbox Capital, Prima Materia, Icebreaker.vc, Brightly Ventures, Nordic Makers, VNV Global, Bonnier Capital, SEB Venture Capital, H&M Group Ventures, Sting Capital, GP Bullhound, Sciety, VEF, Partnerinvest Norr, Flat Capital → SVCA membership is partial; multi-source approach validated.

### Layer 1 sub-tasks

1. Verify HQ for Butterfly Ventures, Endeit Capital → cross-ref vs Sweden-HQ
2. Run Finansinspektionen advanced-search session across AIFM categories (Authorisation, Registration, EEA-based, etc.)
3. Resolve Invest Europe access — or accept SVCA as sufficient cover
4. Apply Layer 5 active-status filter to all 18 new candidates before promoting

---

## Layer 7 Results — 2026-05-10 (Cap-Table Cross-Reference — Initial Pass)

### Method

Direct extraction from funding-round announcements and trade press, prioritizing 2025–2026 Swedish rounds across sectors. Each cap table inspected for Sweden-HQ investors not already in the master list. Bypasses aggregator lag and SPV obfuscation.

### Cap tables reviewed (9 rounds)

| Startup | Round | Date | Size | Sector |
|---|---|---|---|---|
| Pit | Seed | May 2026 | $16M | AI |
| Lovable | Series A | Jul 2025 | $200M | AI / vibe-coding |
| Lovable | Series B | Dec 2025 | $330M | AI / vibe-coding |
| Endra | Seed | Dec 2025 | $20M | AI / building MEP |
| Tzafon | Pre-seed | Jul 2025 | €8.3M | AI / interface-less |
| Kovant | Pre-seed | Nov 2025 | €1.5M | AI / supply chain |
| Legora | Series C | Oct 2025 | $150M | Legal AI |
| Einride | Series D | Oct 2025 | $100M | Autonomous trucking |
| AlixLabs | Series A | Nov 2025 | €14.1M | Semiconductor (Lund) |

### NEW Sweden-HQ entities surfaced — 5 funds + 2 family offices

| Entity | Type | Notes | Source cap table |
|---|---|---|---|
| **Ampli Ventures** | VC fund | Stockholm, est 2022, B2B SaaS, €1–5M ticket, Seed/Series A | Kovant |
| **Greens Ventures** | VC fund | Stockholm, est 2021, Spotify alumni; Dan McCormick GP; Nordic pre-seed for Nordic-Unicorn-alumni founders | Kovant |
| **EQT Growth** | Growth fund | Stockholm, EQT Group sister-vehicle to EQT Ventures; $2.27B; €50–200M tickets | Lovable Series B |
| **Polar Structure** | Evergreen investor | Stockholm, infrastructure / green-transition; co-invests with VCs (railways, charging, energy storage) | Einride |
| **STOAF** (Stockholm Business Angels) | Angel group | Stockholm, est 2008; tech + medtech; SVCA member (associate tier — not on ordinary list) | AlixLabs |
| **Lundin** family office | Family office | Swedish industrial dynasty; verify formal vehicle name (Nemesia? Lundin Investments?) | Pit |
| **Stena** (likely Stena Sessan) | Family office | Already on SVCA Growth list — corroborated as venture-active | Pit |

### Sweden-active foreign funds (potential cross-refs)

| Fund | Primary HQ | Cap table |
|---|---|---|
| 20VC | London | Lovable A |
| Hummingbird | London | Lovable A |
| Notion Capital | London | Endra |
| HV Capital | Munich | Tzafon |
| Visionaries Club | Berlin | Lovable A |
| Evantic | London | Lovable B |

### Architecture question — EQT Group

EQT operates two distinct VC/growth vehicles from Stockholm:
- **EQT Ventures** (already in folder) — early/seed/growth-stage VC, €1.1B Fund III
- **EQT Growth** (new discovery) — growth-stage, $2.27B, €50–200M tickets, separate team

Recommend: add `eqt-growth/` as sibling folder to `eqt-ventures/`. Different mandate, team, fund vehicle. Awaiting user decision before structuring.

### Layer 7 sub-tasks

1. Run ~10 more cap tables for completeness (Voi, Klarna recent, Northvolt, Truecaller, Mentimeter, Anyfin, Juni, Tibber, Volta Greentech, Stegra/H2 Green Steel) — diminishing returns expected
2. Verify Lundin family office vehicle name (Nemesia? Lundin Investments?)
3. ✓ **Done 2026-05-10** — All 5 fund candidates populated as fund folders (Ampli, Greens, EQT Growth, Polar Structure, STOAF). See "Currently in Folder" table for quality levels.
4. ✓ **Done 2026-05-10** — EQT Growth created as sibling folder to `eqt-ventures/`; cross-referenced in both `notes.md` files.

### Validation of Layer 7 thesis

Ampli Ventures and Greens Ventures are both Stockholm-HQ VCs founded in 2021–2022, actively deploying — and **absent from Gilion, Seedtable, Shizune, AND SVCA Layer 1**. They surfaced only via cap-table cross-reference. Confirms cap-table scraping is the highest-leverage discovery layer for Sweden, especially for funds <5 years old.

---

## Currently in Folder

| Fund | Quality | Notes |
|---|---|---|
| [Ampli Ventures](ampli-ventures/brief.md) | 2 | Layer 7 find (Kovant cap table); website + team scraped; fund size unknown |
| [Creandum](creandum/brief.md) | 4 | Full team + 152-company portfolio [S] |
| [EQT Growth](eqt-growth/brief.md) | 3 | Layer 7 find (Lovable cap table); €2.2B Fund I; 4 partners + 25+ team |
| [EQT Ventures](eqt-ventures/brief.md) | 3 | SPA — homepage only; team/portfolio [M] |
| [Greens Ventures](greens-ventures/brief.md) | 1 | Layer 7 find (Kovant cap table); minimal website; 1 person publicly identified |
| [Luminar Ventures](luminar-ventures/brief.md) | 4 | Full scrape [S] |
| [Polar Structure](polar-structure/brief.md) | 3 | Layer 7 find (Einride cap table); evergreen infra investor; 16-person team scraped |
| [STOAF](stoaf/brief.md) | 2 | Layer 7 find (AlixLabs cap table); Stockholm angel collective est. 2008; 4 GPs + 6 advisors |

## Cross-Referenced Here (Primary Folder Elsewhere)

| Fund | Primary Folder | Notes |
|---|---|---|
| Northzone | europe/united-kingdom/northzone | London HQ, Nordic roots |
| Inventure | europe/finland/inventure | Helsinki HQ, Sweden secondary |
| byFounders | europe/denmark/byfounders | Copenhagen HQ |
| Heartcore Capital | europe/denmark/heartcore-capital | Copenhagen HQ — confirm Sweden cross-ref added |

---

## Confirmed Missing — Sweden HQ

Sourced from: Gilion VC Mapping, Seedtable, Shizune, manual research (2026-05-10).

### Tier 1 — Populate First

| Fund | Website | Stage | Sector | Notes |
|---|---|---|---|---|
| Industrifonden | https://industrifonden.com | Seed–Series B | Generalist | Major semi-public fund; very active in Swedish ecosystem |
| Norrsken VC | https://norrsken.org/norrskenvc | Pre-Seed–Series C | Impact / Generalist | €320M Fund II closed 2024; co-founded by Niklas Adalberth (Klarna) |
| Kinnevik | https://kinnevik.com | Series A–E | Consumer, Health, Fintech | Listed investment company; major growth-stage presence |
| Almi Invest | https://almi.se/almi-invest | Pre-Seed–Seed | Generalist | Government-backed; regional offices across Sweden |

### Tier 2 — Active, Well-Known

| Fund | Website | Stage | Sector | Notes |
|---|---|---|---|---|
| Spintop Ventures | https://spintopventures.com | Pre-Seed–Series A | Generalist | Nordic seed fund |
| J12 Ventures | https://j12ventures.com | Pre-Seed–Seed | Generalist | Active Stockholm seed fund |
| NFT Ventures | https://nftventures.com | Seed–Series B | Fintech | One of Sweden's earliest fintech-specialist VCs (est. 2014) |
| Wellstreet | https://wellstreet.se | Seed | Generalist | Innovation ecosystem + fund, Stockholm |
| BackingMinds | https://backingminds.com | Pre-Seed–Seed | Generalist | Diversity-focused; €50M Fund II (2022); Nordics mandate |
| Flat Capital | https://flatcapital.com | Pre-Seed+ | Generalist | Chris Pavlovski's fund |
| Pale Blue Dot | https://paleblue.vc | Pre-Seed–Series A | Climate Tech | Climate specialist; well-regarded |
| Peak Capital | https://peak.capital | Pre-Seed–Series B | Generalist | Active seed/Series A fund |
| HealthCap | https://healthcap.eu | Seed–Series C | Biotech, Healthtech | Long-established biotech specialist |
| Inbox Capital | https://inboxcap.com | Seed–Series B | B2B SaaS | SaaS focus |
| Prima Materia | https://primamateria.com | Series A–B | Climate, Health, AI | Recent fund; climate/deep tech focus |
| Icebreaker.vc | https://icebreaker.vc | Seed–Series A | — | Verify stage and sector |
| Brightly Ventures | https://brightlyventures.com | Seed | — | Newer fund; verify details |
| Nordic Makers | https://nordicmakers.vc | Pre-Seed–Series B | Generalist | Active angel/micro-VC network |
| VNV Global | https://vnv.global | Series A–D | Generalist | Listed investment company; growth stage |

### Tier 3 — Corporate / Specialist / Smaller

| Fund | Website | Stage | Sector | Notes |
|---|---|---|---|---|
| Bonnier Capital | https://bonnierventures.com | Seed–Series B | Media, Consumer, Tech | Bonnier Group CVC; inv. since 2016 |
| SEB Venture Capital | https://seb.se/venturecapital | Seed–Series A | Fintech, Deep Tech | SEB bank CVC |
| H&M Group Ventures | https://hmgroupventures.com | Series A–B | Sustainability, Fashion Tech | H&M Group CVC |
| Sting Capital | https://stingcapital.com | Pre-Seed–Seed | Generalist | Linked to Sting accelerator, Stockholm |
| GP Bullhound | https://gpbullhound.com | Growth | Tech | Also M&A advisory; verify VC activity |
| Navigare Ventures | https://navigareventures.com | Seed–Series A | — | Verify details |
| Fairpoint Capital | https://fairpoint.se | — | — | Verify details |
| Course Corrected | https://cc.vc | Seed | — | Recent fund; verify details |
| Sciety | https://sciety.com | — | — | Recent; verify details |
| VEF | https://vef.vc | Series A–B | Fintech | Listed; emerging markets fintech |
| Chalmers Ventures | https://chalmersventures.com | Pre-Seed | Deep Tech | University-linked (Chalmers); Gothenburg |
| Partnerinvest Norr | https://partnerinvestnorr.se | Seed | Generalist | Regional government fund; Northern Sweden |

---

## Geography Unverified — May Be Cross-References

These appeared in Sweden fund lists but primary HQ may be elsewhere:

| Fund | Likely HQ | Action |
|---|---|---|
| Antler | Singapore (Stockholm office) | Cross-ref if Sweden active; primary in Singapore folder |
| Cherry Ventures | Berlin | Cross-ref if Sweden active; primary in Germany folder |
| Verdane | Oslo | Cross-ref if Sweden active; primary in Norway folder |
| NordicNinja VC | Japan-backed, Helsinki/Stockholm | Verify HQ — may go in Finland or Sweden |
| Alliance Venture | Oslo | Cross-ref if Sweden active; primary in Norway folder |

---

## User-Identified Missing Fund

**Status: UNKNOWN** — user confirmed at least one recent fund is missing from all lists above.

→ Add fund name and URL here once identified, then scrape and populate.

| Fund | Website | Notes |
|---|---|---|
| ??? | ??? | User-identified; not found in any aggregator source |

---

## Population Queue

Priority order for next scraping session:

1. Industrifonden
2. Norrsken VC
3. Kinnevik
4. Almi Invest
5. BackingMinds
6. Pale Blue Dot
7. J12 Ventures
8. Spintop Ventures
9. NFT Ventures
10. Peak Capital
11. HealthCap
12. Flat Capital
13. Nordic Makers
14. Inbox Capital
15. Prima Materia
16. Icebreaker.vc
17. Brightly Ventures
18. Wellstreet
19. Bonnier Capital
20. SEB Venture Capital
21. VNV Global

---

## Sources Used

- https://vc-mapping.gilion.com/venture-capital-firms/sweden (fetched 2026-05-10)
- https://www.seedtable.com/investors-sweden (fetched 2026-05-10)
- https://shizune.co/investors/vc-funds-sweden (fetched 2026-05-10)
- WebSearch: "new venture capital fund Sweden launched 2023 2024 2025" (2026-05-10)
- WebSearch: "BackingMinds Wellstreet Bonnier Ventures NFT Ventures Sweden VC" (2026-05-10)
- https://www.svca.se/ordinarie-medlemmar/ (Layer 1, fetched 2026-05-10)
- https://www.fi.se/en/our-registers/company-register/ (Layer 1 — interactive search, deferred 2026-05-10)
- https://investeurope.eu/about-us/members (Layer 1 — 403, deferred 2026-05-10)
