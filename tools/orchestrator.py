"""
IC-prep orchestrator — drives deals through the IC-prep pipeline.

Phase 1: init, queue, status. No Claude invocation yet — that lands in Phase 2.

Usage:
    python tools/orchestrator.py queue
    python tools/orchestrator.py init --row-id <notion-row-id>
    python tools/orchestrator.py init --all
    python tools/orchestrator.py status [<slug>]
"""
import argparse
import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notion_client import NotionError, get_page, query_database
from notion_mapping import notion_row_to_deal_fields

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path(__file__).with_name("orchestrator.config.json")


def load_config():
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# State reading
# ---------------------------------------------------------------------------

def read_current_stage(deal_path):
    deal_md = deal_path / "deal.md"
    if not deal_md.exists():
        return "Not initialized"
    text = deal_md.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "`current_stage`" in line and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                return parts[2] or "(empty)"
    return "(unknown)"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_queue(cfg):
    """List all Notion rows with current pipeline state."""
    rows = query_database(cfg["notion"]["database_id"])
    deals_dir = WORKSPACE_ROOT / cfg["paths"]["deals"]
    print(f"{'COMPANY':35s}  {'SLUG':30s}  {'STATE':25s}  NOTION ID")
    print("-" * 120)
    for row in rows:
        fields = notion_row_to_deal_fields(row)
        if not fields["company"]:
            continue
        slug = fields["slug"]
        deal_path = deals_dir / slug
        state = read_current_stage(deal_path) if deal_path.exists() else "Not initialized"
        print(f"{fields['company']:35s}  {slug:30s}  {state:25s}  {row['id']}")


def cmd_init(cfg, row_id=None, all_rows=False):
    """Create deal folder(s) from Notion row(s)."""
    template_dir = WORKSPACE_ROOT / cfg["paths"]["template"]
    deals_dir = WORKSPACE_ROOT / cfg["paths"]["deals"]
    deals_dir.mkdir(parents=True, exist_ok=True)

    if all_rows:
        rows = query_database(cfg["notion"]["database_id"])
    elif row_id:
        rows = [get_page(row_id)]
    else:
        raise SystemExit("Provide --row-id or --all")

    for row in rows:
        fields = notion_row_to_deal_fields(row)
        if not fields["company"]:
            print(f"  skip:    {row['id']}  (no Name)")
            continue
        if fields["company"].strip().lower() == "template":
            print(f"  skip:    {fields['company']}  (Notion template placeholder)")
            continue
        slug = fields["slug"]
        deal_path = deals_dir / slug
        if deal_path.exists():
            print(f"  exists:  {slug}")
            continue
        shutil.copytree(template_dir, deal_path)
        replace_company_name_everywhere(deal_path, fields["company"])
        fill_deal_md(deal_path / "deal.md", fields)
        init_notes_md(deal_path / "notes.md", fields)
        print(f"  init:    {slug}  ({row['id']})")


def cmd_status(cfg, slug=None):
    deals_dir = WORKSPACE_ROOT / cfg["paths"]["deals"]
    if not deals_dir.exists():
        print("No deals directory yet.")
        return
    if slug:
        deal_path = deals_dir / slug
        if not deal_path.exists():
            print(f"No deal at {deal_path}")
            return
        print(f"{slug}: {read_current_stage(deal_path)}")
        return
    for deal_dir in sorted(p for p in deals_dir.iterdir() if p.is_dir()):
        print(f"{deal_dir.name:35s}  {read_current_stage(deal_dir)}")


# ---------------------------------------------------------------------------
# Template fillers
# ---------------------------------------------------------------------------

def replace_company_name_everywhere(deal_path, company_name):
    """Replace <Company Name> placeholder across every .md in the deal folder."""
    for md_path in deal_path.rglob("*.md"):
        text = md_path.read_text(encoding="utf-8")
        if "<Company Name>" in text:
            md_path.write_text(text.replace("<Company Name>", company_name), encoding="utf-8")


def fill_deal_md(deal_md_path, fields):
    text = deal_md_path.read_text(encoding="utf-8")
    today = date.today().isoformat()
    replacements = {
        "# Deal — <Company Name>": f"# Deal — {fields['company']}",
        "| `company` | <Company Name> |": f"| `company` | {fields['company']} |",
        "| `slug` | <company-slug> |": f"| `slug` | {fields['slug']} |",
        "| `website` | <url> |": f"| `website` | {fields.get('website') or 'Unknown'} |",
        "| `first_contact` | <YYYY-MM-DD> |": f"| `first_contact` | {today} |",
        "| `current_stage` | <Intake / Dataroom / Research / Build / Review / Package / Decided> |":
            "| `current_stage` | Intake |",
        "| `status` | <Active / Passed / Closed / Killed> |": "| `status` | Active |",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    deal_md_path.write_text(text, encoding="utf-8")


def init_notes_md(notes_md_path, fields):
    text = notes_md_path.read_text(encoding="utf-8")
    today = date.today().isoformat()

    sources_block = (
        "## Sources\n\n"
        f"- Notion: {fields['notion_url']}\n"
        f"- Website: {fields.get('website') or 'Unknown'}\n"
        f"- LinkedIn: {fields.get('linkedin') or 'Unknown'}\n"
        f"- Deck: {fields.get('deck_url') or 'Not provided'}\n"
    )
    text = text.replace("## Sources\n\n- <url / file / person>\n", sources_block)

    changelog_block = (
        "## Changelog\n\n| Date | Change |\n|---|---|\n"
        f"| {today} | Initialized from Notion row {fields['notion_row_id']} |\n"
    )
    text = text.replace(
        "## Changelog\n\n| Date | Change |\n|---|---|\n| | |\n",
        changelog_block,
    )
    notes_md_path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(prog="orchestrator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("queue")

    init_p = sub.add_parser("init")
    grp = init_p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--row-id")
    grp.add_argument("--all", action="store_true")

    status_p = sub.add_parser("status")
    status_p.add_argument("slug", nargs="?")

    args = parser.parse_args()
    cfg = load_config()
    try:
        if args.cmd == "queue":
            cmd_queue(cfg)
        elif args.cmd == "init":
            cmd_init(cfg, row_id=args.row_id, all_rows=args.all)
        elif args.cmd == "status":
            cmd_status(cfg, slug=args.slug)
    except NotionError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
