#!/usr/bin/env python3
"""Build the coach-facing site in docs/ from the week map and the drill library.

  python3 scripts/build_site.py

Everything a coach reads is generated from the WEEKS table below plus
data/drills.csv, so the block audit can never drift from the schedule.
"""

import csv
import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DRILLS = ROOT / "data" / "drills.csv"

SEASON = "2026-27"
TEAM = "14U B White"

AREAS = {
    "CHK": {
        "name": "Contact &amp; Checking",
        "slug": "checking",
        "blocks": 18,
        "blurb": "Angling, stick checks, receiving contact, and delivering it. Weeks 1&ndash;3 are contact and nothing else.",
        "why": (
            "14U is the first year of legal contact, and many players arrive with none of it. "
            "Contact is not a unit we bolt on &mdash; it is the first thing we teach, before any system, "
            "because everything else in this curriculum happens with a body arriving."
        ),
        "steps": [
            ("Positioning &amp; angling", "Week 1",
             "Skate to take ice away. Approach on an angle, stick on the wrong side, close without lunging. No contact required to teach this."),
            ("Stick checks &amp; body position", "Week 2",
             "Poke, lift, press. Get your body between the man and the puck. Box-outs and wall pins."),
            ("Receiving contact", "Week 3",
             "Take a hit along the wall with your head up. Absorb into the boards, protective posture, escape pressure. The safety-critical step."),
            ("Delivering contact", "Weeks 4&ndash;6",
             "Legal check: angle plus timing, hands and elbows in control. And the read of when <em>not</em> to hit."),
        ],
        "say": [
            "Take the ice away, not the body.",
            "Head up, shoulder first, into the wall.",
            "Stick on the wrong side.",
            "Finish it or leave it &mdash; don't lunge.",
        ],
        "errors": [
            "Lunging at the hit instead of skating the angle. Costs the puck and the position.",
            "Skating into the boards square and low &mdash; the injury posture. Turn the shoulder, keep the head up.",
            "Chasing a hit that isn't there while a teammate is left uncovered.",
        ],
        "note": (
            "Weeks 1&ndash;3 are checking and nothing else &mdash; no triangles, no systems. "
            "After Week 6 contact becomes a <b>thread</b>: it lives inside battles, games and rotations, "
            "never as a standalone block again. Three refreshers are scheduled at Weeks 10, 14 and 15."
        ),
    },
    "TRI": {
        "name": "Triangles",
        "slug": "triangles",
        "blocks": 24,
        "blurb": "The support shape. Always two options at good angles. Same shape in every zone &mdash; only the ice changes.",
        "why": (
            "Breakout, entry and O-zone problems are usually one problem in three jerseys: players "
            "don't know where to be relative to the puck and each other. Triangles are the grammar. "
            "Every rung above them is this shape run on different ice."
        ),
        "steps": [
            ("Neutral ice &mdash; learn the shape", "Weeks 4&ndash;7",
             "Two options at good angles, on the move. Passing is the through-line that connects the triangle."),
            ("D-zone &mdash; breakout support", "Weeks 9&ndash;14",
             "The same triangle, formed under forecheck pressure."),
            ("Entry &mdash; the trailer", "Weeks 16&ndash;18",
             "Triangle carried through the neutral zone with a late option behind the puck."),
            ("O-zone &mdash; rotating", "Weeks 22&ndash;23",
             "Triangles rotating below the dots. This is cycling &mdash; it emerges as the last location, not a new system."),
        ],
        "say": [
            "Where's your support?",
            "Two options, good angles.",
            "Don't stand in his shadow &mdash; move to open ice.",
            "Pass and go, don't pass and watch.",
        ],
        "errors": [
            "Puck-watching: three players collapsing to one spot and killing every angle.",
            "Supporting behind the puck-carrier's back where no pass exists.",
            "Standing still to receive. Feet moving, then the puck.",
        ],
        "note": (
            "Triangles are a <b>through-line, not a rung</b>. They never get retired &mdash; they reappear roughly "
            "every third or fourth week for the whole season, because everything above them depends on the shape holding."
        ),
    },
    "PTH": {
        "name": "Protect the House",
        "slug": "protect-the-house",
        "blocks": 20,
        "blurb": "Defend space, not people. Give up the outside, lock the middle, always keep a layer behind.",
        "why": (
            "A kid who doesn't know <em>who</em> to cover still knows <em>where</em> to stand. "
            "That is the whole point with variable turnout and mixed experience &mdash; this system survives "
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
            "Someone fronts the net &mdash; always.",
        ],
        "errors": [
            "Chasing the puck to the corner and vacating the slot.",
            "Both defenders on the same man, nobody in front of the net.",
            "Standing beside a man instead of between him and the net.",
        ],
        "note": (
            "Checking made this easier than it looks. Protect-the-House <em>is</em> Week 1&ndash;2 angling and "
            "box-outs run five-on-five &mdash; we name the system in Week 8 and find the habits are already there.<br><br>"
            "<b>Known trade-off:</b> this concedes point shots and the outside. If league opponents have a blue-line "
            "bomb, we add one hybrid read (pressure the puck-carrier strong side, everyone else holds). "
            "Decision point is Week 8, from game evidence &mdash; not scheduled by default."
        ),
    },
    "BFC": {
        "name": "Breakout / Forecheck",
        "slug": "breakout-forecheck",
        "blocks": 18,
        "blurb": "One rung, both directions. The same triangle run under pressure and against pressure.",
        "why": (
            "Breakout and forecheck are the same picture from opposite ends. Teaching them together means "
            "every rep is contested by definition &mdash; no unopposed breakouts that fall apart the moment "
            "a real forechecker arrives."
        ),
        "steps": [
            ("Forecheck &mdash; first man angles", "Week 11",
             "F1 takes the angle (Week 1, applied). F2 reads off F1 and takes away the outlet."),
            ("Breakout &mdash; triangle under pressure", "Week 12",
             "Support triangle forms in the D-zone. D-to-D and the wall option."),
            ("Both ways, live", "Week 13",
             "Retrieval under pressure, first-pass options, and the same drill run in both directions."),
        ],
        "say": [
            "First man takes the angle, second man takes the outlet.",
            "Give him two options before he turns.",
            "Skate the puck out or pass it out &mdash; don't ring it and hope.",
            "Lose it? First man back is the layer.",
        ],
        "errors": [
            "Both forwards forechecking the same side, outlet wide open.",
            "The winger leaving the wall early, so the first pass has nowhere to go.",
            "D turning into pressure instead of away from it.",
        ],
        "note": (
            "<b>Drill library is thin here</b> &mdash; only 7 tagged drills for 18 blocks. "
            "Needs new drills sourced from IHS before Week 11."
        ),
    },
    "ZE": {
        "name": "Zone Entry",
        "slug": "zone-entry",
        "blocks": 16,
        "blurb": "The triangle carried through the neutral zone with a trailer. Then get to the net.",
        "why": (
            "Entries are where offence actually gets generated at this level &mdash; not from sustained cycling. "
            "Get in with possession and support, drive the net, and have a shape to fall into if it doesn't produce."
        ),
        "steps": [
            ("Carry &amp; trailer", "Week 16",
             "Triangle through the neutral zone. Someone arrives late, behind the puck."),
            ("The read", "Week 17",
             "Carry it in or put it in. Speed through the line decides which."),
            ("Get to the net", "Week 18",
             "Drive it, shoot it, retrieve it. A rule, not a system &mdash; one sentence, no diagrams."),
        ],
        "say": [
            "Speed through the line.",
            "Somebody's late &mdash; be the trailer.",
            "Carry it or put it in. Don't drift.",
            "Get to the net.",
        ],
        "errors": [
            "All three entering flat and wide, no trailer, one bad pass from a rush the other way.",
            "Dumping it in with nobody skating to retrieve.",
            "Stopping at the top of the circles instead of driving through the net.",
        ],
        "note": (
            "If the net drive doesn't produce, the fallback is the triangle in the O-zone (Weeks 22&ndash;23) &mdash; "
            "a shape to rotate into, not a scramble.<br><br>"
            "<b>Drill library is thin here</b> &mdash; only 5 tagged drills for 16 blocks. Needs sourcing before Week 16."
        ),
    },
}

SEGMENTS = ["Opening game", "Station A", "Station B", "Closing game"]

# week, phase, theme, [(area, description) x4] matching SEGMENTS order
WEEKS = [
    (1, "Checking only", "Angling &mdash; take the ice away",
     [("CHK", "Approach angles"), ("CHK", "Closing without lunging"), ("CHK", "Stick on the wrong side"), ("CHK", "Angling races")]),
    (2, "Checking only", "Stick checks &amp; body position",
     [("CHK", "Poke, lift, press"), ("CHK", "Body between man and puck"), ("CHK", "Box-outs"), ("CHK", "Wall pins")]),
    (3, "Checking only", "Receiving contact",
     [("CHK", "Protective posture"), ("CHK", "Absorbing into the boards"), ("CHK", "Head up along the wall"), ("CHK", "Contested wall battles")]),
    (4, "Triangles install", "The shape",
     [("CHK", "Angling game"), ("TRI", "Two options at good angles"), ("TRI", "Holding the shape"), ("TRI", "3v3 triangle game")]),
    (5, "Triangles install", "Support angles",
     [("CHK", "Delivering contact"), ("TRI", "Moving to open ice"), ("TRI", "Receiving in stride"), ("TRI", "3v3 constrained")]),
    (6, "Triangles install", "Passing through the triangle",
     [("CHK", "Contact confidence"), ("TRI", "Passing under pressure"), ("TRI", "Give-and-go"), ("TRI", "Small-area keepaway")]),
    (7, "Triangles install", "The moving triangle",
     [("TRI", "Shape on the move"), ("TRI", "Rotating support"), ("TRI", "Puck movement and timing"), ("TRI", "4v4")]),
    (8, "Protect the House", "The House",
     [("TRI", "Keepaway"), ("PTH", "Defend space, not people"), ("PTH", "Sticks in lanes"), ("PTH", "3v3 low")]),
    (9, "Protect the House", "Layers",
     [("TRI", "Support"), ("PTH", "Second man covers"), ("PTH", "Front the net"), ("PTH", "3v3 with a layer")]),
    (10, "Protect the House", "Box out &amp; clear",
     [("CHK", "Refresher"), ("PTH", "Box-outs, five-on-five"), ("PTH", "Angle it outside"), ("PTH", "Clear the zone")]),
    (11, "Breakout / Forecheck", "Forecheck &mdash; first man angles",
     [("TRI", "Support"), ("BFC", "F1 takes the angle"), ("BFC", "F2 reads off F1"), ("BFC", "2v2 forecheck")]),
    (12, "Breakout / Forecheck", "Breakout &mdash; triangle under pressure",
     [("PTH", "Box-out"), ("BFC", "Support triangle in the D-zone"), ("BFC", "D-to-D, wall option"), ("BFC", "Breakout vs forecheck")]),
    (13, "Breakout / Forecheck", "Both ways",
     [("TRI", "Shape"), ("BFC", "Retrieval under pressure"), ("BFC", "First-pass options"), ("BFC", "Live, both directions")]),
    (14, "Pre-break", "Integration",
     [("CHK", "Refresher"), ("PTH", "Layers live"), ("BFC", "Breakout live"), ("PTH", "Full-pressure game")]),
    (15, "Reset", "Reset",
     [("TRI", "Shape"), ("CHK", "Refresher"), ("TRI", "Support angles"), ("TRI", "3v3")]),
    (16, "Zone entry", "Entry &mdash; carry &amp; trailer",
     [("TRI", "Support"), ("ZE", "Triangle through the neutral zone"), ("ZE", "The trailer"), ("ZE", "3v2 entry")]),
    (17, "Zone entry", "Entry &mdash; the read",
     [("PTH", "Gap"), ("ZE", "Carry vs dump"), ("ZE", "Speed through the line"), ("ZE", "Live entries")]),
    (18, "Zone entry", "Entry &mdash; get to the net",
     [("BFC", "Forecheck"), ("ZE", "Net drive"), ("ZE", "Retrieval off the dump"), ("ZE", "Entry to net-front")]),
    (19, "Spiral", "Forecheck pressure &amp; recovery",
     [("PTH", "Box-out"), ("BFC", "Sustained pressure"), ("BFC", "Losing the puck &mdash; react"), ("BFC", "3v3 forecheck")]),
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

PHASES = [
    ("1&ndash;3", "Checking only", "No triangles, no systems. Full practice on contact, all four segments."),
    ("4&ndash;7", "Triangles install", "The support shape on neutral ice. Contact drops to Station A, then to a thread."),
    ("8&ndash;10", "Protect the House", "Name the D-zone system. The habits are already there from checking."),
    ("11&ndash;13", "Breakout / Forecheck", "One rung, both directions. Every rep contested."),
    ("14", "Integration", "Everything live before the break."),
    ("15&ndash;18", "Reset &amp; zone entry", "Shake off the layoff, then the triangle carried up ice."),
    ("19&ndash;24", "Spiral", "Nothing new. Everything revisited under more pressure."),
]

RULES = [
    ("Segments", "Opening game 10 min, Station A ~12, Station B ~12, closing game 15. Two stations; three if a fourth coach shows."),
    ("One <em>install</em> per practice", "Revisits don't count against it. A practice installing breakouts can still revisit triangles in the opening game."),
    ("Never install in the opening game", "It's the late-arrival buffer &mdash; a third of the group may miss the first four minutes. Revisit and compete only."),
    ("The closing game is the week's theme under pressure", "Its area always matches the install."),
    ("Station 3 is bonus only", "Shooting, faceoffs, individual skills, when numbers allow. It is <em>not</em> part of the 96 blocks and nothing in this plan depends on it. A kid who misses it misses nothing."),
    ("Skating and contact are threads", "After Week 6 they live inside games and battles. Never a standalone skating or checking block."),
    ("Position- and number-agnostic", "Everything here runs with any number of skaters in any positions. Absences are expected."),
]


def esc(s):
    return html.escape(s, quote=False)


def load_drills():
    if not DRILLS.exists():
        return []
    with DRILLS.open() as fh:
        return [r for r in csv.DictReader(fh) if r.get("drill")]


def pill(area):
    return f'<span class="pill {area}">{area}</span>'


def page(title, body, active, depth=0):
    up = "../" * depth
    nav = [("index.html", "Overview"), ("weeks.html", "24-week map")]
    nav += [(f"areas/{a['slug']}.html", a["name"]) for a in AREAS.values()]
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
<footer class="site">
<p>Season curriculum for {TEAM}. Built from the week map in <code>scripts/build_site.py</code> &mdash;
edit the plan there and rebuild rather than editing these pages by hand.</p>
</footer>
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
    for tag, a in AREAS.items():
        n = sum(1 for d in drills if tag in d["areas"].split("|"))
        cards += f"""<a class="card" style="--tag:var(--{tag.lower()})" href="areas/{a['slug']}.html">
<div class="tag">{tag}</div><h3>{a['name']}</h3><p>{a['blurb']}</p>
<div class="meta"><span><b>{counts[tag]}</b> blocks</span><span><b>{n}</b> drills</span></div></a>"""

    phases = ""
    for wks, name, desc in PHASES:
        phases += f'<div class="phase"><div class="wks">Wk {wks}</div><div><b>{name}</b><span>{desc}</span></div></div>'
        if name == "Integration":
            phases += '<div class="phase brk"><div class="wks">&mdash;</div><div><b>Holiday break</b><span>Minimum 7 days off (ADM).</span></div></div>'

    rules = "".join(f"<li><b>{t}.</b> {d}</li>" for t, d in RULES)

    body = f"""<section class="hero">
<h1>The season, in five things</h1>
<p>One hour a week, half ice, twenty-four practices. That is not enough time to be
decent at everything, so we are going to be genuinely good at five things and
deliberately ignore the rest.</p>
<dl class="facts">
<div><dt>Practices</dt><dd>24</dd></div>
<div><dt>Ice per week</dt><dd>50 min</dd></div>
<div><dt>Teaching blocks</dt><dd>96</dd></div>
<div><dt>Areas</dt><dd>5</dd></div>
</dl>
</section>

<h2>The five areas</h2>
<p class="lede">Every block in the season is tagged to exactly one of these. Click through for
the progression, the words to say on the ice, and the drills.</p>
<div class="cards">{cards}</div>

<h2>How the year runs</h2>
<p class="lede">Install tight, then spiral. Nothing gets taught once and abandoned &mdash; with absences
every week, a concept that appears in only one block is a concept half the team never saw.</p>
<div class="phases">{phases}</div>

<div class="note"><b>Why checking comes first.</b> It is foundational and it is a safety issue.
14U is the first year of legal contact, and many players arrive with none of it. Weeks 1&ndash;3 are
contact and nothing else &mdash; and it turns out angling and box-outs are most of our D-zone
system anyway, so we are further ahead in Week 8 than it looks.</div>

<h2>Rules for running a practice</h2>
<ul class="rules">{rules}</ul>

<h2>What we are not doing</h2>
<p class="lede">Power play, penalty kill, faceoff plays, set O-zone systems, and dedicated skating
or shooting blocks. Not because they don't matter &mdash; because 50 minutes a week buys five things
done properly or eleven things done badly. Shooting and faceoffs live in the optional Station 3.</p>

<p><a href="weeks.html">See the full 24-week map &rarr;</a></p>
"""
    return page("Overview", body, "Overview")


def build_weeks(counts):
    rows = ""
    phase_seen = None
    for wk, phase, theme, segs in WEEKS:
        if phase != phase_seen:
            rows += f'<tr><td colspan="6" style="background:var(--bg);font-weight:650">{phase}</td></tr>'
            phase_seen = phase
        cells = "".join(f'<td>{pill(a)} {d}</td>' for a, d in segs)
        rows += f'<tr><td class="wk">{wk}</td><td><b>{theme}</b></td>{cells}</tr>'
        if wk == BREAK_AFTER:
            rows += ('<tr><td colspan="6" style="background:var(--bg);color:var(--muted)">'
                     '&#127876; Holiday break &mdash; minimum 7 days off (ADM)</td></tr>')

    heads = "".join(f"<th>{s}</th>" for s in SEGMENTS)
    audit_rows = "".join(
        f'<tr><td>{pill(t)} {a["name"]}</td><td class="num">{counts[t]}</td>'
        f'<td class="num">{a["blocks"]}</td></tr>'
        for t, a in AREAS.items()
    )
    total = sum(counts.values())

    body = f"""<section class="hero">
<h1>24-week map</h1>
<p>Every block of the season. Four segments a practice, ninety-six blocks, each tagged to one area.</p>
</section>

<div class="scroll"><table>
<thead><tr><th>Wk</th><th>Theme</th>{heads}</tr></thead>
<tbody>{rows}</tbody>
</table></div>

<h2>Block audit</h2>
<p class="lede">Counted from the table above, so it cannot drift from the schedule.</p>
<div class="scroll"><table>
<thead><tr><th>Area</th><th class="num">Scheduled</th><th class="num">Target</th></tr></thead>
<tbody>{audit_rows}</tbody>
<tfoot><tr><td>Total</td><td class="num">{total}</td><td class="num">96</td></tr></tfoot>
</table></div>
"""
    return page("24-week map", body, "24-week map")


def build_area(tag, counts, drills):
    a = AREAS[tag]
    steps = "".join(
        f'<li style="--tag:var(--{tag.lower()})"><span class="when">{when}</span><b>{name}</b>{desc}</li>'
        for name, when, desc in a["steps"]
    )
    say = "".join(f"<q>{s}</q>" for s in a["say"])
    errors = "".join(f"<li>{e}</li>" for e in a["errors"])

    wk_rows = ""
    for wk, _, theme, segs in WEEKS:
        hits = [(SEGMENTS[i], d) for i, (ar, d) in enumerate(segs) if ar == tag]
        if not hits:
            continue
        for n, (seg, desc) in enumerate(hits):
            first = (f'<td class="wk" rowspan="{len(hits)}">{wk}</td>'
                     f'<td rowspan="{len(hits)}">{theme}</td>') if n == 0 else ""
            wk_rows += f'<tr>{first}<td class="seg">{seg}</td><td>{desc}</td></tr>'

    mine = [d for d in drills if tag in d["areas"].split("|")]
    if mine:
        def drill_cell(d):
            name = esc(d["drill"])
            if d["link"]:
                return '<a href="{}">{}</a>'.format(esc(d["link"]), name)
            return name

        drow = "".join(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                drill_cell(d),
                esc(d["subcategories"].replace("|", ", ")),
                "".join(pill(x) for x in d["areas"].split("|") if x != tag and x),
            )
            for d in sorted(mine, key=lambda r: r["drill"])
        )
        drill_html = f"""<div class="scroll"><table>
<thead><tr><th>Drill</th><th>Sub-category</th><th>Also</th></tr></thead>
<tbody>{drow}</tbody></table></div>"""
    else:
        drill_html = '<p class="lede">No drills tagged to this area yet.</p>'

    body = f"""<section class="hero">
<h1>{pill(tag)} {a['name']}</h1>
<p>{a['blurb']}</p>
<dl class="facts">
<div><dt>Blocks</dt><dd>{counts[tag]}</dd></div>
<div><dt>Drills</dt><dd>{len(mine)}</dd></div>
</dl>
</section>

<h2>Why this, for this team</h2>
<p class="lede">{a['why']}</p>

<h2>The progression</h2>
<ol class="steps">{steps}</ol>

<div class="note">{a['note']}</div>

<h2>What to say on the ice</h2>
<p class="lede">Same words from every coach. The kids should hear one phrase, not four versions of it.</p>
<div class="say">{say}</div>

<h2>What goes wrong</h2>
<ul class="rules">{errors}</ul>

<h2>Where it appears &mdash; {counts[tag]} blocks</h2>
<div class="scroll"><table>
<thead><tr><th>Wk</th><th>Theme</th><th>Segment</th><th>Focus</th></tr></thead>
<tbody>{wk_rows}</tbody></table></div>

<h2>Drills &mdash; {len(mine)} tagged</h2>
<p class="lede">From the 2025-26 library. Links go to Ice Hockey Systems.</p>
{drill_html}
"""
    return page(a["name"], body, a["name"], depth=1)


def main():
    (DOCS / "areas").mkdir(parents=True, exist_ok=True)
    drills = load_drills()
    counts = audit()

    (DOCS / "index.html").write_text(build_index(counts, drills))
    (DOCS / "weeks.html").write_text(build_weeks(counts))
    for tag in AREAS:
        (DOCS / "areas" / f"{AREAS[tag]['slug']}.html").write_text(build_area(tag, counts, drills))

    total = sum(counts.values())
    print(f"built docs/ - {len(WEEKS)} weeks, {total} blocks, {len(drills)} drills")
    for tag, n in counts.items():
        flag = "" if n == AREAS[tag]["blocks"] else f"  <-- target {AREAS[tag]['blocks']}"
        print(f"  {tag}: {n}{flag}")
    assert total == 96, f"expected 96 blocks, got {total}"


if __name__ == "__main__":
    main()
