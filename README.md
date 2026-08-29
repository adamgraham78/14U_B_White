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
14u-week-map.md             the 24-week map in markdown
docs/                       generated site (GitHub Pages serves from here)
data/drills-source.csv      2025-26 B Red export, unmodified
data/drills.csv             normalized: drills tagged to the five areas
scripts/normalize_drills.py source CSV -> data/drills.csv
scripts/build_site.py       week map + drills -> docs/
```

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
