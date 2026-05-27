"""
Notion API wrapper — read + write for the orchestrator.

The orchestrator is the only place that talks to Notion. Headless Claude
instances must never call this module.

Token: read from NOTION_TOKEN environment variable. Never hardcoded.
"""
import json
import os
import urllib.error
import urllib.request

NOTION_VERSION = "2022-06-28"
API_BASE = "https://api.notion.com/v1"
REQUEST_TIMEOUT = 20


class NotionError(RuntimeError):
    pass


def _headers():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise NotionError(
            "NOTION_TOKEN environment variable is not set. "
            "Set it in your shell before running the orchestrator."
        )
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _request(method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"{API_BASE}{path}", data=data, method=method, headers=_headers()
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise NotionError(f"Notion API {e.code} on {method} {path}: {err_body}") from e


def query_database(database_id, page_size=100):
    """Return all rows from the database, paginated."""
    results = []
    payload = {"page_size": page_size}
    while True:
        data = _request("POST", f"/databases/{database_id}/query", payload)
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return results


def get_page(page_id):
    return _request("GET", f"/pages/{page_id}")


def get_database(database_id):
    return _request("GET", f"/databases/{database_id}")


def get_block_children(block_id, page_size=100):
    """Return all child blocks of a page or block, paginated."""
    results = []
    params = f"?page_size={page_size}"
    while True:
        data = _request("GET", f"/blocks/{block_id}/children{params}")
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        params = f"?page_size={page_size}&start_cursor={data['next_cursor']}"
    return results
