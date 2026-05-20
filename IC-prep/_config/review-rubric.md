# Review Rubric — Quality Gates & Reroute Logic

The review gate (`playbooks/5-review-gate.md`) checks against this rubric. Failures route back to a prior stage; events logged in `review-log.md`.

## After stage 2 — Dataroom assembly

- [ ] Founder deck present
- [ ] ≥ 1 founder interview completed and written up
- [ ] Customer interviews: ≥ 3 (or documented why not feasible)
- [ ] References: ≥ 2 backchannel calls on the founding team
- [ ] Financials: historicals + plan provided by founder
- [ ] `dataroom/INDEX.md` reflects current state

**Reroute:** missing items → stage 2

## After stage 3 — Research synthesis

- [ ] `research.md` synthesizes dataroom into key findings
- [ ] `competition.md` covers direct + indirect competitors
- [ ] `risks.md` lists ≥ 5 risks with mitigations
- [ ] `conflicts.md` checked against operating fund `portfolio.md` — explicit Pass / Conflict
- [ ] `syndication.md` proposes ≥ 3 candidate co-investors drawn from `funds/`
- [ ] Market sizing in `research.md` has source attribution

**Reroute:** evidence gaps → stage 2; analysis gaps → stage 3

## After stage 4 — Build

- [ ] Every claim in `memo.md` traces to a working file or dataroom item
- [ ] Section word budgets respected (or overrun explicitly justified)
- [ ] `deck-outline.md` aligned with `memo.md` — no contradictions, no new claims
- [ ] `appendix.md` curated — only items the IC may ask about
- [ ] `recommendation.md` drafted with conditions to close
- [ ] §16 (Fit with Our Fund) reflects operating fund mandate from root `CLAUDE.md`

**Reroute matrix:**

| Failure | Reroute to |
|---|---|
| Missing dataroom item | 2 |
| Unsupported claim | 2 (gather) or 3 (cite existing) |
| Weak market sizing | 3 |
| Memo/deck contradiction | within 4 |
| Unresolved portfolio conflict | 3 (re-check) |
| Mandate mismatch | escalate; do not proceed |

## Hard blockers — never pass

- Unresolved portfolio conflict (`conflicts.md` shows direct competitor in operating fund portfolio without explicit resolution)
- No founder reference completed
- Mandate mismatch (stage / sector / geography outside operating fund parameters) without IC pre-approval
