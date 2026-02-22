#!/usr/bin/env python3
"""Scrape player bios from the roster using Playwright and write bio.csv

Usage:
  python3 scrape_bios_playwright.py

Requires: Playwright installed (`pip install playwright` and `playwright install`).
"""
from pathlib import Path
import csv
import sys
from typing import List, Dict

from playwright.sync_api import sync_playwright

HERE = Path(__file__).parent
OUT_CSV = HERE / "bio.csv"
ROSTER_URL = "https://hurstathletics.com/sports/mens-ice-hockey/roster"

HEADERS = [
    "Number",
    "Player",
    "FirstName",
    "LastName",
    "Position",
    "Height",
    "Weight",
    "Class",
    "Hometown",
    "HighSchool",
]


def normalize(s: str) -> str:
    return " ".join(s.replace("\xa0", " ").split()).strip()


def extract_from_profile(page) -> Dict[str, str]:
    data: Dict[str, str] = {h: "" for h in HEADERS}

    # Number
    num_el = page.query_selector("span.sidearm-roster-player-jersey-number")
    if num_el:
        data["Number"] = normalize(num_el.inner_text())

    # Name
    name_el = page.query_selector("span.sidearm-roster-player-name")
    if name_el:
        parts = [normalize(span.inner_text()) for span in name_el.query_selector_all("span")]
        full = " ".join(parts).strip()
        data["Player"] = full
        if parts:
            data["FirstName"] = parts[0]
            data["LastName"] = parts[-1]

    # Image (not used in CSV headers requested, but could be helpful)
    img_el = page.query_selector(".sidearm-roster-player-image img")
    if img_el:
        src = normalize(img_el.get_attribute("src") or "")
        # store image path in HighSchool field if missing - but we don't include it now

    # dt/dd fields in the header info
    dl_elems = page.query_selector_all(".sidearm-roster-player-fields dl")
    for dl in dl_elems:
        dt = dl.query_selector("dt")
        dd = dl.query_selector("dd")
        if not dt or not dd:
            continue
        key = normalize(dt.inner_text()).rstrip(":")
        val = normalize(dd.inner_text())
        if key.lower().startswith("position"):
            data["Position"] = val
        elif key.lower().startswith("height"):
            data["Height"] = val
        elif key.lower().startswith("weight"):
            data["Weight"] = val
        elif key.lower().startswith("class"):
            data["Class"] = val
        elif key.lower().startswith("hometown"):
            data["Hometown"] = val
        elif key.lower().startswith("high school") or key.lower().startswith("highschool"):
            data["HighSchool"] = val

    return data


def gather_profile_links(page) -> List[str]:
    # Select links that look like player profile links under the roster
    anchors = page.query_selector_all('a[href*="/sports/mens-ice-hockey/roster/"]')
    hrefs = []
    for a in anchors:
        href = a.get_attribute("href")
        if not href:
            continue
        # Normalize to absolute
        if href.startswith("/"):
            href = "https://hurstathletics.com" + href
        if href not in hrefs:
            hrefs.append(href)
    return hrefs


def main() -> None:
    rows: List[List[str]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Opening roster page: {ROSTER_URL}")
        page.goto(ROSTER_URL, timeout=60000)
        page.wait_for_selector(".sidearm-roster-player-name", timeout=60000)

        profile_links = gather_profile_links(page)
        print(f"Found {len(profile_links)} profile links")

        for i, url in enumerate(profile_links, start=1):
            try:
                print(f"[{i}/{len(profile_links)}] Visiting {url}")
                page.goto(url, timeout=60000)
                page.wait_for_selector(".sidearm-roster-player-header-details", timeout=30000)
                data = extract_from_profile(page)
                rows.append([data[h] for h in HEADERS])
            except Exception as exc:
                print(f"Failed to scrape {url}: {exc}", file=sys.stderr)

        browser.close()

    # Write CSV
    with OUT_CSV.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(HEADERS)
        writer.writerows(rows)

    print(f"Wrote {len(rows)} bios to {OUT_CSV}")


if __name__ == "__main__":
    main()
