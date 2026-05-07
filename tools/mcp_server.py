#!/usr/bin/env python3
"""
VC OS MCP Server — Fund Website Scraper
========================================
Exposes the fund scraper as an MCP tool so Claude can call it directly
within a Claude Code session — no API keys, no cost.

Setup:
    1. Install dependencies:
           pip install requests beautifulsoup4 lxml

    2. Register in Claude Code settings (settings.json):
           {
             "mcpServers": {
               "vc-os": {
                 "command": "python",
                 "args": ["C:/Users/krist/Desktop/VC OS/tools/mcp_server.py"]
               }
             }
           }

    3. Restart Claude Code. Claude can now call scrape_fund() directly.

Protocol:
    MCP over stdio — JSON-RPC 2.0, newline-delimited messages.
"""

import json
import sys
import os

# Make scraper importable from the same directory
sys.path.insert(0, os.path.dirname(__file__))
from scraper import scrape_fund

# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "scrape_fund",
        "description": (
            "Scrape a VC fund website to retrieve profile, team, portfolio, and thesis information. "
            "Returns clean plain text extracted from the fund's homepage, team page, portfolio page, "
            "and approach/thesis page. Use this before populating a fund's markdown files."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Fund name, e.g. 'Index Ventures'"
                },
                "url": {
                    "type": "string",
                    "description": "Fund website URL, e.g. 'https://www.indexventures.com'"
                },
                "use_playwright": {
                    "type": "boolean",
                    "description": "Use Playwright for JavaScript-rendered sites. Requires: pip install playwright && playwright install chromium. Default: false.",
                    "default": False
                }
            },
            "required": ["name", "url"]
        }
    }
]


# ---------------------------------------------------------------------------
# Request handlers
# ---------------------------------------------------------------------------

def handle_initialize(params: dict) -> dict:
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "vc-os-scraper", "version": "1.0.0"}
    }


def handle_tools_list(_params: dict) -> dict:
    return {"tools": TOOLS}


def handle_tools_call(params: dict) -> dict:
    tool_name = params.get("name")
    args = params.get("arguments", {})

    if tool_name != "scrape_fund":
        raise ValueError(f"Unknown tool: {tool_name}")

    name = args.get("name", "")
    url = args.get("url", "")
    use_playwright = args.get("use_playwright", False)

    if not name or not url:
        raise ValueError("Both 'name' and 'url' are required.")

    result = scrape_fund(name, url, use_playwright=use_playwright)

    return {
        "content": [{"type": "text", "text": result}]
    }


HANDLERS = {
    "initialize":   handle_initialize,
    "tools/list":   handle_tools_list,
    "tools/call":   handle_tools_call,
}


# ---------------------------------------------------------------------------
# JSON-RPC loop
# ---------------------------------------------------------------------------

def process_message(raw: str) -> str | None:
    try:
        msg = json.loads(raw)
    except json.JSONDecodeError:
        return None

    msg_id = msg.get("id")
    method = msg.get("method", "")

    # Notifications (no id) — acknowledge but don't respond
    if msg_id is None:
        return None

    handler = HANDLERS.get(method)
    if handler is None:
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }
        return json.dumps(response)

    try:
        result = handler(msg.get("params", {}))
        response = {"jsonrpc": "2.0", "id": msg_id, "result": result}
    except Exception as e:
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32603, "message": str(e)}
        }

    return json.dumps(response)


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = process_message(line)
        if response:
            print(response, flush=True)


if __name__ == "__main__":
    main()
