#!/usr/bin/env python3
"""Log an Ice Hockey Systems practice into data/practices.csv.

    ./.venv/bin/python scripts/fetch_practice.py <share-url> --week 1
    ./.venv/bin/python scripts/fetch_practice.py <share-url> --week 1 --dry-run

IHS sits behind a Cloudflare challenge that no plain HTTP client can pass, so
this drives a real Chrome via Playwright. The window is visible on purpose: a
headless browser gets fingerprinted and served the interstitial instead.

Re-running for a week replaces that week's rows, so it is safe to re-log a
practice after editing it in IHS.
"""

import argparse
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "practices.csv"
LIBRARY = ROOT / "data" / "drills.csv"

FIELDS = ["week", "practice", "url", "order", "drill", "drill_url", "notes", "description"]


def scrape(url):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright missing - run: ./.venv/bin/pip install playwright")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, channel="chrome")
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        for _ in range(40):
            if "Just a moment" not in page.title():
                break
            page.wait_for_timeout(1000)
        else:
            browser.close()
            sys.exit("Cloudflare challenge did not clear - try again, or solve it in the window.")
        page.wait_for_timeout(2000)

        title = page.eval_on_selector_all(
            "h1", "els => els.map(e => e.innerText.trim()).filter(Boolean)[0] || ''"
        )
        # Each drill is a Drupal "practice-drill" paragraph. The same drill appears
        # twice (summary list, then the detail block that carries the notes), so
        # blocks are merged by name below.
        blocks = page.eval_on_selector_all(
            ".paragraph--type--practice-drill",
            """els => els.map(el => {
                const a = el.querySelector(".field--name-field-drill-name a");
                const notes = el.querySelector(".field--name-field-my-drill-notes .field__item");
                const details = el.querySelector("details .field__item");
                return {
                    name: a ? a.innerText.trim() : "",
                    url: a ? a.href : "",
                    notes: notes ? notes.innerText.trim() : "",
                    details: details ? details.innerText.trim() : ""
                };
            })""",
        )
        browser.close()

    drills, index = [], {}
    for b in blocks:
        name = b["name"]
        if not name:
            continue
        if name not in index:
            index[name] = {"drill": name, "drill_url": b["url"], "notes": "", "description": ""}
            drills.append(index[name])
        d = index[name]
        for src, dst in (("notes", "notes"), ("details", "description")):
            if b[src] and not d[dst]:
                d[dst] = re.sub(r"\s*\n\s*", " ", b[src]).strip()

    if not drills:
        sys.exit("No drills found on that page - is it a practice share link?")

    return title, drills


def load_rows():
    if not OUT.exists():
        return []
    with OUT.open() as fh:
        return list(csv.DictReader(fh))


def known_drills():
    if not LIBRARY.exists():
        return set()
    with LIBRARY.open() as fh:
        return {r["drill"].strip().lower() for r in csv.DictReader(fh) if r.get("drill")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    title, drills = scrape(args.url)

    print(f"\n{title}   (week {args.week})")
    library = known_drills()
    new = []
    for i, d in enumerate(drills, 1):
        flag = "" if d["drill"].strip().lower() in library else "  [not in library]"
        if flag:
            new.append(d["drill"])
        print(f"  {i}. {d['drill']}{flag}")
        if d["notes"]:
            print(f"     notes: {d['notes'][:100]}")

    if args.dry_run:
        print("\ndry run - nothing written")
        return

    rows = [r for r in load_rows() if int(r["week"]) != args.week]
    for i, d in enumerate(drills, 1):
        rows.append({
            "week": args.week, "practice": title, "url": args.url, "order": i,
            "drill": d["drill"], "drill_url": d["drill_url"],
            "notes": d["notes"], "description": d["description"],
        })
    rows.sort(key=lambda r: (int(r["week"]), int(r["order"])))

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    print(f"\nwrote {len(drills)} drills -> {OUT.relative_to(ROOT)}")
    if new:
        print(f"{len(new)} drill(s) not in the library yet: {', '.join(new)}")
    print("run scripts/build_site.py to refresh the site")


if __name__ == "__main__":
    main()
