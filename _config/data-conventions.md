# VC OS — Data Conventions

## Source Tags

Every field value in fund files should be traceable. Use inline tags to indicate provenance:

| Tag | Meaning | Trust Level |
|---|---|---|
| `[S]` | Scraped from fund website (this session) | High — ground truth |
| `[M]` | AI training data / memory — not verified against a primary source | Low — verify before live use |
| `[V]` | Manually verified against a primary source | High |
| *(no tag)* | Unknown origin — treat as unverified | Low |

### Where to apply

Apply tags at the **field level** in profile.md and team.md tables, and at the **section level** in portfolio.md and co-investors.md when the entire block is from a single source.

**Example — profile.md field:**
```
| **Check Size** | €500K – €5M [M] |
| **Founded** | 2003 [S] |
```

**Example — team.md section header:**
```
<!-- Source: [M] — team populated from AI training data. Verify names, titles, and investment attribution before use in a live deal. -->
```

**Example — portfolio.md summary note:**
```
| **Source Completeness** | Key companies from scrape [S] + memory [M]; full list requires Crunchbase |
```

---

## Data Quality Scale

| Score | Meaning |
|---|---|
| 1 | Stub — folder exists, no files populated |
| 2 | Homepage only — thesis.md partial, all others empty or placeholder |
| 3 | Core files populated (profile, thesis) — team/portfolio from memory [M], not verified |
| 4 | Core files verified — team and portfolio substantially complete with sourced data |
| 5 | Comprehensive — all files verified, relationships active, no open questions |

**Key rule:** A fund cannot be quality 4 or above if team.md or portfolio.md is primarily `[M]`-tagged.

---

## The `[M]` Rule

Any value tagged `[M]` must be treated as a hypothesis, not a fact. Specific risks:

- **team.md investment attribution `[M]`**: A partner attributed to a deal they didn't lead will be embarrassed if you raise it. Verify on Crunchbase or LinkedIn before any outreach.
- **portfolio.md company entries `[M]`**: Wrong conflict flags or wrong portfolio company claims can damage a co-investment conversation.
- **check size `[M]`**: Negotiating based on a wrong check size is a bad start.

Do not rely on `[M]`-tagged data in live deal conversations without first verifying.

---

## "Unknown" vs. `[M]`

| Value | Meaning |
|---|---|
| `Unknown` | No data at all — field has not been researched |
| `[M]` | Data exists but the source is AI memory, not a verified primary source |

Never replace `Unknown` with `[M]`-tagged data unless you are willing to verify it before acting on it.
