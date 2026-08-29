#!/usr/bin/env python3
"""Normalize the 2025-26 B Red drill export onto the 14U curriculum areas.

Source: adamgraham78/Practice-Drills -> data/drills-source.csv
Output: data/drills.csv  (one row per drill, areas as a pipe-delimited list)

The source Theme and Sub Category columns are multi-valued (comma-separated
inside quoted fields), so both are split before matching.
"""

import csv
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "drills-source.csv"
OUT = ROOT / "data" / "drills.csv"

# area -> (themes that imply it, sub categories that imply it)
AREA_RULES = {
    "CHK": (
        {"Competitive Contact", "Angling"},
        {"Angling", "Delivering and Receiving Body Contact", "Gap Control"},
    ),
    # Triangles are a possession shape only. Every Triangles-tagged drill in the
    # source is an offensive/transition drill, so the tag is safe on either axis.
    "TRI": (
        {"Passing and Receiving", "Puck Control", "Stickhandling", "Triangles"},
        {"Triangles", "Quick Decisions", "One Touch", "Cycling"},
    ),
    "PTH": (
        {"Team Play - Defensive"},
        {"Backcheck", "Gap Control", "Down Low Play"},
    ),
    "BFC": (
        {"Forecheck"},
        {"Breakout", "Forecheck"},
    ),
    "ZE": (
        set(),
        {"Zone Entry"},
    ),
}

# The source export has a fill-down error: three drills inherited the previous
# row's link. Where the correct URL is known it is corrected; where it is not,
# the link is dropped, because a wrong link is worse than none.
LINK_FIXES = {
    "Royal Road Drill": "https://www.icehockeysystems.com/hockey-drills/royal-road-drill",
    "1 v 1 Angle Around The Net Drill": "",
    "Quick Release & Reaction Shooting": "",
}

# Themes that only ever belong in the optional Station C pool.
BONUS_THEMES = {"Shooting", "Goalie", "Fun", "Power Play", "Penalty Kill", "Skating"}
BONUS_SUBS = {"Face-Offs", "Quick Release", "One-Timers", "Snapshot", "Slapshot", "Breakaways"}


def split_multi(value):
    return {part.strip() for part in value.split(",") if part.strip()}


def main():
    rows = list(csv.reader(SRC.open()))
    out = []
    for row in rows[1:]:
        if not row or not row[0].strip():
            continue
        name = row[0].strip()
        themes = split_multi(row[2]) if len(row) > 2 else set()
        subs = split_multi(row[3]) if len(row) > 3 else set()
        link = row[4].strip() if len(row) > 4 else ""
        link = LINK_FIXES.get(name, link)

        areas = []
        for area, (t_match, s_match) in AREA_RULES.items():
            if themes & t_match or subs & s_match:
                areas.append(area)

        # Gap Control is shared: it only counts as contact work when the drill
        # is actually tagged as contact, otherwise it is pure defensive play.
        if "CHK" in areas and "Gap Control" in subs and not (themes & {"Competitive Contact", "Angling"}):
            areas.remove("CHK")

        bonus = bool(themes & BONUS_THEMES or subs & BONUS_SUBS)

        out.append({
            "drill": name,
            "areas": "|".join(areas),
            "bonus": "yes" if bonus else "",
            "themes": "|".join(sorted(themes)),
            "subcategories": "|".join(sorted(subs)),
            "link": link,
        })

    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["drill", "areas", "bonus", "themes", "subcategories", "link"]
        )
        writer.writeheader()
        writer.writerows(out)

    unmapped = [r["drill"] for r in out if not r["areas"] and not r["bonus"]]
    counts = {a: sum(1 for r in out if a in r["areas"].split("|")) for a in AREA_RULES}
    print(f"{len(out)} drills -> {OUT.relative_to(ROOT)}")
    for area, n in counts.items():
        print(f"  {area}: {n}")
    print(f"  bonus (Station 3): {sum(1 for r in out if r['bonus'])}")
    if unmapped:
        print(f"  unmapped: {len(unmapped)} -> {', '.join(unmapped)}")


if __name__ == "__main__":
    main()
