# IC-prep — Navigation

Workflow for preparing material for Investment Committee meetings. Operating fund: see root `CLAUDE.md`.

## What do you need to do?

| Scenario | Go to |
|---|---|
| Start a new deal | `playbooks/1-intake.md` |
| Build the dataroom | `playbooks/2-dataroom-assembly.md` |
| Synthesize research | `playbooks/3-research-synthesis.md` |
| Draft the memo | `playbooks/4a-memo-drafting.md` |
| Outline the deck | `playbooks/4b-deck-creation.md` |
| Assemble appendix | `playbooks/4c-appendix-assembly.md` |
| Quality-gate review | `playbooks/5-review-gate.md` |
| Final IC package | `playbooks/6-final-package.md` |
| Memo field definitions | `_config/memo-schema.md` |
| Standard slide sequence | `_config/deck-schema.md` |
| Dataroom structure | `_config/dataroom-schema.md` |
| Review criteria | `_config/review-rubric.md` |
| Look up a deal | `deals/<company-slug>/memo.md` |

## Workflow

Linear with recursive review:

```
1. Intake → 2. Dataroom → 3. Research → 4. Build (memo / deck / appendix) → 5. Review → 6. Package
                                                          ↑                       ↓
                                                          └───────  reroute  ─────┘
```

The review gate (stage 5) may route back to any prior stage. All reroutes logged in the deal's `review-log.md`.

## Three artifacts, three workflows

| Artifact | File | Workflow |
|---|---|---|
| Memo (canonical) | `memo.md` | `4a-memo-drafting.md` |
| Deck outline (→ Claude Design) | `deck-outline.md` | `4b-deck-creation.md` |
| Appendix (curated supporting material) | `appendix.md` | `4c-appendix-assembly.md` |

Memo is the source of truth. Deck and appendix derive from it — no new claims introduced downstream.

## Adding a new deal

1. Copy `_template/` → `deals/<company-slug>/`
2. Fill `deal.md` (meta) and initialize `notes.md`
3. Follow playbooks 1 → 6
