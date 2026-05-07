# Fund Schema — Canonical Field Definitions

All fund files must conform to these definitions. Use exact field names. Mark unknown values as `Unknown`.

---

## brief.md fields

**Read this first.** Synthesizes all other files into a 60-second scan.

| Field | Type | Description |
|---|---|---|
| `stage` | list | Investment stages — from taxonomy (e.g. Seed, Series A) |
| `sectors` | list | Sector focus — from taxonomy |
| `check_size` | string | Initial check range (e.g. €500K – €3M) |
| `primary_geography` | string | Single country where the fund is headquartered and primarily invests — determines folder location |
| `secondary_geographies` | list | Other countries/regions where the fund actively invests — drives cross-referencing in those country indexes |
| `deployment_status` | enum | Active / Raising New Fund / Between Funds / Unknown |
| `lead_or_follow` | enum | Lead / Follow / Either |
| `intro_preference` | enum | Warm intro only / Cold email OK / Apply online |
| `tldr` | paragraph | 3 lines: who they are, what they're known for, why they matter |
| `fit_syndication` | enum | High / Medium / Low / Unknown |
| `fit_next_round` | enum | High / Medium / Low / Unknown |
| `compete_on` | string | What they lead with when competing for deals |
| `their_weakness` | string | What founders say they lack |
| `differentiate` | string | How to position against them |
| `portfolio_conflicts` | table | Your portfolio co vs. their portfolio co — with conflict level |
| `best_entry_point` | string | Tactical note on how to approach |
| `partner_summary` | table | One line per partner: stage/sector focus, style, best use |

---

## profile.md fields

| Field | Type | Description |
|---|---|---|
| `stage` | list | From taxonomy: Pre-Seed, Seed, Series A, Series B, Growth |
| `sectors` | list | From taxonomy sectors list |
| `primary_geography` | string | Single country — determines which country folder the fund lives in |
| `secondary_geographies` | list | Other countries where the fund actively invests — add a cross-reference row to each of those country indexes |
| `check_size_min` | string | Minimum initial check (e.g. €500K) |
| `check_size_max` | string | Maximum initial check |
| `ownership_target` | string | Typical ownership sought (e.g. 10–20%) |
| `lead_or_follow` | enum | Lead / Follow / Either |
| `fund_number` | string | Current fund (e.g. Fund IV) |
| `current_fund_size` | string | Size with currency (e.g. €400M) |
| `total_aum` | string | Total AUM across all vehicles |
| `deployment_status` | enum | Active / Raising New Fund / Between Funds / Unknown |
| `founded` | year | Year the fund was founded |
| `hq` | string | City, Country |
| `other_offices` | list | Other office locations |
| `intro_preference` | enum | Warm intro only / Cold email OK / Apply online |
| `pitch_email` | string | Cold pitch email if public |
| `application_url` | url | Online application form if exists |
| `website` | url | Fund website |
| `linkedin` | url | LinkedIn company page |
| `twitter` | string | @handle |
| `description` | paragraph | 2–3 sentence plain-English description |

---

## thesis.md fields

| Field | Type | Description |
|---|---|---|
| `thesis_summary` | paragraph | Core investment thesis in 3–5 sentences |
| `stage_rationale` | paragraph | Why they focus on their chosen stage(s) |
| `sector_rationale` | paragraph | Why they focus on their chosen sectors |
| `what_they_look_for` | list | Specific founder/company traits they prioritize |
| `what_they_avoid` | list | Explicit anti-portfolio criteria |
| `decision_speed` | string | Typical time from first meeting to term sheet |
| `board_involvement` | string | Level of post-investment involvement |
| `follow_on_policy` | paragraph | How they approach follow-on investments |
| `key_quotes` | list | Direct quotes from named partners — include attribution and URL |
| `thesis_sources` | list | URLs or publications where thesis is documented |

---

## portfolio.md fields

Each portfolio company is one row in the table:

| Field | Description |
|---|---|
| `company` | Company name |
| `sector` | Primary sector (from taxonomy) |
| `country` | Company HQ country |
| `stage_at_investment` | Stage when fund first invested |
| `year_invested` | Year of first investment |
| `status` | Active / Exited / Failed / Acquired / IPO |
| `exit_details` | If exited: acquirer or IPO details |
| `notable` | Y if unicorn / major exit / landmark deal |
| `conflict` | Y if this company competes with any of your portfolio — detail in brief.md |

---

## co-investors.md fields

| Field | Type | Description |
|---|---|---|
| `lead_or_follow` | enum | Typically Lead / Follow / Either |
| `frequent_co_investors` | list | Funds they most often appear alongside (with frequency if known) |
| `syndication_style` | paragraph | How they approach building syndicates |
| `avoided_co_investors` | list | Known conflicts or firms they don't co-invest with |
| `notable_syndicates` | list | Landmark deals with specific co-investor combinations |

---

## team.md fields

Each partner/principal is one entry:

| Field | Description |
|---|---|
| `name` | Full name |
| `title` | General Partner / Partner / Principal / Associate |
| `focus` | Sectors or stages they cover |
| `background` | Prior companies/roles (2–3 key items) |
| `notable_investments` | 3–5 investments they led or championed |
| `linkedin` | LinkedIn URL |
| `twitter` | @handle |
| `contact_preference` | Cold email / Warm intro only / Unknown |

---

## relationships.md fields

| Field | Type | Description |
|---|---|---|
| `relationship_status` | enum | Strong / Warm / Cold / None / Unknown |
| `last_contact` | date | ISO date (YYYY-MM-DD) |
| `last_contact_by` | string | Name at your firm |
| `last_contact_context` | string | Brief description of the interaction |
| `warm_intro_paths` | table | People who can intro, with strength rating and connection type |
| `past_interactions` | table | Dated log of meetings, emails, events, co-investments |
| `co_investments` | table | Deals done together — round, year, who led |
| `perception_signals` | list | Signals on how they view your firm |
| `action_items` | table | Open tasks with owner and due date |

---

## notes.md fields

| Field | Type | Description |
|---|---|---|
| `file_status` | table | Completion flag per file (Yes / No) |
| `last_updated` | date | ISO date of last edit (YYYY-MM-DD) |
| `data_quality` | score | 1–5 (1 = stub, 5 = comprehensive + verified) |
| `primary_sources` | list | URLs used to build this profile |
| `open_questions` | list | Things still unknown or needing verification |
| `changelog` | list | Dated notes on significant updates |
