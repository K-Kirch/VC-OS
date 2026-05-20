"""
Notion property -> deal.md field mapping.

Single source of truth for the Notion schema boundary. Schema changes in
Notion are reflected by editing this one file.

Current Notion schema — Potential Investments database (Baby VC):
  - Name      (title)
  - Website   (url)
  - LinkedIn  (url)
  - Deck      (url)

The schema is intentionally minimal. The pipeline enriches the rest
during stage 1 (Intake). When the Notion DB gains additional
properties (Stage, Sector, Source, Status, etc.), extend the readers
and `notion_row_to_deal_fields` below.
"""
import re


def _read_property(prop):
    """Return the value of a Notion property regardless of its type."""
    if not prop:
        return None
    ptype = prop["type"]
    val = prop.get(ptype)
    if val is None:
        return None
    if ptype in ("title", "rich_text"):
        text = "".join(t.get("plain_text", "") for t in val)
        return text or None
    if ptype in ("url", "email", "phone_number"):
        return val
    if ptype in ("select", "status"):
        return val.get("name") if val else None
    if ptype == "multi_select":
        return [o["name"] for o in val]
    if ptype == "number":
        return val
    if ptype == "checkbox":
        return val
    if ptype == "date":
        return val.get("start") if val else None
    if ptype == "people":
        return [p.get("name") or p.get("id") for p in val]
    return None


def slugify(name):
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def notion_row_to_deal_fields(page):
    """
    Translate a Notion row into a dict of deal.md fields.

    Fields not present in Notion are returned as None — the deal folder
    keeps the template placeholder for those, to be filled later in the
    pipeline.
    """
    props = page.get("properties", {})
    name = _read_property(props.get("Name"))
    return {
        "company": name,
        "slug": slugify(name) if name else None,
        "website": _read_property(props.get("Website")),
        "linkedin": _read_property(props.get("LinkedIn")),
        "deck_url": _read_property(props.get("Deck")),
        "notion_row_id": page.get("id"),
        "notion_url": page.get("url"),
    }


# Schema gaps — fields the pipeline will need but Notion does not currently
# carry. Either enrich during stage 1, or add as Notion properties later:
#
#   stage, sector, round_size, pre_money, our_check, target_ownership,
#   lead_or_follow, source, source_person, target_ic_date, target_close,
#   current_stage, status
