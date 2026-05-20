# Playbook 4b — Deck Creation

**When to use:** Memo draft exists. Build the IC presentation outline.

## Steps

1. **Open `deck-outline.md`** — follow `_config/deck-schema.md` (10–15 slides)
2. **One key message per slide** — distilled from the corresponding `memo.md` section
3. **Visual specification** — describe charts / diagrams in text (Claude Design will produce the actual slides from this outline)
4. **Speaker notes** — ≤ 60 words per slide, conversational
5. **Sanity check vs. memo** — no claims in the deck that aren't in the memo. Reroute if contradiction.
6. **Handoff to Claude Design** — pass `deck-outline.md` to the design workflow; place the produced deck in `dataroom/deck/ic-deck-<YYYY-MM-DD>.<ext>`

## Hard rules

- Deck never introduces new claims — only emphasizes memo content
- Visuals described, not drawn
- 10–15 slides total

## Exit criterion

`deck-outline.md` complete, ready for Claude Design.

## Next stage

`4c-appendix-assembly.md` (if not parallel) → `5-review-gate.md`
