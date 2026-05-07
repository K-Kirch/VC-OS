#!/usr/bin/env python3
"""
VC OS Fund Scraper
==================
Scrapes a VC fund website and returns clean text for Claude to parse into fund files.

Usage:
    python tools/scraper.py --name "Index Ventures" --url "https://www.indexventures.com"

Output:
    Structured plain text covering homepage, team, portfolio, and thesis pages.
    Pipe to a file or let Claude read it directly.

Note:
    Works on static and server-rendered HTML. For JavaScript-heavy SPAs that render
    blank pages, see the --playwright flag (requires: pip install playwright &&
    playwright install chromium).
"""

import argparse
import sys
import time
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install requests beautifulsoup4 lxml", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

REQUEST_TIMEOUT = 12
POLITE_DELAY = 0.8       # seconds between requests
MAX_CHARS_PER_PAGE = 4000  # cap per page to avoid flooding Claude's context

# Tags to strip before extracting text
STRIP_TAGS = ["script", "style", "nav", "footer", "iframe", "noscript",
              "svg", "img", "picture", "video", "audio", "head"]

# Candidate paths per content type, ordered by likelihood
SUB_PAGE_CANDIDATES = {
    "team": [
        "/team", "/people", "/our-team", "/about/team", "/about/people",
        "/who-we-are", "/partners", "/our-partners", "/about"
    ],
    "portfolio": [
        "/portfolio", "/companies", "/investments", "/our-portfolio",
        "/our-companies", "/our-investments", "/ventures"
    ],
    "thesis": [
        "/approach", "/thesis", "/philosophy", "/what-we-do", "/about",
        "/strategy", "/how-we-invest", "/manifesto", "/focus"
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def base_root(url: str) -> str:
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}"


def clean_text(soup: "BeautifulSoup") -> str:
    """Strip boilerplate tags and return condensed plain text."""
    for tag in soup(STRIP_TAGS):
        tag.decompose()
    lines = []
    for line in soup.get_text(separator="\n").splitlines():
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
    return "\n".join(lines)


def fetch(url: str, session: "requests.Session") -> tuple:
    """Return (clean_text, soup) or (None, None) on failure."""
    try:
        resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        return clean_text(soup), soup
    except requests.exceptions.SSLError:
        try:
            resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, verify=False)
            soup = BeautifulSoup(resp.text, "lxml")
            return clean_text(soup), soup
        except Exception:
            return None, None
    except Exception:
        return None, None


def find_sub_page(base_url: str, homepage_soup: "BeautifulSoup", content_type: str) -> str | None:
    """
    Try to find the best URL for a content type by:
    1. Matching nav/link hrefs against known candidate paths
    2. Falling back to trying candidate paths directly
    """
    root = base_root(base_url)
    candidates = SUB_PAGE_CANDIDATES.get(content_type, [])

    if homepage_soup:
        all_links = [a.get("href", "").strip() for a in homepage_soup.find_all("a", href=True)]
        for candidate in candidates:
            for link in all_links:
                if not link:
                    continue
                # Normalise to full URL
                if link.startswith("http"):
                    full = link
                elif link.startswith("/"):
                    full = root + link
                else:
                    full = urljoin(base_url, link)

                parsed = urlparse(full)
                # Must be same domain; path must match candidate (ignoring trailing slash)
                if (parsed.netloc == urlparse(base_url).netloc and
                        parsed.path.lower().rstrip("/") == candidate.rstrip("/")):
                    return full

    # Direct fallback — try the first candidate path
    for candidate in candidates:
        return root + candidate

    return None


def detect_js_only(text: str | None) -> bool:
    """Heuristic: if page text is very short, it probably needs JS to render."""
    if text is None:
        return True
    return len(text.strip()) < 200


# ---------------------------------------------------------------------------
# Playwright fallback (optional)
# ---------------------------------------------------------------------------

def fetch_with_playwright(url: str) -> tuple:
    """Render a JS-heavy page using Playwright. Requires: pip install playwright && playwright install chromium"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=20000)
            html = page.content()
            browser.close()
        soup = BeautifulSoup(html, "lxml")
        return clean_text(soup), soup
    except Exception:
        return None, None


# ---------------------------------------------------------------------------
# Main scrape function
# ---------------------------------------------------------------------------

def scrape_fund(name: str, url: str, use_playwright: bool = False) -> str:
    """
    Scrape a fund website and return structured plain text.
    Fetches: homepage, team page, portfolio page, thesis/approach page.
    """
    session = requests.Session()
    output = []
    output.append(f"FUND: {name}")
    output.append(f"URL:  {url}")
    output.append("=" * 60)

    # --- Homepage ---
    home_text, home_soup = fetch(url, session)

    if detect_js_only(home_text):
        if use_playwright:
            print(f"[scraper] Homepage appears JS-rendered, trying Playwright...", file=sys.stderr)
            home_text, home_soup = fetch_with_playwright(url)
        else:
            output.append(
                "\nWARNING: Homepage returned very little text — site may be JavaScript-rendered.\n"
                "Results may be incomplete. Re-run with --playwright if Playwright is installed,\n"
                "or check the URL manually.\n"
            )

    if home_text:
        output.append(f"\n--- HOMEPAGE ({url}) ---")
        output.append(home_text[:MAX_CHARS_PER_PAGE])
    else:
        output.append(f"\nERROR: Could not fetch homepage ({url}). Check the URL and try again.")
        return "\n".join(output)

    # --- Sub-pages ---
    fetched_urls = {url}

    for content_type in ["team", "portfolio", "thesis"]:
        sub_url = find_sub_page(url, home_soup, content_type)
        if not sub_url or sub_url in fetched_urls:
            continue

        time.sleep(POLITE_DELAY)
        print(f"[scraper] Fetching {content_type} page: {sub_url}", file=sys.stderr)

        text, _ = fetch(sub_url, session)

        if detect_js_only(text) and use_playwright:
            text, _ = fetch_with_playwright(sub_url)

        if text:
            output.append(f"\n--- {content_type.upper()} PAGE ({sub_url}) ---")
            output.append(text[:MAX_CHARS_PER_PAGE])
            fetched_urls.add(sub_url)
        else:
            output.append(f"\n--- {content_type.upper()} PAGE: could not fetch {sub_url} ---")

    output.append("\n" + "=" * 60)
    output.append("END OF SCRAPE")
    return "\n".join(output)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scrape a VC fund website for VC OS fund population."
    )
    parser.add_argument("--name", required=True, help='Fund name, e.g. "Index Ventures"')
    parser.add_argument("--url",  required=True, help="Fund website URL, e.g. https://www.indexventures.com")
    parser.add_argument("--playwright", action="store_true",
                        help="Use Playwright for JS-rendered sites (requires: pip install playwright && playwright install chromium)")
    args = parser.parse_args()

    result = scrape_fund(args.name, args.url, use_playwright=args.playwright)
    print(result)


if __name__ == "__main__":
    main()
