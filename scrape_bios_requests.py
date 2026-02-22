#!/usr/bin/env python3
"""Scrape player bios from the roster using requests + BeautifulSoup

This is a fallback when Playwright/browser can't be started. It attempts
to parse profile links from the roster page and then fetches each profile
page to extract the requested fields.

Usage:
  python3 scrape_bios_requests.py

Requires: `pip install -r requirements.txt`
"""
from pathlib import Path
import csv
import time
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

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
    if not s:
        return ""
    return " ".join(s.replace("\xa0", " ").split()).strip()


def get_soup(url: str, session: requests.Session) -> BeautifulSoup:
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def gather_profile_links(soup: BeautifulSoup) -> List[str]:
    anchors = soup.find_all("a", href=True)
    hrefs: List[str] = []
    for a in anchors:
        href = a["href"]
        if "/sports/mens-ice-hockey/roster/" in href and href not in ("/sports/mens-ice-hockey/roster", "https://hurstathletics.com/sports/mens-ice-hockey/roster"):
            if href.startswith("/"):
                href = "https://hurstathletics.com" + href
            if href not in hrefs:
                hrefs.append(href)
    return hrefs


def extract_from_profile(soup: BeautifulSoup) -> Dict[str, str]:
    data = {h: "" for h in HEADERS}

    num_el = soup.select_one("span.sidearm-roster-player-jersey-number")
    if num_el:
        data["Number"] = normalize(num_el.get_text())

    name_el = soup.select_one("span.sidearm-roster-player-name")
    if name_el:
        parts = [normalize(span.get_text()) for span in name_el.find_all("span")]
        if not parts:
            full = normalize(name_el.get_text())
            parts = full.split()
        else:
            full = " ".join(parts).strip()
        data["Player"] = full
        if parts:
            data["FirstName"] = parts[0]
            data["LastName"] = parts[-1]

    # dl fields container
    for dl in soup.select(".sidearm-roster-player-fields dl"):
        dt = dl.find("dt")
        dd = dl.find("dd")
        if not dt or not dd:
            continue
        key = normalize(dt.get_text()).rstrip(":")
        val = normalize(dd.get_text())
        lk = key.lower()
        if lk.startswith("position"):
            data["Position"] = val
        elif lk.startswith("height"):
            data["Height"] = val
        elif lk.startswith("weight"):
            data["Weight"] = val
        elif lk.startswith("class"):
            data["Class"] = val
        elif lk.startswith("hometown"):
            data["Hometown"] = val
        elif lk.startswith("high school") or lk.startswith("highschool"):
            data["HighSchool"] = val

    return data


def main() -> None:
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; bio-scraper/1.0)"})

    print(f"Fetching roster page: {ROSTER_URL}")
    soup = get_soup(ROSTER_URL, session)
    profile_links = gather_profile_links(soup)
    print(f"Found {len(profile_links)} profile links (attempting to fetch each)")

    rows: List[List[str]] = []
    for i, url in enumerate(profile_links, start=1):
        try:
            print(f"[{i}/{len(profile_links)}] {url}")
            psoup = get_soup(url, session)
            data = extract_from_profile(psoup)
            rows.append([data[h] for h in HEADERS])
        except Exception as exc:
            print(f"Failed {url}: {exc}")
        time.sleep(0.5)

    # If we didn't find any links, fall back to scanning roster page for inline player blocks
    if not rows:
        print("No profile pages scraped; attempting to parse roster page entries directly")
        # Try to find roster player blocks on the roster page
        for player_div in soup.select(".sidearm-roster-player"):  # best-effort
            try:
                pdata = extract_from_profile(player_div)
                rows.append([pdata[h] for h in HEADERS])
            except Exception:
                continue

    # Write CSV
    with OUT_CSV.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(HEADERS)
        writer.writerows(rows)

    print(f"Wrote {len(rows)} bios to {OUT_CSV}")


if __name__ == "__main__":
    main()
