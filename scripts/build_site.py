#!/usr/bin/env python3
"""Build the coach-facing site in docs/ from the week map and the drill library.

  python3 scripts/build_site.py

Everything a coach reads is generated from the WEEKS table below plus
data/drills.csv, so the block audit can never drift from the schedule.
"""

import csv
import datetime
import html
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DRILLS = ROOT / "data" / "drills.csv"

SEASON = "2026-27"
TEAM = "14U B White"

AREAS = {
    "CHK": {
        "published": True,
        "name": "Contact &amp; Checking",
        "slug": "checking",
        "blocks": 18,
        # Block 1 of the season - the three checking-only practices.
        "practice_weeks": (1, 3),
        "quote": (
            "Body contact is separating the player from the puck, "
            "not the player from the game.",
            "Bob O&rsquo;Connor, National Coach-In-Chief &middot; "
            "USA Hockey, <i>Introduction to Body Contact</i>",
        ),
        "blurb": "",
        "why": "",
        "intro": (
            "14U is the first year of legal contact, and half the team has never seen it. "
            "They will see real checking in a game after Practice 2."
        ),
        "steps_title": "Focus areas",
        # Four focus areas, not a progression - receiving and delivering run together
        # from Practice 1. The how-to lives in the drills and the on-ice cues.
        "steps": [
            ("Contact confidence", "Weeks 1-2", ""),
            ("Body checks", "Weeks 1-2", ""),
            ("Angling &amp; stick checks", "Week 3", ""),
            ("Body blocks", "Weeks 4-6", ""),
        ],
        # Focus area -> the drills sub-category that trains it.
        "step_drills": {
            "Contact confidence": "Delivering and Receiving Body Contact",
            "Body checks": "Delivering and Receiving Body Contact",
            "Angling &amp; stick checks": "Angling",
            "Body blocks": "Gap Control",
        },
        "say": [
            "Head up - always.",
            "Out of the danger zone.",
            "Move into the checker.",
            "Body contact is separating the player from the puck, not the player from the game.",
        ],
        # Grouped: the two halves of contact are different lessons.
        "errors": {
            "Taking a check": [
                "Skating with your head down. Know who's around you. Don't watch the puck with "
                "pressure near. Head down is how you get leveled.",
                "Into the boards square, feet together. Skates parallel, knees bent, forearm and hip take it.",
                "Turning your back or jumping out of a check. Face it, and move into it low.",
                "Skating in the danger zone with pressure - inside a stick length of the boards. "
                "Get to the boards or get away.",
            ],
            "Delivering a check": [
                "Lunging at the hit. Take an angle. Always.",
                "Hands and elbows above the shoulders. That's a penalty, not a check.",
                "Chasing a hit that isn't there while a teammate is left uncovered.",
                "Gliding once you're alongside him. Skate through the contact or he skates out of it.",
            ],
        },
        "note": "",
    },
    "TRI": {
        "published": False,
        "name": "Triangles",
        "slug": "triangles",
        "blocks": 24,
        "blurb": "Our system <em>with the puck</em>. Always two options at good angles.",
        "why": (
            "Breakout, entry and O-zone problems are usually one problem in three jerseys: players "
            "don't know where to be relative to the puck and each other. Triangles are the grammar. "
            "Every rung above them is this shape run on different ice."
        ),
        "steps": [
            ("Neutral ice - learn the shape", "Weeks 4-7",
             "Two options at good angles, on the move. Passing is the through-line that connects the triangle."),
            ("Our end - breakout support", "Weeks 9-14",
             "The same triangle, formed in our own end while we still have the puck, under forecheck pressure."),
            ("Entry - the trailer", "Weeks 16-18",
             "Triangle carried through the neutral zone with a late option behind the puck."),
            ("O-zone - rotating", "Weeks 22-23",
             "Triangles rotating below the dots. This is cycling - it emerges as the last location, not a new system."),
        ],
        "say": [
            "Where's your support?",
            "Two options, good angles.",
            "Don't stand in his shadow - move to open ice.",
            "Pass and go, don't pass and watch.",
        ],
        "errors": [
            "Puck-watching: three players collapsing to one spot and killing every angle.",
            "Supporting behind the puck-carrier's back where no pass exists.",
            "Standing still to receive. Feet moving, then the puck.",
        ],
        "note": (
            "<b>Triangles are possession only.</b> We form a triangle when we have the puck - never as a way to defend. "
            "The moment we lose it, the shape is irrelevant and the answer is Protect the House. Coaches: if the other team "
            "has the puck, stop saying &ldquo;triangle&rdquo;.<br><br>"
            "Triangles are also a <b>through-line, not a rung</b>. They never get retired - they reappear roughly "
            "every third or fourth week for the whole season, because everything above them depends on the shape holding."
        ),
    },
    "PTH": {
        "published": False,
        "name": "Protect the House (D-Zone System)",
        "slug": "protect-the-house",
        "blocks": 20,
        "blurb": "Defend space, not people. Layers and support.",
        "why": (
            "A kid who doesn't know <em>who</em> to cover still knows <em>where</em> to stand. "
            "That is the whole point with variable turnout and mixed experience - this system survives "
            "any number of skaters in any positions."
        ),
        "steps": [
            ("The House", "Week 8",
             "Faceoff dots down to the posts, up to the top of the circles. That is the only ice that matters. Defend space, not people."),
            ("Layers", "Week 9",
             "A second player behind covers when someone is beaten one-on-one low. Nobody is ever alone."),
            ("Box out &amp; clear", "Week 10",
             "Angle the puck to the outside, front the net, box out, get it out. This is Week 2 run five-on-five."),
        ],
        "say": [
            "Give up the outside, lock the middle.",
            "Who's your layer?",
            "Stick in the lane.",
            "Someone fronts the net - always.",
        ],
        "errors": [
            "Chasing the puck to the corner and vacating the slot.",
            "Both defenders on the same man, nobody in front of the net.",
            "Standing beside a man instead of between him and the net.",
        ],
        "note": (
            "Checking made this easier than it looks. Protect-the-House <em>is</em> Week 3 angling and "
            "Week 4 body blocks run five-on-five - we name the system in Week 8 and find the habits are already there.<br><br>"
            "<b>Known trade-off:</b> this concedes point shots and the outside. If league opponents have a blue-line "
            "bomb, we add one hybrid read (pressure the puck-carrier strong side, everyone else holds). "
            "Decision point is Week 8, from game evidence - not scheduled by default.<br><br>"
            "<b>No triangles in here.</b> Triangles are our shape with the puck. Without it, in our own end, "
            "the only shape is the House and the layer behind it."
        ),
    },
    "BFC": {
        "published": False,
        "name": "Breakout / Forecheck",
        "slug": "breakout-forecheck",
        "blocks": 18,
        "blurb": "Use Triangles for Breakouts, install Forecheck approach (1-2-2 or 2-1-2 - TBD).",
        "why": (
            "Breakout and forecheck are the same picture from opposite ends. Teaching them together means "
            "every rep is contested by definition - no unopposed breakouts that fall apart the moment "
            "a real forechecker arrives."
        ),
        "steps": [
            ("Forecheck - first man angles", "Week 11",
             "F1 takes the angle (Week 1, applied). F2 reads off F1 and takes away the outlet."),
            ("Breakout - triangle under pressure", "Week 12",
             "Support triangle forms in our end the moment we win the puck. D-to-D and the wall option."),
            ("Both ways, live", "Week 13",
             "Retrieval under pressure, first-pass options, and the same drill run in both directions."),
        ],
        "say": [
            "First man takes the angle, second man takes the outlet.",
            "Give him two options before he turns.",
            "Skate the puck out or pass it out - don't ring it and hope.",
            "Lose it? First man back is the layer.",
        ],
        "errors": [
            "Both forwards forechecking the same side, outlet wide open.",
            "The winger leaving the wall early, so the first pass has nowhere to go.",
            "D turning into pressure instead of away from it.",
        ],
        "note": (
            "<b>Drill library is thin here</b> - only 7 tagged drills for 18 blocks. "
            "Needs new drills sourced from IHS before Week 11."
        ),
    },
    "ZE": {
        "published": False,
        "name": "Zone Entry",
        "slug": "zone-entry",
        "blocks": 16,
        "blurb": "Triangles applied to zone entry w/ O-zone options (cycling).",
        "why": (
            "Entries are where offence actually gets generated at this level - not from sustained cycling. "
            "Get in with possession and support, drive the net, and have a shape to fall into if it doesn't produce."
        ),
        "steps": [
            ("Carry &amp; trailer", "Week 16",
             "Triangle through the neutral zone. Someone arrives late, behind the puck."),
            ("The read", "Week 17",
             "Carry it in or put it in. Speed through the line decides which."),
            ("Get to the net", "Week 18",
             "Drive it, shoot it, retrieve it. A rule, not a system - one sentence, no diagrams."),
        ],
        "say": [
            "Speed through the line.",
            "Somebody's late - be the trailer.",
            "Carry it or put it in. Don't drift.",
            "Get to the net.",
        ],
        "errors": [
            "All three entering flat and wide, no trailer, one bad pass from a rush the other way.",
            "Dumping it in with nobody skating to retrieve.",
            "Stopping at the top of the circles instead of driving through the net.",
        ],
        "note": (
            "If the net drive doesn't produce, the fallback is the triangle in the O-zone (Weeks 22-23) - "
            "a shape to rotate into, not a scramble.<br><br>"
            "<b>Drill library is thin here</b> - only 5 tagged drills for 16 blocks. Needs sourcing before Week 16."
        ),
    },
}

# Said every practice, all season. One name, two directions.
THEMES = [
    ("Safe", "Head Up. Out of the danger zone. Meet the hit, don't take it."),
    ("Team First", "Triangle support when attacking, play your zone when defending."),
    ("Net Front", "Crash it on offense, protect it on defense."),
    ("Quick Decisions", "3 seconds max. Move the puck or shoot it."),
]

SEGMENTS = ["Opening game", "Station A", "Station B", "Closing game"]

# week, phase, theme, [(area, description) x4] matching SEGMENTS order
#
# The theme and the per-segment descriptions are NOT published anywhere - they are
# the reference used to build each practice in Ice Hockey Systems. Only the area
# tag reaches the site (as a badge, and in the per-area block counts); real drill
# names appear on the Season Plan once a practice is logged into data/practices.csv.
WEEKS = [
    (1, "Checking only", "Giving &amp; receiving contact",
     [("CHK", "Angling to contact"), ("CHK", "Step forward, absorb it"), ("CHK", "Shoulder to shoulder, both roles"), ("CHK", "Contested wall battles")]),
    (2, "Checking only", "Contact on the wall",
     [("CHK", "Protective posture"), ("CHK", "Take-out check, hips ahead"), ("CHK", "Skates parallel, forearm and hip"), ("CHK", "1v1 wall checks")]),
    (3, "Checking only", "Angling &amp; stick checks",
     [("CHK", "Approach angles"), ("CHK", "Stick on the wrong side"), ("CHK", "Poke, lift, press"), ("CHK", "Angling races")]),
    (4, "Triangles install", "The shape",
     [("CHK", "Body block - steer, don't hit"), ("TRI", "Two options at good angles"), ("TRI", "Holding the system"), ("TRI", "3v3 triangle game")]),
    (5, "Triangles install", "Support angles",
     [("CHK", "Take-out check, live"), ("TRI", "Moving to open ice"), ("TRI", "Receiving in stride"), ("TRI", "3v3 constrained")]),
    (6, "Triangles install", "Passing through the triangle",
     [("CHK", "When not to hit"), ("TRI", "Passing under pressure"), ("TRI", "Give-and-go"), ("TRI", "Small-area keepaway")]),
    (7, "Triangles install", "The moving triangle",
     [("TRI", "System on the move"), ("TRI", "Rotating support"), ("TRI", "Puck movement and timing"), ("TRI", "4v4")]),
    (8, "Protect the House", "The House",
     [("TRI", "Keepaway"), ("PTH", "Defend space, not people"), ("PTH", "Sticks in lanes"), ("PTH", "3v3 low")]),
    (9, "Protect the House", "Layers",
     [("TRI", "Support"), ("PTH", "Second man covers"), ("PTH", "Front the net"), ("PTH", "3v3 with a layer")]),
    (10, "Protect the House", "Box out &amp; clear",
     [("CHK", "Refresher"), ("PTH", "Box-outs, five-on-five"), ("PTH", "Angle it outside"), ("PTH", "Clear the zone")]),
    (11, "Breakout / Forecheck", "Forecheck - first man angles",
     [("TRI", "Support"), ("BFC", "F1 takes the angle"), ("BFC", "F2 reads off F1"), ("BFC", "2v2 forecheck")]),
    (12, "Breakout / Forecheck", "Breakout - triangle under pressure",
     [("PTH", "Box-out"), ("BFC", "Support triangle in our end"), ("BFC", "D-to-D, wall option"), ("BFC", "Breakout vs forecheck")]),
    (13, "Breakout / Forecheck", "Both ways",
     [("TRI", "System"), ("BFC", "Retrieval under pressure"), ("BFC", "First-pass options"), ("BFC", "Live, both directions")]),
    (14, "Pre-break", "Integration",
     [("CHK", "Refresher"), ("PTH", "Layers live"), ("BFC", "Breakout live"), ("PTH", "Full-pressure game")]),
    (15, "Reset", "Reset",
     [("TRI", "System"), ("CHK", "Refresher"), ("TRI", "Support angles"), ("TRI", "3v3")]),
    (16, "Zone entry", "Entry - carry &amp; trailer",
     [("TRI", "Support"), ("ZE", "Triangle through the neutral zone"), ("ZE", "The trailer"), ("ZE", "3v2 entry")]),
    (17, "Zone entry", "Entry - the read",
     [("PTH", "Gap"), ("ZE", "Carry vs dump"), ("ZE", "Speed through the line"), ("ZE", "Live entries")]),
    (18, "Zone entry", "Entry - get to the net",
     [("BFC", "Forecheck"), ("ZE", "Net drive"), ("ZE", "Retrieval off the dump"), ("ZE", "Entry to net-front")]),
    (19, "Spiral", "Forecheck pressure &amp; recovery",
     [("PTH", "Box-out"), ("BFC", "Sustained pressure"), ("BFC", "Losing the puck - react"), ("BFC", "3v3 forecheck")]),
    (20, "Spiral", "D-zone under sustained pressure",
     [("ZE", "Entry game"), ("PTH", "Layers under fatigue"), ("PTH", "Net-front battle"), ("PTH", "4v4 defend")]),
    (21, "Spiral", "Entry vs live D",
     [("PTH", "Gap"), ("ZE", "Against an active gap"), ("ZE", "Support on the entry"), ("ZE", "3v3 transition")]),
    (22, "Spiral", "Breakout to entry, connected",
     [("BFC", "Forecheck"), ("TRI", "Triangle in the O-zone"), ("BFC", "Breakout into entry"), ("BFC", "Full-sequence game")]),
    (23, "Spiral", "O-zone triangles (cycling)",
     [("PTH", "Defend"), ("TRI", "Cycle low-to-high"), ("TRI", "Rotating support"), ("ZE", "Entry into the cycle")]),
    (24, "Spiral", "Integration / playoff prep",
     [("BFC", "Forecheck"), ("ZE", "Live entries"), ("ZE", "Net drive"), ("PTH", "Full-pressure game")]),
]

BREAK_AFTER = 14

# Weekly from 11 Sep 2026. Ice is booked through 27 Nov; the slot after that is
# not yet set, so later weeks carry no date rather than a guess.
# The fixed 5 min checking block rotates through the four steps all season.
CHECKING_CYCLE = ["Contact confidence", "Body checks", "Angling", "Stick checks"]

SEASON_START = datetime.date(2026, 9, 11)
LAST_BOOKED = datetime.date(2026, 11, 27)


def week_date(wk):
    d = SEASON_START + datetime.timedelta(weeks=wk - 1)
    return d if d <= LAST_BOOKED else None

PRACTICES = ROOT / "data" / "practices.csv"

PRACTICE = [
    ("Opening game", "10 min", "Small-area game, full group",
     "Revisit previous focus areas.", False),
    ("Checking", "5 min", "Fixed ritual, every practice",
     "Non-negotiable, like form tackling.", False),
    ("Stations", "20 min", "Two teaching blocks, 10 min each",
     "30-60s demo, then work before rotating.", False),
    ("Station C", "optional", "Shooting, faceoffs, individual skills",
     "Only if a fourth coach shows and numbers allow.", True),
    ("Closing game", "15 min", "High-compete game",
     "The week's theme under full pressure.", False),
]


def esc(s):
    return html.escape(s, quote=False)


def load_practices():
    """week -> {title, url, sections:[{name, minutes, kind, drills:[...]}]}"""
    if not PRACTICES.exists():
        return {}
    with PRACTICES.open() as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("drill")]
    out = {}
    for r in sorted(rows, key=lambda r: (int(r["week"]), int(r["order"]))):
        wk = int(r["week"])
        pr = out.setdefault(wk, {"title": r["practice"], "url": r["url"], "sections": []})
        if not pr["sections"] or pr["sections"][-1]["name"] != r["section"]:
            pr["sections"].append({"name": r["section"], "minutes": r["minutes"],
                                   "kind": r["kind"], "drills": []})
        pr["sections"][-1]["drills"].append(
            {"name": r["drill"], "url": r["drill_url"], "option": r["is_option"] == "yes"})
    return out


def segment_drills(pr):
    """Map a logged practice's sections onto the five segment columns.

    Columns are 0 opening game, 1-3 stations A/B/C, 4 closing game. Pre-practice
    work is off-ice and belongs to no segment.
    """
    out = {}
    for sec in pr["sections"]:
        if sec["kind"] == "prep":
            continue
        items = sec["drills"]
        if re.search(r"check", sec["name"], re.I):
            out.setdefault("check", []).extend(items)
        elif re.search(r"station", sec["name"], re.I):
            for i, d in enumerate(items[:3]):
                out.setdefault(1 + i, []).append(d)
        elif re.search(r"warm|opening", sec["name"], re.I):
            out.setdefault(0, []).extend(items)
        elif re.search(r"game|closing", sec["name"], re.I):
            out.setdefault(4, []).extend(items)
    return out


# Bonus work that sits outside the five focus areas gets its own badge.
SHOOTING = re.compile(r"shot|shoot|release|one[\s-]?timer|snip", re.I)
FACEOFF = re.compile(r"face[\s-]?off", re.I)


def bonus_badge(name):
    if SHOOTING.search(name):
        return pill("SHOOT")
    if FACEOFF.search(name):
        return pill("FO")
    return ""


def drill_html(d):
    name = esc(d["name"])
    inner = f'<a href="{esc(d["url"])}">{name}</a>' if d.get("url") else name
    return f'<div class="dr">{inner}</div>' 


def load_drills():
    if not DRILLS.exists():
        return []
    with DRILLS.open() as fh:
        return [r for r in csv.DictReader(fh) if r.get("drill")]


def pill(area):
    return f'<span class="pill {area}">{area}</span>'


def page(title, body, active, depth=0):
    up = "../" * depth
    nav = [("index.html", "Overview"), ("weeks.html", "Season Plan")]
    nav += [(f"areas/{a['slug']}.html", a["name"])
            for a in AREAS.values() if a["published"]]
    links = "".join(
        '<a href="{}{}"{}>{}</a>'.format(
            up, href, ' aria-current="page"' if label == active else "", label
        )
        for href, label in nav
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &middot; {TEAM}</title>
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<header class="site"><div class="wrap">
<a class="brand" href="{up}index.html">{TEAM} &middot; {SEASON}</a>
<nav>{links}</nav>
</div></header>
<div class="wrap">
{body}
</div>
</body>
</html>
"""


def audit():
    counts = {a: 0 for a in AREAS}
    for _, _, _, segs in WEEKS:
        for area, _ in segs:
            counts[area] += 1
    return counts


def build_index(counts, drills):
    cards = ""
    for i, (tag, a) in enumerate(AREAS.items(), 1):
        n = sum(1 for d in drills if tag in d["areas"].split("|"))
        blurb_p = f"<p>{a['blurb']}</p>" if a["blurb"] else ""
        if a["published"]:
            open_tag = f'<a class="card" style="--tag:var(--{tag.lower()})" href="areas/{a["slug"]}.html">'
            close_tag = "</a>"
            extra = ""
        else:
            open_tag = f'<div class="card" style="--tag:var(--{tag.lower()})">'
            close_tag = "</div>"
            extra = '<span class="seg">in review</span>'
        cards += f"""{open_tag}
<div class="tag">{i} &middot; {tag}</div><h3>{i}. {a['name']}</h3>{blurb_p}
<div class="meta"><span><b>{counts[tag]}</b> blocks</span><span><b>{n}</b> drills</span>{extra}</div>{close_tag}"""

    prows = "".join(
        '<tr{}><td>{}{}{}</td><td class="num">{}</td><td>{}</td>'
        '<td style="color:var(--muted)">{}</td></tr>'.format(
            ' style="color:var(--muted)"' if opt else "",
            "" if opt else "<b>", seg, "" if opt else "</b>", t, fmt, note)
        for seg, t, fmt, note, opt in PRACTICE
    )

    themes = "".join(
        f'<li><b>{name}</b>{line}</li>' for name, line in THEMES
    )

    body = f"""<section class="hero">
<h1>{TEAM} Practice Plan</h1>
<dl class="facts">
<div><dt>Practices</dt><dd>24</dd></div>
<div><dt>Ice per week</dt><dd>50 min</dd></div>
<div><dt>Teaching blocks</dt><dd>96</dd></div>
<div><dt>Areas</dt><dd>5</dd></div>
</dl>
</section>

<h2>Team Themes</h2>
<ol class="steps">{themes}</ol>

<h2>Focus Areas</h2>
<div class="cards">{cards}</div>
<p><a href="weeks.html">See the full season plan &rarr;</a></p>

<h2>Skill Development</h2>
<ul class="rules">
<li><b>Station C, when the coaches are there.</b> An optional station for individual skills.</li>
<li><b>Small-area games build skills too.</b> Passing, stickhandling, shooting and skating are
taught in the drills and games that build each system.</li>
<li><b>Outside sessions.</b> Players are encouraged to attend the weekly O&rsquo;Sullivan Skills
and Driscoll sessions.</li>
</ul>

<h2>Practice Structure</h2>
<div class="scroll"><table>
<thead><tr><th>Segment</th><th class="num">Time</th><th>Format</th><th>Notes</th></tr></thead>
<tbody>{prows}</tbody></table></div>
"""
    return page("Overview", body, "Overview")


def season_table(weeks, practices, phases=True):
    """The Season Plan grid - one row per practice, a column per segment.

    Shared by the Season Plan and the per-area practice lists, so an area page
    shows its practices in exactly the format coaches already read.
    """
    rows = ""
    phase_seen = None
    for wk, phase, theme, segs in weeks:
        if phases and phase != phase_seen:
            rows += f'<tr><td colspan="9" style="background:var(--bg);font-weight:650">{phase}</td></tr>'
            phase_seen = phase
        tags = [pill(a) for a, _ in segs]
        plan = practices.get(wk)
        fills = segment_drills(plan) if plan else {}
        logged = fills.get("check", [])
        if logged:
            check = "<td>" + "".join(drill_html(d) for d in logged) + "</td>"
        else:
            step = CHECKING_CYCLE[(wk - 1) % len(CHECKING_CYCLE)]
            check = (f'<td class="seg" style="text-transform:none;letter-spacing:0">'
                     f'{step}</td>')
        cells = ""
        for col, tag in enumerate([tags[0], tags[1], tags[2], "", tags[3]]):
            items = fills.get(col, [])
            if not tag and not items:
                cells += '<td style="color:var(--muted)">-</td>'
                if col == 0:
                    cells += check
                continue
            badge = tag or " ".join(
                dict.fromkeys(b for b in (bonus_badge(d["name"]) for d in items) if b))
            # Drill names appear only once a practice has actually been logged.
            cells += f'<td>{badge}{"".join(drill_html(d) for d in items)}</td>' 
            if col == 0:
                cells += check
        plan_url = plan["url"] if plan else ""
        cells += (f'<td><a href="{esc(plan_url)}">Plan</a></td>' if plan_url
                  else '<td style="color:var(--muted)">-</td>')
        d = week_date(wk)
        when = (f'<td class="wk" style="font-weight:400">{d.strftime("%a %-d %b")}</td>'
                if d else '<td class="seg">TBD</td>')
        rows += f'<tr><td class="wk">{wk}</td>{when}{cells}</tr>'
        if wk == BREAK_AFTER and wk != weeks[-1][0]:
            rows += ('<tr><td colspan="9" style="background:var(--bg);color:var(--muted)">'
                     '&#127876; Holiday break - minimum 7 days off (ADM)</td></tr>')

    cols = ([SEGMENTS[0], "Checking <span style='font-weight:400;text-transform:none'>(5 min)</span>"]
            + SEGMENTS[1:3]
            + ["Station C <span style='font-weight:400;text-transform:none'>(optional)</span>"]
            + SEGMENTS[3:]
            + ["Practice plan"])
    heads = "".join(f"<th>{c}</th>" for c in cols)
    return f"""<div class="scroll"><table>
<thead><tr><th>Wk</th><th>Date</th>{heads}</tr></thead>
<tbody>{rows}</tbody>
</table></div>"""


def build_weeks(counts, practices):
    audit_rows = "".join(
        f'<tr><td>{pill(t)} {a["name"]}</td><td class="num">{counts[t]}</td>'
        f'<td class="num">{a["blocks"]}</td></tr>'
        for t, a in AREAS.items()
    )
    total = sum(counts.values())

    body = f"""<section class="hero">
<h1>Season Plan</h1>
</section>

{season_table(WEEKS, practices)}

<h2>Block audit</h2>
<div class="scroll"><table>
<thead><tr><th>Area</th><th class="num">Scheduled</th><th class="num">Target</th></tr></thead>
<tbody>{audit_rows}</tbody>
<tfoot><tr><td>Total</td><td class="num">{total}</td><td class="num">96</td></tr></tfoot>
</table></div>
"""
    return page("Season Plan", body, "Season Plan")


def area_practices(tag, practices):
    """The Season Plan rows for this area's practices, in the same format.

    An area names its own week range in AREAS["practice_weeks"]; otherwise every
    week carrying a block in the area is listed.
    """
    weeks = area_weeks(tag)
    if not weeks:
        return ""
    return f"""<h2>Practices</h2>
{season_table(weeks, practices, phases=False)}
<p><a href="../weeks.html">See the full season plan &rarr;</a></p>

"""


def toc_layout(hero, body, tag):
    """Give an area page a sticky side menu built from its own h2 headings."""
    entries = []

    def tag_h2(m):
        text = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        slug = re.sub(r"[^a-z0-9]+", "-", html.unescape(text).lower()).strip("-")
        entries.append((slug, text))
        return f'<h2 id="{slug}">{m.group(1)}</h2>'

    body = re.sub(r"<h2>(.*?)</h2>", tag_h2, body, flags=re.S)
    links = "".join(f'<li><a href="#{slug}">{text}</a></li>' for slug, text in entries)
    return f"""{hero}
<div class="doc" style="--tag:var(--{tag.lower()})">
<nav class="toc" aria-label="On this page"><ol>{links}</ol></nav>
<div class="doc-body">
{body}
</div>
</div>
"""


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", html.unescape(text).lower()).strip("-")


def area_weeks(tag):
    """The weeks this area's practice list covers."""
    span = AREAS[tag].get("practice_weeks")
    if span:
        first, last = span
        return [w for w in WEEKS if first <= w[0] <= last]
    return [w for w in WEEKS if any(a == tag for a, _ in w[3])]


def next_practice_card(tag, practices):
    """The next practice in this area - the one a coach is about to run."""
    today = datetime.date.today()
    upcoming = [w for w in area_weeks(tag)
                if week_date(w[0]) is None or week_date(w[0]) >= today]
    if not upcoming:
        return ""
    wk = upcoming[0][0]
    d = week_date(wk)
    when = d.strftime("%a %-d %b") if d else "date TBD"
    plan = practices.get(wk)
    if plan:
        title = re.sub(rf"^{re.escape(TEAM)}\s*-\s*", "", plan["title"])
        return (f'<a class="next" href="{esc(plan["url"])}">'
                f'<span class="lbl">Next practice</span>'
                f'<b>{esc(title)}</b><span class="when">{when} &middot; Week {wk}</span></a>')
    return ('<div class="next pending">'
            '<span class="lbl">Next practice</span>'
            f'<b>Week {wk}</b><span class="when">{when} &middot; not built yet</span></div>')


def drills_table(tag, mine):
    """Drills grouped by sub-category, so the table reads as sections."""
    def cell(d):
        name = esc(d["drill"])
        return f'<a href="{esc(d["link"])}">{name}</a>' if d["link"] else name

    groups = {}
    for d in mine:
        subs = [x for x in d["subcategories"].split("|") if x]
        groups.setdefault(subs[0] if subs else "Other", []).append(d)
    order = sorted(groups, key=lambda g: (g == "Other", -len(groups[g]), g))

    rows = ""
    for g in order:
        rows += (f'<tr id="d-{slug(g)}"><td colspan="3" '
                 f'style="background:var(--bg);font-weight:650">{esc(g)}</td></tr>')
        for d in sorted(groups[g], key=lambda r: r["drill"]):
            extra = ", ".join(x for x in d["subcategories"].split("|") if x and x != g)
            also = "".join(pill(x) for x in d["areas"].split("|") if x != tag and x)
            rows += ('<tr><td>{}</td><td style="color:var(--muted)">{}</td>'
                     "<td>{}</td></tr>").format(cell(d), esc(extra) or "-", also or "-")
    return f"""<div class="scroll"><table>
<thead><tr><th>Drill</th><th>Also trains</th><th>Also in</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""


def build_area(tag, counts, drills, practices):
    a = AREAS[tag]
    mine = [d for d in drills if tag in d["areas"].split("|")]
    have = {s for d in mine for s in d["subcategories"].split("|") if s}

    def step_name(name):
        # Each focus area jumps to the drills that train it.
        sub = a.get("step_drills", {}).get(name)
        if sub and sub in have:
            return (f'<a href="#d-{slug(sub)}">{name} '
                    f'<span aria-hidden="true">&rarr;</span></a>')
        return name

    steps = "".join(
        f'<li style="--tag:var(--{tag.lower()})"><span class="when">{when}</span>'
        f"<b>{step_name(name)}</b>{desc}</li>"
        for name, when, desc in a["steps"]
    )
    say = "".join(f"<q>{s}</q>" for s in a["say"])

    if isinstance(a["errors"], dict):
        errors = '<div class="cols">' + "".join(
            f"<div><h3>{head}</h3><ul class=\"rules\">"
            + "".join(f"<li>{e}</li>" for e in items) + "</ul></div>"
            for head, items in a["errors"].items()
        ) + "</div>"
    else:
        errors = '<ul class="rules">' + "".join(f"<li>{e}</li>" for e in a["errors"]) + "</ul>"

    drill_html = (drills_table(tag, mine) if mine
                  else '<p class="lede">No drills tagged to this area yet.</p>')

    num = list(AREAS).index(tag) + 1
    blurb_p = f"<p>{a['blurb']}</p>" if a["blurb"] else ""
    intro_p = f'<p class="lede">{a["intro"]}</p>' if a.get("intro") else ""
    note_div = f'<div class="note">{a["note"]}</div>\n\n' if a["note"] else ""
    why_section = (f'<h2>Why this, for this team</h2>\n<p class="lede">{a["why"]}</p>\n\n'
                   if a["why"] else "")

    epigraph = ""
    if a.get("quote"):
        text, source = a["quote"]
        epigraph = (f'<blockquote class="epigraph"><p>&ldquo;{text}&rdquo;</p>'
                    f'<cite>{source}</cite></blockquote>')

    practice_section = area_practices(tag, practices)

    hero = f"""<section class="hero">
<h1>{num}. {a['name']} {pill(tag)}</h1>
{epigraph}
{blurb_p}
<div class="herofoot">
<dl class="facts">
<div><dt>Blocks</dt><dd>{counts[tag]}</dd></div>
<div><dt>Drills</dt><dd>{len(mine)}</dd></div>
</dl>
{next_practice_card(tag, practices)}
</div>
</section>"""

    body = f"""{why_section}<h2>{a.get("steps_title", "The progression")}</h2>
{intro_p}
<ol class="steps">{steps}</ol>

{note_div}{practice_section}<h2>What to say on the ice</h2>
<div class="say">{say}</div>

<h2>What goes wrong</h2>
{errors}

<h2>Drills</h2>
{drill_html}
"""
    return page(a["name"], toc_layout(hero, body, tag), a["name"], depth=1)


def main():
    (DOCS / "areas").mkdir(parents=True, exist_ok=True)
    drills = load_drills()
    practices = load_practices()
    counts = audit()

    (DOCS / "index.html").write_text(build_index(counts, drills))
    (DOCS / "weeks.html").write_text(build_weeks(counts, practices))
    for tag, a in AREAS.items():
        target = DOCS / "areas" / f"{a['slug']}.html"
        if a["published"]:
            target.write_text(build_area(tag, counts, drills, practices))
        elif target.exists():
            target.unlink()

    total = sum(counts.values())
    print(f"built docs/ - {len(WEEKS)} weeks, {total} blocks, {len(drills)} drills, "
          f"{len(practices)} practice plan(s)")
    for tag, n in counts.items():
        flag = "" if n == AREAS[tag]["blocks"] else f"  <-- target {AREAS[tag]['blocks']}"
        print(f"  {tag}: {n}{flag}")
    assert total == 96, f"expected 96 blocks, got {total}"


if __name__ == "__main__":
    main()
