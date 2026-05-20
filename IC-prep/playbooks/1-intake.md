# Playbook 1 — Intake

**When to use:** A new deal enters the pipeline.

## Steps

1. **Create deal folder** — copy `_template/` → `deals/<company-slug>/`
2. **Fill `deal.md`** — all meta fields; mark unknowns explicitly
3. **Set targets** — `target_ic_date`, `target_close`
4. **Mandate check** — does this deal fit the operating fund mandate? (See root `CLAUDE.md` → operating fund → stage / sector / geography / check size)
   - Hard mismatch → escalate to sponsoring partner before further work
5. **Initialize `notes.md`** — log source, first contact, initial open questions

## Exit criterion

`deal.md` complete (no missing required fields), mandate check passed or escalated, `notes.md` initialized.

## Next stage

`2-dataroom-assembly.md`
