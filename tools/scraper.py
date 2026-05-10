#!/usr/bin/env python3
"""
VC OS Fund Scraper
==================
Scrapes a VC fund website and returns clean text for Claude to parse into fund files.

Usage:
    python tools/scraper.py --name "Index Ventures" --url "https://www.indexventures.com"

Output:
    Structured plain text covering homepage, team, portfolio, and thesis pages.
    Includes lightweight structured extraction of team members and portfolio companies
    found in HTML elements — these are tagged [S] and more reliable than plain text alone.

Note:
    Works on static and server-rendered HTML. For JavaScript-heavy SPAs that render
    blank pages or return the homepage shell for all routes, use the --playwright flag
    (requires: pip install playwright && playwright install chromium).
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
POLITE_DELAY = 0.8
MAX_CHARS_PER_PAGE = 6000

STRIP_TAGS = ["script", "style", "nav", "footer", "iframe", "noscript",
              "svg", "img", "picture", "video", "audio", "head"]

# Candidate paths per content type, ordered by likelihood.
# All candidates are tried in sequence until one returns unique, usable content.
SUB_PAGE_CANDIDATES = {
    "team": [
        "/team", "/people", "/our-team", "/about/team", "/about/people",
        "/who-we-are", "/partners", "/our-partners", "/about"
    ],
    "portfolio": [
        "/portfolio", "/commitments", "/companies", "/investments", "/our-portfolio",
        "/our-companies", "/our-investments", "/ventures"
    ],
    "thesis": [
        "/approach", "/thesis", "/philosophy", "/what-we-do",
        "/strategy", "/how-we-invest", "/manifesto", "/focus", "/about"
    ],
}

# SPA detection: sub-pages sharing this many leading characters with the homepage
# are almost certainly returning the same HTML shell (client-side routing).
SPA_FINGERPRINT_LEN = 300

# Structured extraction: keywords that identify portfolio/team containers in HTML
PORTFOLIO_KEYWORDS = ["portfolio", "companies", "investments", "ventures", "our-companies"]
TEAM_KEYWORDS = ["team", "people", "partners", "staff", "founders"]


# ---------------------------------------------------------------------------
# Fetch helpers
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


def detect_js_only(text: str | None) -> bool:
    """Page text is very short — likely needs JS to render."""
    if text is None:
        return True
    return len(text.strip()) < 200


def is_spa_duplicate(sub_text: str, home_text: str) -> bool:
    """
    True if a sub-page returned the same HTML shell as the homepage.

    SPAs using client-side routing return the homepage skeleton for every URL;
    actual content is injected by JS after load. requests/BS4 can't run JS,
    so all sub-pages look identical. We detect this by comparing the opening
    characters of the extracted text — if they match, it's the same shell.
    """
    if not sub_text or not home_text:
        return False
    fp_len = min(SPA_FINGERPRINT_LEN, len(sub_text), len(home_text))
    return sub_text[:fp_len] == home_text[:fp_len]


# ---------------------------------------------------------------------------
# Sub-page discovery — tries all candidates, not just the first
# ---------------------------------------------------------------------------

def find_sub_page_candidates(base_url: str, homepage_soup: "BeautifulSoup", content_type: str) -> list:
    """
    Return an ordered list of candidate URLs to try for a given content type.

    Strategy:
    1. Nav/link matches — URLs actually present on the homepage, in candidate order
    2. Direct path fallbacks — all remaining candidates not found in nav links
    """
    root = base_root(base_url)
    candidates = SUB_PAGE_CANDIDATES.get(content_type, [])
    base_netloc = urlparse(base_url).netloc

    nav_matched = []
    direct_fallbacks = []

    if homepage_soup:
        all_links = [a.get("href", "").strip() for a in homepage_soup.find_all("a", href=True)]

        for candidate in candidates:
            matched = False
            for link in all_links:
                if not link:
                    continue
                if link.startswith("http"):
                    full = link
                elif link.startswith("/"):
                    full = root + link
                else:
                    full = urljoin(base_url, link)

                parsed = urlparse(full)
                if (parsed.netloc == base_netloc and
                        parsed.path.lower().rstrip("/") == candidate.rstrip("/")):
                    if full not in nav_matched:
                        nav_matched.append(full)
                    matched = True
                    break

            if not matched:
                direct_fallbacks.append(root + candidate)

    else:
        direct_fallbacks = [root + c for c in candidates]

    return nav_matched + direct_fallbacks


# ---------------------------------------------------------------------------
# Structured extractors — pull data directly from HTML elements
# ---------------------------------------------------------------------------

def extract_team_members(soup: "BeautifulSoup") -> list:
    """
    Extract person names and brief bios from team-page HTML patterns.

    Looks for headings (h2/h3/h4) that look like person names (2-4 title-cased words),
    then grabs the immediately following paragraph(s) as bio/title text.

    Returns a list of dicts: [{"name": str, "bio": str}]
    Results are tagged [S] — extracted from HTML structure, not guessed.
    """
    members = []
    seen = set()

    for heading in soup.find_all(["h2", "h3", "h4"]):
        text = heading.get_text().strip()
        words = text.split()
        # Heuristic: person names are 2-4 words, each starting with a capital letter
        if not (1 < len(words) <= 4):
            continue
        if not all(w[0].isupper() for w in words if w and w[0].isalpha()):
            continue
        # Avoid generic headings like "Our Team", "Meet The Partners"
        skip_words = {"our", "the", "meet", "team", "partners", "people", "about", "portfolio"}
        if any(w.lower() in skip_words for w in words):
            continue
        if text in seen:
            continue

        bio_parts = []
        for sib in heading.next_siblings:
            if getattr(sib, "name", None) in ["h2", "h3", "h4"]:
                break
            if getattr(sib, "name", None) in ["p", "span", "div"]:
                sib_text = sib.get_text().strip()
                if sib_text and len(sib_text) < 300:
                    bio_parts.append(sib_text)
            if len(bio_parts) >= 2:
                break

        seen.add(text)
        members.append({"name": text, "bio": " | ".join(bio_parts)})

    return members


def extract_portfolio_names(soup: "BeautifulSoup") -> list:
    """
    Extract portfolio company names from portfolio-page HTML.

    Looks for text in heading and link elements within containers whose class or
    id attributes suggest they are portfolio grids or lists.

    Returns a deduplicated list of company name strings.
    Results are tagged [S] — extracted from HTML, not guessed.
    """
    names = []
    seen = set()

    # Identify portfolio container elements
    portfolio_containers = []
    for tag in soup.find_all(True):
        attrs = " ".join([
            " ".join(tag.get("class", [])),
            tag.get("id", "")
        ]).lower()
        if any(kw in attrs for kw in PORTFOLIO_KEYWORDS):
            portfolio_containers.append(tag)

    # If no labelled containers found, use the whole page
    search_scope = portfolio_containers if portfolio_containers else [soup]

    for container in search_scope:
        for el in container.find_all(["h2", "h3", "h4", "a", "strong"]):
            text = el.get_text().strip()
            # Company names: 1-5 words, not a sentence, not a nav item
            if not text or len(text) > 60 or len(text) < 2:
                continue
            if text.endswith((".", "?", "!")):
                continue
            if text in seen:
                continue
            seen.add(text)
            names.append(text)

    return names


# ---------------------------------------------------------------------------
# Playwright fallback
# ---------------------------------------------------------------------------

def fetch_with_playwright(url: str) -> tuple:
    """Render a JS-heavy page using Playwright. Requires playwright + chromium."""
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
    Scrape a fund website and return structured plain text ready for fund file population.
    """
    session = requests.Session()
    output = []
    output.append(f"FUND: {name}")
    output.append(f"URL:  {url}")
    output.append("=" * 60)

    fetch_results = {}

    # --- Homepage ---
    home_text, home_soup = fetch(url, session)

    if detect_js_only(home_text):
        if use_playwright:
            print("[scraper] Homepage JS-rendered, trying Playwright...", file=sys.stderr)
            home_text, home_soup = fetch_with_playwright(url)
        else:
            output.append(
                "\nWARNING: Homepage returned very little text — site may be JavaScript-rendered.\n"
                "Re-run with --playwright, or check the URL manually.\n"
            )

    if home_text:
        output.append(f"\n--- HOMEPAGE ({url}) ---")
        output.append(home_text[:MAX_CHARS_PER_PAGE])
        fetch_results["homepage"] = "ok"
    else:
        output.append(f"\nERROR: Could not fetch homepage ({url}).")
        return "\n".join(output)

    # --- Sub-pages: try all candidates in order until one returns unique content ---
    fetched_urls = {url}

    for content_type in ["team", "portfolio", "thesis"]:
        candidates = find_sub_page_candidates(url, home_soup, content_type)
        page_written = False

        for sub_url in candidates:
            if sub_url in fetched_urls:
                continue

            time.sleep(POLITE_DELAY)
            print(f"[scraper] Trying {content_type}: {sub_url}", file=sys.stderr)

            text, sub_soup = fetch(sub_url, session)

            # If page is JS-only and Playwright is available, try it
            if detect_js_only(text) and use_playwright:
                text, sub_soup = fetch_with_playwright(sub_url)

            if not text:
                print(f"[scraper] No content at {sub_url}, trying next candidate...", file=sys.stderr)
                continue

            # If SPA duplicate: try Playwright if available, otherwise warn and try next
            if is_spa_duplicate(text, home_text):
                if use_playwright:
                    print(f"[scraper] SPA duplicate detected, trying Playwright...", file=sys.stderr)
                    text, sub_soup = fetch_with_playwright(sub_url)
                    if text and not is_spa_duplicate(text, home_text):
                        pass  # Playwright got real content — fall through to write
                    else:
                        print(f"[scraper] Playwright also returned duplicate, trying next...", file=sys.stderr)
                        continue
                else:
                    print(f"[scraper] SPA duplicate at {sub_url}, trying next candidate...", file=sys.stderr)
                    # Record the SPA hit but keep trying other paths
                    fetch_results.setdefault(content_type, f"spa_duplicate — try --playwright ({sub_url})")
                    continue

            # Got unique, usable content
            output.append(f"\n--- {content_type.upper()} PAGE ({sub_url}) ---")
            output.append(text[:MAX_CHARS_PER_PAGE])
            fetched_urls.add(sub_url)
            fetch_results[content_type] = f"ok ({sub_url})"
            page_written = True

            # Run structured extractors on this page's soup
            if content_type == "team" and sub_soup:
                members = extract_team_members(sub_soup)
                if members:
                    output.append(f"\n--- STRUCTURED TEAM EXTRACTION [S] ({sub_url}) ---")
                    output.append("Names and bios extracted directly from HTML headings:")
                    for m in members:
                        output.append(f"  NAME: {m['name']}")
                        if m["bio"]:
                            output.append(f"  BIO:  {m['bio']}")
                        output.append("")

            if content_type == "portfolio" and sub_soup:
                companies = extract_portfolio_names(sub_soup)
                if companies:
                    output.append(f"\n--- STRUCTURED PORTFOLIO EXTRACTION [S] ({sub_url}) ---")
                    output.append("Company names extracted directly from HTML (portfolio containers):")
                    for c in companies[:80]:  # cap at 80 to avoid flooding context
                        output.append(f"  - {c}")

            break  # Stop trying candidates once we have good content

        if not page_written and content_type not in fetch_results:
            fetch_results[content_type] = "all candidates failed or duplicate"

    # --- Fetch summary ---
    output.append("\n" + "=" * 60)
    output.append("SCRAPE SUMMARY")
    output.append("-" * 40)
    for page, result in fetch_results.items():
        flag = "OK " if result.startswith("ok") else "!!!"
        output.append(f"  {flag}  {page}: {result}")
    output.append(
        "\nSource tagging guide (see _config/data-conventions.md):\n"
        "  [S] — from this scrape (homepage text, structured extraction blocks above)\n"
        "  [M] — filled from AI memory; verify before use in live deals\n"
        "Fields rarely on websites: check size, AUM, fund number, LinkedIn, co-investors."
    )
    output.append("=" * 60)
    output.append("END OF SCRAPE")
    return "\n".join(output)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    # Ensure UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError on non-ASCII chars)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Scrape a VC fund website for VC OS fund population."
    )
    parser.add_argument("--name", required=True, help='Fund name, e.g. "Index Ventures"')
    parser.add_argument("--url",  required=True, help="Fund website URL")
    parser.add_argument("--playwright", action="store_true",
                        help="Use Playwright for JS/SPA sites (pip install playwright && playwright install chromium)")
    args = parser.parse_args()

    result = scrape_fund(args.name, args.url, use_playwright=args.playwright)
    print(result)


if __name__ == "__main__":
    main()
