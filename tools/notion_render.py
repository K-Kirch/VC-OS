"""
Render Notion block children as Markdown.

Supports the block types we expect to see in the Potential Investments DB:
paragraph, headings, bulleted/numbered lists, to-do, quote, callout, code,
divider, toggle, bookmark, link_preview, embed, image, file, child_page.
Unknown blocks fall through as a stub line so nothing is silently dropped.

Nested children (toggles, list items with sub-bullets) are fetched lazily by
passing a `fetch_children` callable; pass `None` to skip recursion.
"""

INLINE_OPEN = {
    "bold": "**",
    "italic": "*",
    "strikethrough": "~~",
    "code": "`",
    "underline": "",  # markdown has no underline; render plain
}


def render_rich_text(rich_text):
    """Render a Notion rich_text array to inline markdown."""
    if not rich_text:
        return ""
    out = []
    for r in rich_text:
        text = r.get("plain_text", "")
        if not text:
            continue
        ann = r.get("annotations", {}) or {}
        wrappers = []
        for key in ("bold", "italic", "strikethrough", "code"):
            if ann.get(key):
                wrappers.append(INLINE_OPEN[key])
        wrapped = text
        for w in wrappers:
            wrapped = f"{w}{wrapped}{w}"
        href = r.get("href")
        if href:
            wrapped = f"[{wrapped}]({href})"
        out.append(wrapped)
    return "".join(out)


def _block_text(block, key):
    return render_rich_text(block.get(key, {}).get("rich_text", []))


def render_blocks(blocks, fetch_children=None, indent=0):
    """Render a list of Notion blocks to a markdown string.

    fetch_children: callable(block_id) -> list[block] or None to skip recursion.
    indent: nesting level for list items / toggle children.
    """
    lines = []
    pad = "  " * indent

    numbered_counter = 0
    prev_type = None

    for block in blocks:
        btype = block.get("type")
        if btype != "numbered_list_item":
            numbered_counter = 0

        if btype == "paragraph":
            text = _block_text(block, "paragraph")
            lines.append(f"{pad}{text}" if text else "")
        elif btype in ("heading_1", "heading_2", "heading_3"):
            level = int(btype.split("_")[1])
            text = _block_text(block, btype)
            lines.append(f"{'#' * level} {text}")
        elif btype == "bulleted_list_item":
            text = _block_text(block, "bulleted_list_item")
            lines.append(f"{pad}- {text}")
        elif btype == "numbered_list_item":
            numbered_counter += 1
            text = _block_text(block, "numbered_list_item")
            lines.append(f"{pad}{numbered_counter}. {text}")
        elif btype == "to_do":
            checked = block.get("to_do", {}).get("checked", False)
            mark = "x" if checked else " "
            text = _block_text(block, "to_do")
            lines.append(f"{pad}- [{mark}] {text}")
        elif btype == "quote":
            text = _block_text(block, "quote")
            lines.append(f"{pad}> {text}")
        elif btype == "callout":
            icon = block.get("callout", {}).get("icon", {}) or {}
            emoji = icon.get("emoji", "") if icon.get("type") == "emoji" else ""
            text = _block_text(block, "callout")
            prefix = f"{emoji} " if emoji else ""
            lines.append(f"{pad}> {prefix}{text}")
        elif btype == "code":
            lang = block.get("code", {}).get("language", "") or ""
            text = _block_text(block, "code")
            lines.append(f"{pad}```{lang}")
            for ln in text.splitlines() or [""]:
                lines.append(f"{pad}{ln}")
            lines.append(f"{pad}```")
        elif btype == "divider":
            lines.append(f"{pad}---")
        elif btype == "toggle":
            text = _block_text(block, "toggle")
            lines.append(f"{pad}- <details><summary>{text}</summary>")
        elif btype == "bookmark":
            url = block.get("bookmark", {}).get("url", "")
            caption = render_rich_text(block.get("bookmark", {}).get("caption", []))
            lines.append(f"{pad}- [{caption or url}]({url})")
        elif btype == "link_preview":
            url = block.get("link_preview", {}).get("url", "")
            lines.append(f"{pad}- {url}")
        elif btype == "embed":
            url = block.get("embed", {}).get("url", "")
            lines.append(f"{pad}- Embed: {url}")
        elif btype in ("image", "file", "pdf", "video", "audio"):
            obj = block.get(btype, {}) or {}
            kind = obj.get("type")
            url = ""
            if kind == "external":
                url = obj.get("external", {}).get("url", "")
            elif kind == "file":
                url = obj.get("file", {}).get("url", "")
            caption = render_rich_text(obj.get("caption", []))
            label = caption or btype
            lines.append(f"{pad}- {btype.capitalize()}: [{label}]({url})")
        elif btype == "child_page":
            title = block.get("child_page", {}).get("title", "")
            lines.append(f"{pad}- Child page: {title}")
        elif btype == "child_database":
            title = block.get("child_database", {}).get("title", "")
            lines.append(f"{pad}- Child database: {title}")
        elif btype == "table_of_contents":
            lines.append(f"{pad}<!-- table of contents -->")
        elif btype == "equation":
            expr = block.get("equation", {}).get("expression", "")
            lines.append(f"{pad}$$ {expr} $$")
        else:
            lines.append(f"{pad}<!-- unhandled block type: {btype} -->")

        # Recurse into children when present.
        if fetch_children and block.get("has_children"):
            child_blocks = fetch_children(block["id"])
            child_md = render_blocks(child_blocks, fetch_children, indent + 1)
            if child_md.strip():
                lines.append(child_md)
            if btype == "toggle":
                lines.append(f"{pad}</details>")

        prev_type = btype

    return "\n".join(lines)
