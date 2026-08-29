# 14U B White — Season Curriculum

Coach-facing site: **https://adamgraham78.github.io/14U_B_White/**

One hour a week, half ice, 24 practices. Five areas taught properly instead of
eleven taught badly.

| Area | Blocks |
|---|---|
| Contact & Checking | 18 |
| Triangles | 24 |
| Protect the House | 20 |
| Breakout / Forecheck | 18 |
| Zone Entry | 16 |
| | **96** |

## Layout

```
14u-week-map.md             the season plan in markdown
docs/                       generated site (GitHub Pages serves from here)
data/drills-source.csv      2025-26 B Red export, unmodified
data/drills.csv             normalized: drills tagged to the five areas
data/practices.csv          logged practices, one row per drill
inbox/                      pasted IHS practice text, archived
scripts/normalize_drills.py source CSV -> data/drills.csv
scripts/log_practice.py     pasted IHS text -> data/practices.csv
scripts/fetch_practice.py   Playwright scraper (parked, see below)
scripts/build_site.py       season plan + drills + practices -> docs/
```

## Logging a practice

In Ice Hockey Systems, add separator entries as section headers - any line with
three or more dashes. `(10 min)` in a header is captured as that section's
duration. Anything above the first header is treated as off-ice pre-practice
work. A section named for games with more than one entry is logged as options.

    ----Warm-Up (10 min) ----
    --------- Checking ---------
    --------- Stations ---------
    ---- Small Area Games ----

Copy the drill list, save it to `inbox/week-NN.txt`, then:

```sh
python3 scripts/log_practice.py --week 1 --url <share-url> --title "..." inbox/week-01.txt
python3 scripts/build_site.py
```

`fetch_practice.py` scrapes the same data directly, but IHS sits behind a
Cloudflare challenge that only a real headed Chrome clears, and repeated hits
get rate-limited. It is kept for reference; the paste path is the one to use.

## Editing

The week map lives in the `WEEKS` table in `scripts/build_site.py`, and the area
write-ups live in `AREAS` in the same file. **Edit there, not in `docs/`** — the
HTML is generated and will be overwritten.

```sh
python3 scripts/normalize_drills.py   # only if drills-source.csv changed
python3 scripts/build_site.py         # rebuild docs/
```

`build_site.py` asserts the block count is exactly 96, so the audit table on the
site can't drift from the schedule.

## Known gaps

- **Breakout/Forecheck (7 drills for 18 blocks)** and **Zone Entry (5 for 16)** are
  thin. Needs new drills sourced from IHS before Weeks 11 and 16.
- Individual station blocks aren't yet assigned specific drills.
- Hybrid D-zone pressure read is unscheduled — decide at Week 8 from game evidence.

## Scope

Curriculum only — skills, drills and the practice schedule. No roster, player or
team-specific information belongs in this repo.
