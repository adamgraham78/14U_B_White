#!/usr/bin/env python3
"""Log a practice into data/practices.csv from pasted IHS text.

    python3 scripts/log_practice.py --week 1 --url <share-url> inbox/week-01.txt
    pbpaste | python3 scripts/log_practice.py --week 1 --url <share-url> -

Paste the drill list straight out of Ice Hockey Systems. Section headers are the
separator rows you add in IHS as dummy drills - any line with three or more
dashes is treated as a header rather than a drill:

    Body Checking Basics
    ----Warm-Up (10 min) ----
    Chaos
    --------- Stations ---------
    USA Step Forward Drill

A "(10 min)" in a header is captured as that section's duration.

Where a section holds more than one game, every game is logged and flagged as an
option - they are alternatives, not all-of-the-above, so block counts must not
treat them as separate teaching blocks.

Anything before the first header is treated as pre-practice work - reading or
video the players do at home. It is tagged kind=prep, and is neither on-ice time
nor a teaching block. An explicit header (Pre-Watch, Prep, Video) does the same.

Drill links are filled in from data/drills.csv where the name matches; anything
unmatched is reported so it can be added to the library.
"""

import argparse
import csv
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "practices.csv"
LIBRARY = ROOT / "data" / "drills.csv"

FIELDS = ["week", "practice", "url", "order", "section", "minutes",
          "kind", "drill", "is_option", "drill_url"]

HEADER = re.compile(r"^[\s\-–—]*(?=.*-{3,})(.*?)[\s\-–—]*$")
DASHES = re.compile(r"-{3,}")
MINUTES = re.compile(r"\((\d+)\s*(?:min|minutes)\)", re.I)
SKIP = {"drills", "practice notes", "drill"}

# A section is a set of alternatives when its name reads like games.
OPTION_SECTIONS = re.compile(r"\bgames?\b", re.I)

# Off-ice work the players do before practice. Never on-ice time, never a
# teaching block. Anything listed before the first header is assumed to be this.
PREP_SECTIONS = re.compile(r"pre[\s-]*(read|watch|game)|prep|homework|video|watch", re.I)
LEAD_SECTION = "Pre-practice"


def parse(text):
    entries, section, minutes = [], "", ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.lower() in SKIP:
            continue
        if DASHES.search(line):
            name = HEADER.match(line).group(1).strip()
            name = DASHES.sub("", name).strip(" -–—")
            m = MINUTES.search(name)
            minutes = m.group(1) if m else ""
            section = MINUTES.sub("", name).strip()
            continue
        entries.append({"section": section, "minutes": minutes, "drill": line})

    for e in entries:
        if not e["section"]:
            e["section"] = LEAD_SECTION
        e["kind"] = "prep" if PREP_SECTIONS.search(e["section"]) or e["section"] == LEAD_SECTION else "ice"
    return entries


def library_links():
    if not LIBRARY.exists():
        return {}
    with LIBRARY.open() as fh:
        return {r["drill"].strip().lower(): r.get("link", "")
                for r in csv.DictReader(fh) if r.get("drill")}


def load_rows():
    if not OUT.exists():
        return []
    with OUT.open() as fh:
        return list(csv.DictReader(fh))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="file with the pasted drill list, or - for stdin")
    ap.add_argument("--week", type=int, required=True)
    ap.add_argument("--url", default="", help="IHS share link for the practice")
    ap.add_argument("--title", default="", help="practice name (defaults to 'Practice <week>')")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    text = sys.stdin.read() if args.file == "-" else pathlib.Path(args.file).read_text()
    entries = parse(text)
    if not entries:
        sys.exit("No drills found - check the pasted text.")

    title = args.title or f"Practice {args.week}"
    links = library_links()

    # Count drills per section so games can be flagged as alternatives.
    per_section = {}
    for e in entries:
        per_section[e["section"]] = per_section.get(e["section"], 0) + 1

    rows, missing = [], []
    for i, e in enumerate(entries, 1):
        key = e["drill"].strip().lower()
        if key not in links and e["kind"] == "ice":
            missing.append(e["drill"])
        option = (e["kind"] == "ice" and OPTION_SECTIONS.search(e["section"] or "")
                  and per_section[e["section"]] > 1)
        rows.append({
            "week": args.week, "practice": title, "url": args.url, "order": i,
            "section": e["section"], "minutes": e["minutes"], "kind": e["kind"],
            "drill": e["drill"],
            "is_option": "yes" if option else "", "drill_url": links.get(key, ""),
        })

    section = None
    for r in rows:
        if r["section"] != section:
            section = r["section"]
            mins = f"  [{r['minutes']} min]" if r["minutes"] else ""
            tag = "  (off-ice)" if r["kind"] == "prep" else ""
            print(f"\n{section}{mins}{tag}")
        opt = "  (option)" if r["is_option"] else ""
        new = "" if r["drill_url"] or r["kind"] == "prep" else "  [not in library]"
        print(f"  {r['order']:2}. {r['drill']}{opt}{new}")

    if args.dry_run:
        print("\ndry run - nothing written")
        return

    keep = [r for r in load_rows() if int(r["week"]) != args.week]
    keep.extend(rows)
    keep.sort(key=lambda r: (int(r["week"]), int(r["order"])))

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(keep)

    print(f"\nwrote {len(rows)} rows -> {OUT.relative_to(ROOT)}")
    if missing:
        print(f"{len(missing)} not in the library: {', '.join(missing)}")


if __name__ == "__main__":
    main()
