# IC-prep Automation — Architecture

> Design doc for the orchestrated IC-prep pipeline. Source of truth for build phases. Update on architectural changes.

## Purpose

Drive deals through the IC-prep workflow (`playbooks/1-intake.md` → `6-final-package.md`) automatically:

- Read potential investments from a Notion database
- Initialize a deal folder per investment from `_template/`
- Execute each stage in a fresh Claude context, scoped to that deal folder
- Verify claims with an independent research-analyst subagent
- Sync status back to Notion
- Skip blocked deals and continue processing the queue

## Source Notion database

**Parent page:** Baby VC - Investment Challenge (`365209d4-799c-8047-ab8c-d7d1cd098293`)
**Database:** Potential Investments (`365209d4-799c-8061-82f5-d4c700dcf4f2`) — child of the parent page

Access via **Notion Integration token** (Option a). Configuration:

- Env var: `NOTION_TOKEN` — integration token with access to the parent page
- Config: `tools/orchestrator.config.json` → `notion.database_id`

Property mapping lives in `tools/notion_mapping.py` and is the only place the Notion schema is referenced. Schema changes in Notion → update this one file.

### Current Notion schema (minimal)

| Property | Type |
|---|---|
| Name | title |
| Website | url |
| LinkedIn | url |
| Deck | url |

This is intentionally minimal. The pipeline enriches the rest during stage 1 (Intake). When the Notion DB gains additional properties (Stage, Sector, Source, Status, etc.), extend `notion_mapping.py`.

### Filtering

The Notion DB contains a row literally named "Template" (Notion's own placeholder). The orchestrator filters this row out of `init --all`.

## High-level architecture

```
Notion DB  ◄──────────── orchestrator (read + write status) ────────┐
                                  │                                  │
                                  │ for each deal × each stage       │
                                  ▼                                  │
                  ┌────────────────────────────────┐                 │
                  │ Headless Claude (one stage)    │                 │
                  │  cwd = deals/<slug>            │                 │
                  │  ┌──────────────────────────┐  │                 │
                  │  │ Stage execution loop     │  │                 │
                  │  └────────┬─────────────────┘  │                 │
                  │           │ Agent tool         │                 │
                  │           ▼                    │                 │
                  │  ┌──────────────────────────┐  │                 │
                  │  │ research-analyst subagent│  │                 │
                  │  │  (read-only verifier)    │  │                 │
                  │  └──────────────────────────┘  │                 │
                  │  writes: deal artifacts        │                 │
                  │           verification/*.md    │                 │
                  └────────────┬───────────────────┘                 │
                               │ exit code + state update            │
                               ▼                                     │
                          orchestrator advances state ───────────────┘
```

Single state store: each deal's `deal.md` `current_stage` field. Version-controlled. No external DB.

## Components

### 1. Orchestrator (`tools/orchestrator.py`)

Python CLI. Owns the pipeline loop and all Notion I/O.

| Command | Purpose |
|---|---|
| `init <notion-row-id>` | Initialize a deal folder from a Notion row |
| `run <slug>` | Run the full pipeline for one deal until done or blocked |
| `run-stage <slug> <stage>` | Run a single stage (for debugging) |
| `resume <slug>` | Resume a blocked deal (after human resolves the blocker) |
| `queue` | List Notion rows ready for IC-prep + their current pipeline state |
| `sync <slug>` | Push current deal state to Notion |

### 2. Notion client (`tools/notion_client.py`)

Thin wrapper around the Notion API. Functions:

- `list_ready_deals()` — rows where `pipeline_status = Ready for IC-prep`
- `get_deal(row_id)` — full row with properties
- `update_deal_status(row_id, stage, blocker=None, ic_date=None, recommendation=None)`

No business logic — mapping lives in `notion_mapping.py`.

### 3. Notion mapping (`tools/notion_mapping.py`)

Single bidirectional translation layer:

- `notion_row_to_deal_fields(row) -> dict` — fills `deal.md` from Notion
- `deal_state_to_notion_update(deal_path) -> dict` — pushes state back

Schema reference (filled when the integration token is provisioned):

```python
NOTION_TO_DEAL = {
    "Company": "company",
    # "Stage": "stage",
    # "Sector": "sector",
    # ... pending schema introspection
}
```

### 4. Deal initializer (`tools/orchestrator.py:init`)

For each new Notion row:

1. Generate `<company-slug>` (kebab-case from `Company` property)
2. Copy `IC-prep/_template/` → `IC-prep/deals/<slug>/`
3. Fill `deal.md` from `notion_row_to_deal_fields()`
4. Set `current_stage = Intake`
5. Initialize `notes.md` changelog with Notion source link
6. Update Notion: `pipeline_status = In Progress`, `deal_folder = <slug>`

### 5. Stage runner (`tools/stage_runner.py`)

Spawns one headless Claude per stage:

```python
subprocess.run([
    "claude", "-p", render_prompt(stage, deal_path),
    "--output-format", "json",
    "--permission-mode", "acceptEdits",
    "--add-dir", str(deal_path),
], cwd=workspace_root, capture_output=True, timeout=STAGE_TIMEOUT)
```

Properties:
- Fresh process = fresh context window per stage
- Auto-approves file edits *within the deal folder only* (`--add-dir` scopes the write boundary)
- Reads root `CLAUDE.md` automatically → operating-fund context available
- Output captured to `IC-prep/_pipeline/runs/<slug>/<timestamp>-stage-<N>.log`

### 6. Stage prompt template

Uniform across stages. The playbook does the work; the prompt just points Claude at it.

```
You are executing IC-prep stage <N>: <stage name>.

Deal folder: IC-prep/deals/<slug>/
Playbook:    IC-prep/playbooks/<playbook-file>.md
Operating fund: see root CLAUDE.md

Read the playbook. Execute every step in order. Exit criterion is at the
bottom of the playbook.

For stages 3 and 5: invoke the research-analyst subagent to verify claims.
See .claude/agents/research-analyst.md.

When complete:
1. Update deal.md `current_stage` to the next stage
2. Append a row to review-log.md (date, stage, result, issue, reroute)
3. Exit

If the stage cannot complete (missing materials, conflict, mandate mismatch):
1. Write the blocker to notes.md
2. Set current_stage = "Blocked-<reason>"
3. Exit
```

Stored as `tools/prompts/stage-<N>.txt` with `<slug>` and other variables interpolated at runtime.

### 7. State machine

`deal.md` `current_stage` drives orchestrator behavior:

| State | Next action |
|---|---|
| `Intake` | Run playbook 1 |
| `Dataroom` | Run playbook 2 |
| `Research` | Run playbook 3 (with verification) |
| `Build` | Run 4a → 4b → 4c sequentially |
| `Review` | Run playbook 5 (with verification) |
| `Package` | Run playbook 6 |
| `Decided` | Sync vote to Notion; deal done |
| `Blocked-<reason>` | Log; notify (CLI); move to next deal in queue |

### 8. Reroute logic

After stage 5, orchestrator reads the latest `review-log.md` row:

- `Result = Pass` → set `current_stage = Package`, continue
- `Result = Reroute, target = N` → set `current_stage = <N>`, re-run
- **Cap: 3 reroutes per deal.** On the 4th, force `Blocked-Reroute-Cap` and escalate.

### 9. "Blocked, move on" semantics

| Scope | Behavior |
|---|---|
| Pipeline level (queue of deals) | Blocked deal logged to CLI; orchestrator advances to next deal. Manual `resume` required to unblock. |
| Within stage 4 (4a → 4b → 4c) | 4a is prerequisite for 4b and 4c. If 4b fails, 4c still runs (no mutual dependency). Orchestrator runs sub-stages whose dependencies are satisfied. |
| Within a stage | Atomic. A stage that cannot complete writes the blocker and exits — never half-finishes. |

### 10. Research Analyst subagent

Read-only verifier. Defined at `.claude/agents/research-analyst.md`.

**Role:** Independent verification of claims in deal documentation and dataroom. Adversarial peer review — find weak claims, missing evidence, market-sizing errors, competitive blind spots, founder-narrative drift.

**Tools allowed:** `Read`, `Grep`, `Glob`, `WebSearch`, `WebFetch`
**Tools denied:** `Write`, `Edit`, `Bash` — no side effects.

**Invocation points:**

| Stage | Verification scope |
|---|---|
| 3 — Research synthesis | `research.md`, `competition.md`, `risks.md`, market sizing. Output: `verification/stage-3-<date>.md` |
| 5 — Review gate | `memo.md` claims vs. dataroom + working files; independent web checks on team backgrounds, funding history, public market data. Output: `verification/stage-5-<date>.md` |

**Verdict structure:** Pass with no findings / Pass with minor findings / Fail — N material findings (≥ 3 high-severity findings forces a reroute).

**Output schema:** see template in `_template/verification/`.

### 11. Human-in-the-loop gates

Stages that block on human action — orchestrator pauses, logs, moves on:

| Trigger | State | Resolution |
|---|---|---|
| Founder materials missing | `Blocked-Dataroom` | Human collects materials, places them in `dataroom/`, runs `resume` |
| References unavailable | `Blocked-References` | Human schedules references; or proceeds with explicit risk flag |
| Portfolio conflict found | `Blocked-Conflict` | Human + sponsoring partner decide path; resolution logged in `conflicts.md` |
| Mandate mismatch | `Blocked-Mandate` | IC pre-approval required |
| Reroute cap exceeded | `Blocked-Reroute-Cap` | Human review of `review-log.md` |
| Sponsoring partner sign-off | Always at end of stage 5 | Human signs `review-log.md` |

### 12. Observability

- `IC-prep/_pipeline/pipeline.log` — orchestrator-level events (one line per state transition)
- `IC-prep/_pipeline/runs/<slug>/<YYYY-MM-DD-HHMMSS>-stage-<N>.log` — per-stage Claude transcripts
- `IC-prep/deals/<slug>/review-log.md` — canonical decision history per deal (already specified in `_template/`)
- `IC-prep/deals/<slug>/notes.md` changelog — human-readable activity per deal
- Notion: `pipeline_status`, `current_stage`, `blocker` updated on every transition

## File layout

```
tools/
├── orchestrator.py              # CLI driver
├── notion_client.py             # Notion API wrapper
├── notion_mapping.py            # Notion ↔ deal.md field map
├── stage_runner.py              # subprocess wrapper for `claude -p`
├── orchestrator.config.json     # database_id, stage timeouts, reroute cap
└── prompts/
    ├── stage-1-intake.txt
    ├── stage-2-dataroom.txt
    ├── stage-3-research.txt
    ├── stage-4a-memo.txt
    ├── stage-4b-deck.txt
    ├── stage-4c-appendix.txt
    ├── stage-5-review.txt
    └── stage-6-package.txt

.claude/
└── agents/
    └── research-analyst.md      # Subagent definition

IC-prep/
├── automation-architecture.md   # This file
├── _template/
│   └── verification/            # Verification reports per stage
│       ├── README.md
│       └── .gitkeep
└── _pipeline/                   # Runtime logs (gitignored)
    ├── pipeline.log
    └── runs/<slug>/<timestamp>-stage-<N>.log
```

## Schema updates required

- `_config/review-rubric.md` — add criterion: "Research-analyst verification report shows Pass or ≤ minor findings"
- `_template/notes.md` — add `verification/` to file status table

## Build phases

| Phase | Deliverable | Validates |
|---|---|---|
| 1 | `orchestrator init <row-id>` — Notion read + deal folder creation. No Claude. | Notion integration + mapping |
| 2 | `orchestrator run-stage <slug> <stage>` — single headless Claude invocation. | Prompt template + state update + permission scoping |
| 3 | `.claude/agents/research-analyst.md` + verification folder | Subagent execution + verification report shape |
| 4 | `orchestrator run <slug>` — full pipeline with reroute logic | End-to-end one deal |
| 5 | `orchestrator queue` — multi-deal processing with "blocked, move on" | Pipeline-level scheduling |
| 6 | Notion write-back on every state transition | Full bidirectional sync |

Each phase is independently shippable and testable.

## Open items

- `STAGE_TIMEOUT` per stage — to be tuned after first end-to-end run
- Reroute cap = 3 (decision locked); reassess after live data
- Notion schema is minimal (4 properties). Consider adding to Notion later: `Stage`, `Sector`, `Pipeline Status`, `IC Date`, `Recommendation`, `Blocker` — would enable bidirectional state sync. Until then, state lives only in `deal.md`.

## Hard constraints (do not violate)

- Notion access lives only in the orchestrator. Claude instances never touch the Notion API.
- Claude instances are scoped to their deal folder via `--add-dir`. They cannot edit outside it.
- Research-analyst subagent is read-only — no `Write`, `Edit`, or `Bash`.
- Every stage transition writes to `review-log.md`. No silent state changes.
- One source of truth per concern: state in `deal.md`, decisions in `review-log.md`, raw inputs in `dataroom/`, synthesis in working files, IC-facing in `memo.md` / `appendix.md` / `deck-outline.md`.
