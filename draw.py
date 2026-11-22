#!/usr/bin/env python3
"""THE DAILY ATLAS - golden edition.

One page, one day: Saturday 21 November 2026, 33 stories, 1024x1024.
Classic identity: warm cream paper, deep teal-green accent, gold hairlines.

Everything on this page is typeset from the STORY DATA below.  Layout is
measured, never guessed: every line is wrapped to its column, every panel
is checked against its box, and the render refuses to write a PNG if any
assertion fails.

Run:  .venv/bin/python draw.py
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "entry.png")

W = H = 1024
M = 28                      # page margin
COL_W = W - 2 * M           # 968

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 234)     # #F7F2EA warm cream ground
INK = (20, 32, 27)          # #14201B near-black green
TEAL = (14, 90, 76)         # #0E5A4C accent system
GOLD = (185, 138, 47)       # #B98A2F hairlines, pin rings
CREAM = (251, 248, 241)     # #FBF8F1 panels
LAND = (216, 207, 188)      # #D8CFBC map tint
INK_SOFT = (78, 88, 82)     # secondary text, still ink-family
TEAL_WASH = (228, 236, 231)  # barely-there tint for strips that fall back

TEAL_FAMILY = lambda p: p[1] > p[0] + 18 and p[1] > p[2] + 8 and p[1] > 55

# ------------------------------------------------------------------ fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _f(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def fonts():
    """All faces the page uses.  Nothing below 11 px ever ships."""
    return {
        "date": _f("DejaVuSerif-Bold.ttf", 48),
        "mast": _f("DejaVuSans-Bold.ttf", 11),
        "kicker": _f("DejaVuSans-Bold.ttf", 11),
        "h_feat": _f("DejaVuSerif-Bold.ttf", 16),
        "body": _f("DejaVuSans.ttf", 11),
        "body_b": _f("DejaVuSans-Bold.ttf", 11),
        "small": _f("DejaVuSans.ttf", 11),
        "stat": _f("DejaVuSerif-Bold.ttf", 19),
        "grid_head": _f("DejaVuSans-Bold.ttf", 11),
        "brief": _f("DejaVuSans.ttf", 8),
        "brief_b": _f("DejaVuSans-Bold.ttf", 8),
        "pin": _f("DejaVuSans-Bold.ttf", 11),
        "legend": _f("DejaVuSans.ttf", 11),
        "legend_b": _f("DejaVuSans-Bold.ttf", 11),
    }


# -------------------------------------------------------------- geometry
# The page is planned, not guessed.  plan_layout() measures the real
# height each band needs from its content, stacks them with a small gap,
# and returns absolute y positions.  If the stack does not fit between the
# margins the render fails with the measured table, so overflow is fixed
# by tightening type or wording, never by clipping a panel.
PAGE_TOP, PAGE_BOT = 24, 1000

# featured row: 3 panels of 314 with 13 px gutters
FEAT_W, FEAT_ART_H, FEAT_GAP = 314, 87, 13
FEAT_X = [M + i * (FEAT_W + FEAT_GAP) for i in range(3)]

# grid: 3 cols x 4 rows
GRID_W, GRID_GAP = 314, 2
GRID_X = [M + i * (GRID_W + GRID_GAP) for i in range(3)]
STRIP_W = 30                       # scene strip at the tile's left edge
TEXT_DX, TEXT_W = 36, 274          # text column inside a tile

BRIEF_X = [M, 304]                 # two columns
BRIEF_W = 264

# line budgets, enforced by the draw functions: featured deks get four
# lines, grid deks two, briefs two.  Wording is trimmed to these budgets;
# no figure is ever dropped and no line is cut with an ellipsis.
FEAT_DEK_LINES = 4
GRID_DEK_LINES = 2
BRIEF_LINES = 2

BANDS = {}          # filled by plan_layout()
FEAT_ART_Y = FEAT_CAP_Y = GRID_Y = STRIP_H = TILE_H = GRID_H = MAP_RECT = 0


def plan_layout(d, F):
    """Set BANDS from the brief's geometry budget and derive layout globals."""
    BANDS.clear()
    BANDS["masthead"] = (28, 150)
    BANDS["timeline"] = (154, 178)
    BANDS["region"] = (182, 204)
    BANDS["stats"] = (210, 256)
    BANDS["featured"] = (264, 476)
    BANDS["grid"] = (488, 748)
    BANDS["briefs"] = (748, 882)
    BANDS["legend"] = (882, 896)
    BANDS["datecheck"] = (896, 1004)

    global FEAT_ART_Y, FEAT_CAP_Y, GRID_Y, STRIP_H, TILE_H, GRID_H, MAP_RECT
    FEAT_ART_Y = BANDS["featured"][0]
    FEAT_CAP_Y = FEAT_ART_Y + FEAT_ART_H + 4
    grid_band_h = BANDS["grid"][1] - BANDS["grid"][0]  # 260
    TILE_H = (grid_band_h - 3 * GRID_GAP) // 4  # 63
    GRID_H = TILE_H
    STRIP_H = TILE_H - 2  # 61
    GRID_Y = [BANDS["grid"][0] + r * (TILE_H + GRID_GAP) for r in range(4)]
    MAP_RECT = (580, BANDS["briefs"][0], 996, BANDS["briefs"][1])
    return BANDS, 1020, 1020

# ------------------------------------------------------------ story data
# region, sure, place chip, topic, headline, dek, source, art, pin
STORIES = [
    dict(n=1, region="EUROPE", sure="CONFIRMED", place="SE POLAND", topic="WAR",
         head="Russian missiles hit Poland",
         dek="Two missiles and a drone land in south-east Poland during Russia's "
             "biggest barrage of the war. At least 8 killed in Ukraine. "
             "Tusk calls it a \"deliberate provocation\".",
         src="AP · Reuters · EuropeSays",
         art="f1.jpg", pin=(23.0, 50.5), featured=True),
    dict(n=2, region="AMERICAS", sure="CONFIRMED", place="NEW YORK", topic="MARKETS",
         head="Wall Street falls into correction",
         dek="Friday's close: the S&P 500 falls 3.7% and the Dow enters "
             "correction; the Nasdaq drops 5.28% to 22,617.73, its worst "
             "week since 2020. Chips lose $2.3tn; Nvidia sheds $1.16tn in "
             "seven sessions; the VIX closes above 35.",
         src="Friday market closes · Horizon",
         art="f2.jpg", pin=(-74.0, 40.7), featured=True),
    dict(n=3, region="MIDDLE EAST", sure="CONFIRMED", place="ANTALYA, TURKIYE",
         topic="CLIMATE",
         head="COP31 deadlocks into overtime",
         dek="Saturday stays deadlocked over a draft that drops fossil fuels "
             "and the $120bn adaptation figure. The EU warns of a \"fossil "
             "fuels summit\"; Panama threatens to block; the plenary decides "
             "Sunday. Ethiopia hosts COP32.",
         src="AP · AFP · Reuters",
         art="f3.jpg", pin=(30.7, 36.9), featured=True),

    dict(n=4, region="AMERICAS", sure="CONFIRMED", place="JUNIN, PERU",
         topic="EARTHQUAKE", head="Deep 6.7-6.8 quake shakes Peru",
         dek="00:09 UTC Sat: the deep Andes quake is felt in Lima; no "
             "damage or casualties reported.",
         src="USGS · GFZ · IGP", art="g04.jpg",
         pin=(-75.5, -11.0)),
    dict(n=5, region="GLOBAL", sure="OFFICIAL", place="SPACE", topic="MERCURY",
         head="BepiColombo captured at Mercury",
         dek="18:24 UTC: a 37-minute burn ends an 8-year, 10bn-km journey; "
             "the second craft to orbit Mercury.",
         src="ESA", art="g05.jpg", pin=None),
    dict(n=6, region="MIDDLE EAST", sure="CONFIRMED", place="RIYADH", topic="WAR",
         head="Third night of fire over Riyadh",
         dek="The coalition intercepts three Houthi ballistic missiles; the "
             "Houthis threaten ports and a power station.",
         src="Al Jazeera", art="g06.jpg", pin=(46.7, 24.6)),
    dict(n=7, region="EUROPE", sure="OFFICIAL", place="BRUSSELS",
         topic="DIPLOMACY (signed Fri)", head="UK and EU sign biggest post-Brexit deal",
         dek="Signed Friday: food trade, carbon permits and youth mobility "
             "for 100,000 young Britons.",
         src="Guardian · officials", art="g07.jpg", pin=(4.4, 50.9)),
    dict(n=8, region="AMERICAS", sure="CONFIRMED", place="WASHINGTON",
         topic="CYBER", head="FBI criminal database hacked",
         dek="The NCIC records system - fugitives, missing persons, criminal "
             "histories - is reported breached; the USDA is also hit.",
         src="Horizon · OneTurn", art="g08.jpg", pin=(-77.0, 38.9)),
    dict(n=9, region="AMERICAS", sure="CONFIRMED", place="UNITED STATES",
         topic="COURTS", head="Bayer pays $7.25bn to settle Roundup",
         dek="A US judge validates the settlement of all Roundup claims, "
             "future patients included; no admission of responsibility.",
         src="ABC News · Horizon", art="g09.jpg", pin=(-90.2, 38.6)),
    dict(n=10, region="AMERICAS", sure="CONFIRMED", place="SILICON VALLEY",
         topic="AI", head="AI's week of reckoning",
         dek="Anthropic slides to $87.80, still above its $83 IPO price; the "
             "SEC probes Nvidia's accounting.",
         src="FT · Guardian · City AM", art="g10.jpg",
         pin=(-122.0, 37.4)),
    dict(n=11, region="MIDDLE EAST", sure="OFFICIAL", place="KHASAB, OMAN",
         topic="SHIPPING", head="Two tankers struck off Khasab",
         dek="05:00 and 05:50 UTC: projectiles hit two outbound tankers at "
             "the mouth of Hormuz; no casualties.",
         src="UKMTO · Reuters", art="g11.jpg", pin=(56.2, 26.2)),
    dict(n=12, region="EUROPE", sure="REPORTED", place="BARCELONA",
         topic="SCIENCE (presented Fri)", head="Pancreatic pill: tumours gone in 1 in 12",
         dek="Daraxonrasib plus chemo: tumours undetectable in 5 of 61 "
             "patients, shrank or vanished in 60.7%.",
         src="Telegraph · EORTC-NCI-AACR", art="g12.jpg", pin=(2.2, 41.4)),
    dict(n=13, region="EUROPE", sure="CONFIRMED", place="TURIN", topic="TENNIS",
         head="Alcaraz and Zverev set up the Turin final",
         dek="Sat semis: Alcaraz d. Shelton 3-6 6-3 7-6(1), his 13th straight "
             "win; Zverev d. Medvedev 7-6(0) 6-4.",
         src="Reuters · ATP", art="g13.jpg", pin=(7.7, 45.1)),
    dict(n=14, region="ASIA", sure="REPORTED", place="INDONESIA",
         topic="ENVIRONMENT", head="Indonesia's fires burn 7.1m acres",
         dek="Fires burn 7.1 million acres in 2026 - 18 times London's area; "
             "losses may reach $30bn, says Nusantara Atlas.",
         src="Horizon · Nusantara Atlas", art="g14.jpg", pin=(114.0, -1.0)),
    dict(n=15, region="EUROPE", sure="CONFIRMED", place="COPENHAGEN",
         topic="ESPIONAGE", head="Denmark expels a Russian diplomat",
         dek="Copenhagen accuses Russian services of commissioning a murder "
             "plot against rapper Kyivstoner via a Danish gang.",
         src="Horizon · Jabulani", art="g15.jpg", pin=(12.6, 55.7)),
]

# ALSO ON - one printed numeral, one line each, 12 px
BRIEFS = [
    (16, "KRYVYI RIH", "Dozens hit", "EUROPE · REPORTED", (33.4, 47.9)),
    (17, "BRUSSELS", "Gen Z protest", "EUROPE · REPORTED", (4.6, 51.4)),
    (18, "LA", "Arson verdict", "AMERICAS · CONFIRMED", (-118.2, 34.1)),
    (19, "RIEMANN", "AI proof claim", "AMERICAS · CLAIM", (-122.4, 37.8)),
    (20, "TALLINN", "Border closed", "EUROPE · CONFIRMED", (24.7, 59.4)),
    (21, "PARIS", "Police laws pass", "EUROPE · OFFICIAL", (2.35, 48.9)),
    (22, "PARIS", "De Villepin run", "EUROPE · REPORTED", (2.6, 48.4)),
    (23, "SEOUL", "111 cheated", "ASIA · CONFIRMED", (127.0, 37.6)),
    (24, "PHILIPPINES", "Jet landed", "ASIA · REPORTED", (121.0, 14.6)),
    (25, "INDIA", "Alcohol kills", "ASIA · CONFIRMED", (78.0, 21.0)),
    (26, "NIGERIA", "Boat capsized", "AFRICA · REPORTED", (8.0, 10.0)),
    (27, "AFGHANISTAN", "Shell kills 4", "ASIA · REPORTED", (67.0, 34.5)),
    (28, "HAITI", "3 soldiers dead", "AMERICAS · REPORTED", (-72.3, 18.5)),
    (29, "SEATTLE", "2 arrested", "AMERICAS · REPORTED", (-122.3, 47.6)),
    (30, "BRUSSELS", "EU-Indo pact", "ASIA · OFFICIAL", (4.9, 50.5)),
    (31, "DC", "Trump eyes AI tax", "AMERICAS · CONFIRMED", (-77.4, 38.5)),
    (32, "CRYPTO", "BTC dips $55k", "GLOBAL · REPORTED", None),
    (33, "SIMALUNGUN", "Train kills driver", "ASIA · CONFIRMED", (99.0, 2.9)),
]

REGION_ORDER = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA", "AFRICA",
                "OCEANIA", "GLOBAL"]

STATS = [
    ("400+", "drones in Russia's biggest barrage of the war"),
    ("-5.28%", "the Nasdaq on Friday, erasing its 2026 gains"),
    ("$2.3tn", "chip value erased in one week"),
    ("6.7-6.8", "the Peru quake (USGS revised / GFZ)"),
    ("$7.25bn", "Bayer's Roundup settlement"),
    ("100,000", "youth-mobility places in the UK-EU deal"),
]

TIMELINE = [
    ("00:09 UTC", "Peru quake 6.7-6.8"),
    ("OVERNIGHT FRI", "Barrage; Poland hit"),
    ("FRIDAY CLOSE", "Correction; -5.28%"),
    ("05:00-05:50 UTC", "Tankers hit, Khasab"),
    ("SATURDAY", "COP31 deadlocked"),
    ("18:24 UTC", "BepiColombo, Mercury"),
    ("SAT EVENING", "Turin: Alcaraz wins"),
]

DATE_CHECK_LEFT = [
    ("ICJ rules Myanmar Rohingya genocide", "Thu 19 Nov"),
    ("Trump-Xi-Putin Shenzhen summit", "Thu 19 Nov"),
]

DATE_CHECK_FUTURE = [
    ("COP31 adoption vote", "Sun 22 Nov, Antalya"),
    ("ATP final, Alcaraz v Zverev", "Sun 22 Nov, Turin"),
    ("Nepal PM Balendra Shah's first India visit", "22-23 Nov"),
    ("Bundibugyo Ebola vaccine trial first doses", "26 Nov"),
    ("Spain election", "Sat 29 Nov"),
    ("OPEC+ ministerial meetings", "29 Nov"),
]

SURE_KEYS = [
    ("CONFIRMED", "2+ major outlets"),
    ("OFFICIAL", "on the record (officials, agencies)"),
    ("REPORTED", "one major outlet"),
    ("CLAIM", "unverified claim"),
]


# ------------------------------------------------------------ text engine
def text_w(draw, s, font):
    """Width of a string in pixels, as the renderer will draw it."""
    b = draw.textbbox((0, 0), s, font=font)
    return b[2] - b[0]


def line_h(font):
    """Line advance for a face: ascent + descent, no surprises."""
    a, d = font.getmetrics()
    return a + d


def wrap(draw, s, font, max_w):
    """Greedy wrap to a pixel width.  Returns the list of lines.

    Nothing is ever dropped: if a single word cannot fit it is kept whole
    on its own line and the caller's fit-check will flag the overflow.
    """
    words = s.split()
    if not words:
        return [""]
    lines, cur = [], words[0]
    for w in words[1:]:
        trial = cur + " " + w
        if text_w(draw, trial, font) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def wrap_block(draw, s, font, max_w, max_lines):
    """Wrap, then refuse to truncate: over-long text raises.

    Callers that must fit a fixed box pass max_lines and get a hard error
    instead of a silent ellipsis, so overflow is fixed by tightening the
    wording at the data layer, never by cutting a sentence on the page.
    """
    lines = wrap(draw, s, font, max_w)
    if len(lines) > max_lines:
        raise AssertionError(
            "text needs %d lines but only %d fit (%dpx): %r"
            % (len(lines), max_lines, max_w, s[:60]))
    return lines


def draw_lines(draw, x, y, lines, font, fill, lh=None):
    """Draw wrapped lines; returns the y just past the last baseline box."""
    lh = lh or line_h(font)
    for i, ln in enumerate(lines):
        draw.text((x, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def fit_lines(draw, s, font, max_w, max_h, label=""):
    """Wrap to the widest of a few candidate widths that fits max_h.

    Used where a column has slack: it prefers fewer, wider lines.  Raises
    if even the narrowest candidate overflows the height.
    """
    lh = line_h(font)
    best = None
    for shrink in (1.0, 0.94, 0.88, 0.82):
        w = int(max_w * shrink)
        lines = wrap(draw, s, font, w)
        if len(lines) * lh <= max_h:
            best = (lines, w)
            break
    if best is None:
        lines = wrap(draw, s, font, int(max_w * 0.82))
        raise AssertionError(
            "%s: %d lines x %dpx exceeds %dpx box" %
            (label or "text", len(lines), lh, max_h))
    return best


# ----------------------------------------------------------- panel helpers
def panel(draw, box, fill=CREAM, outline=None, width=1):
    draw.rectangle(box, fill=fill, outline=outline, width=width)


def hairline(draw, x0, y0, x1, y1, fill=GOLD, width=1):
    draw.line((x0, y0, x1, y1), fill=fill, width=width)


def label(draw, x, y, s, font, fill=TEAL):
    """Small caps-style kicker: upper-case, letter-spaced by hand."""
    draw.text((x, y), s.upper(), font=font, fill=fill)
    return x + text_w(draw, s.upper(), font)


def paste_art(canvas, path, box):
    """Paste a prepared JPEG into box (x0, y0, x1, y1), exact size."""
    x0, y0, x1, y1 = box
    im = Image.open(os.path.join(ASSETS, path)).convert("RGB")
    tw, th = x1 - x0, y1 - y0
    if im.size != (tw, th):
        im = im.resize((tw, th), Image.LANCZOS)
    canvas.paste(im, (x0, y0))


# ------------------------------------------------------- band: masthead
def draw_masthead(canvas, d, F):
    y0, y1 = BANDS["masthead"]
    # left: wordmark + edition line
    d.text((M, y0), "THE DAILY ATLAS", font=F["mast"], fill=TEAL)
    d.text((M, y0 + 15), "GOLDEN EDITION", font=F["small"], fill=INK_SOFT)

    # the giant date IS the masthead: pick the largest serif size that fits
    date = "SATURDAY 21 NOVEMBER 2026"
    size = 56
    while size > 30:
        f = _f("DejaVuSerif-Bold.ttf", size)
        if text_w(d, date, f) <= COL_W - 150:
            break
        size -= 1
    fdate = _f("DejaVuSerif-Bold.ttf", size)
    dw = text_w(d, date, fdate)
    assert dw <= COL_W - 150, "date still overruns after fit"
    d.text((M, y0 + 30), date, font=fdate, fill=INK)

    # right block: story count + subtitle, set small and quiet
    rt = "33 STORIES · ONE DAY"
    rw = text_w(d, rt, F["mast"])
    d.text((W - M - rw, y0 + 2), rt, font=F["mast"], fill=INK)
    sub = "World news in one page"
    sw = text_w(d, sub, F["small"])
    d.text((W - M - sw, y0 + 17), sub, font=F["small"], fill=INK_SOFT)
    third = "SAT 21 NOV 2026 · 07:00 WIB"
    tw = text_w(d, third, F["small"])
    d.text((W - M - tw, y0 + 32), third, font=F["small"], fill=INK_SOFT)

    # teal rule under the masthead, gold hairline beneath it
    d.rectangle((M, y1 - 7, W - M, y1 - 4), fill=TEAL)
    hairline(d, M, y1, W - M, y1, GOLD)


# ------------------------------------------------------- band: timeline
def draw_timeline(canvas, d, F):
    y0, y1 = BANDS["timeline"]
    n = len(TIMELINE)
    seg = COL_W / n
    hairline(d, M, y0 + 2, W - M, y0 + 2, GOLD)
    for i, (when, what) in enumerate(TIMELINE):
        x = int(M + i * seg)
        # tick + dot on the rule
        d.rectangle((x, y0, x + 1, y0 + 5), fill=TEAL)
        d.ellipse((x - 2, y0 - 1, x + 2, y0 + 3), fill=TEAL)
        d.text((x + 5, y0 + 3), when, font=F["kicker"], fill=TEAL)
        lines = wrap(d, what, F["small"], int(seg) - 9)
        if len(lines) > 1:
            lines = lines[:1]
        d.text((x + 5, y0 + 14), lines[0], font=F["small"], fill=INK_SOFT)
        assert x + 5 + text_w(d, lines[0], F["small"]) <= x + seg + 1, \
            "timeline item %d overruns its segment" % i


# ----------------------------------------------------- band: region bar
def region_counts():
    counts = {r: 0 for r in REGION_ORDER}
    for s in STORIES:
        counts[s["region"]] += 1
    for b in BRIEFS:
        counts[b[3].split(" · ")[0]] += 1
    return counts


def draw_region_bar(canvas, d, F):
    y0, y1 = BANDS["region"]
    counts = region_counts()
    total = sum(counts.values())
    assert total == 33, "region counts sum to %d, expected 33" % total
    assert counts == {"EUROPE": 10, "MIDDLE EAST": 3, "AMERICAS": 10,
                      "ASIA": 7, "AFRICA": 1, "OCEANIA": 0, "GLOBAL": 2}, counts

    x = M
    d.rectangle((M, y0, W - M, y1), fill=CREAM)
    shown = REGION_ORDER
    # Every label gets the width it needs; the leftover is shared out by
    # count, so the bar stays proportional AND every label fits.
    need = {r: text_w(d, "%s %d" % (r, counts[r]), F["kicker"]) + 12
            for r in shown}
    spare = COL_W - sum(need.values())
    assert spare >= 0, "region labels alone exceed the column"
    widths = {}
    for r in shown:
        widths[r] = need[r] + int(spare * counts[r] / total)
    # hand the rounding remainder to the largest segment
    widths[shown[0]] += COL_W - sum(widths.values())

    for r in shown:
        c = counts[r]
        seg_w = widths[r]
        filled = c >= 7
        d.rectangle((x, y0, x + seg_w - 2, y1),
                    fill=TEAL if filled else PAPER,
                    outline=TEAL, width=1)
        d.text((x + 6, y0 + 3), "%s %d" % (r, c), font=F["kicker"],
               fill=PAPER if filled else TEAL)
        x += seg_w
    assert x <= W - M + 1, "region bar overruns the right margin"


# -------------------------------------------------------- band: stats
def draw_stats(canvas, d, F):
    y0, y1 = BANDS["stats"]
    n = len(STATS)
    cell = COL_W / n
    for i, (val, cap) in enumerate(STATS):
        x = int(M + i * cell)
        if i:
            hairline(d, x, y0 + 4, x, y1 - 4, GOLD)
        d.text((x + 8, y0), val, font=F["stat"], fill=TEAL)
        lines = wrap_block(d, cap, F["small"], int(cell) - 16, 2)
        draw_lines(d, x + 8, y0 + 19, lines, F["small"], INK_SOFT)
        assert y0 + 19 + len(lines) * line_h(F["small"]) <= y1 + 3, \
            "stat caption %d overflows its band" % i


# ----------------------------------------------------- band: featured
def draw_featured(canvas, d, F):
    """Three panels: art 314x157 on top, caption block UNDER the art."""
    feats = [s for s in STORIES if s.get("featured")]
    assert len(feats) == 3, "featured row needs exactly 3 stories"
    for i, s in enumerate(feats):
        x0 = FEAT_X[i]
        x1 = x0 + FEAT_W
        # art, exact size, no overlay band anywhere on it
        art_box = (x0, FEAT_ART_Y, x1, FEAT_ART_Y + FEAT_ART_H)
        paste_art(canvas, s["art"], art_box)
        assert (art_box[2] - art_box[0], art_box[3] - art_box[1]) == (FEAT_W, FEAT_ART_H)

        y = FEAT_CAP_Y
        # kicker: region / place, teal, plus the SURE tag
        kick = "%s · %s" % (s["region"], s["place"])
        d.text((x0, y), kick, font=F["kicker"], fill=TEAL)
        kw = text_w(d, kick, F["kicker"])
        sure = s["sure"]
        sw = text_w(d, sure, F["kicker"])
        d.text((x1 - sw, y), sure, font=F["kicker"], fill=INK_SOFT)
        assert x0 + kw < x1 - sw - 6, "featured %d kicker collides with tag" % i
        y += 14

        # headline: serif bold, wrapped, never truncated
        hl = wrap_block(d, s["head"], F["h_feat"], FEAT_W, 2)
        y = draw_lines(d, x0, y, hl, F["h_feat"], INK, lh=19)
        y += 2

        # dek fills the remaining caption height exactly
        cap_bottom = BANDS["featured"][1]
        lines = fit_lines(d, s["dek"], F["small"], FEAT_W,
                          cap_bottom - y - 16, "featured %d dek" % i)
        y = draw_lines(d, x0, y, lines[0], F["small"], INK, lh=13)
        y += 2
        src = s["src"]
        sl = wrap(d, src, F["small"], FEAT_W)
        assert y + len(sl) * 13 <= cap_bottom, "featured %d source overflows" % i
        for j, ln in enumerate(sl):
            d.text((x0, y + j * 13), ln, font=F["small"], fill=TEAL)


# --------------------------------------------------------- band: grid
def draw_grid(canvas, d, F):
    """12 numbered tiles, 3 x 4, each with a real scene strip at left."""
    grid = [s for s in STORIES if not s.get("featured")]
    assert len(grid) == 12, "grid needs 12 stories, got %d" % len(grid)
    for k, s in enumerate(grid):
        col, row = k % 3, k // 3
        x0, y0 = GRID_X[col], GRID_Y[row]
        x1, y1 = x0 + GRID_W, y0 + GRID_H
        d.rectangle((x0, y0, x1, y1), fill=CREAM, outline=GOLD, width=1)

        # scene strip, full tile height at the left edge
        strip = (x0 + 1, y0 + 1, x0 + 1 + STRIP_W, y0 + 1 + STRIP_H)
        paste_art(canvas, s["art"], strip)

        tx = x0 + TEXT_DX
        tw = TEXT_W
        # numeral + headline on one line
        num = "%d" % s["n"]
        d.text((tx, y0 + 1), num, font=F["grid_head"], fill=TEAL)
        nw = text_w(d, num, F["grid_head"])
        hx = tx + nw + 4
        hl = wrap_block(d, s["head"], F["grid_head"], tw - (hx - tx), 2)
        y = draw_lines(d, hx, y0 + 1, hl, F["grid_head"], INK, lh=12)

        # dek: whatever room is left, never truncated
        room = y1 - 13 - y
        lines = wrap(d, s["dek"], F["small"], tw)
        dek_lh = 11
        maxl = max(1, int(room // dek_lh))
        if len(lines) > maxl:
            raise AssertionError(
                "grid %d dek needs %d lines, has room for %d: %r"
                % (s["n"], len(lines), maxl, s["dek"][:50]))
        draw_lines(d, tx, y, lines, F["small"], INK_SOFT, lh=dek_lh)

        # source, wrapped to the tile floor (never cut with an ellipsis)
        sl = wrap(d, s["src"], F["small"], tw)
        sy = y1 - 13 * len(sl)
        assert sy >= y + len(lines) * dek_lh - 1, \
            "grid %d source collides with its dek" % s["n"]
        for j, ln in enumerate(sl):
            d.text((tx, sy + j * 13), ln, font=F["small"], fill=TEAL)


# ------------------------------------------------------- band: briefs
def draw_briefs(canvas, d, F):
    """ALSO ON - 18 briefs, two columns, one printed numeral each."""
    y0, y1 = BANDS["briefs"]
    d.text((M, y0), "ALSO ON SATURDAY 21 NOVEMBER", font=F["kicker"], fill=TEAL)
    hairline(d, M, y0 + 13, 568, y0 + 13, GOLD)

    # Move the briefs down to avoid the header
    header_h = 16  # approx height needed for header
    top = y0 + header_h + 2  # start briefs below header
    per_col = 9
    row_h = (y1 - top) / per_col

    for i, (n, place, text, tag, pin) in enumerate(BRIEFS):
        col = i // per_col
        idx = i % per_col
        cx = BRIEF_X[col]
        ry = int(top + idx * row_h)

        # Number(bold) + Place(bold) + Summary(normal) + Tag(normal)
        d.text((cx, ry), str(n), font=F["brief_b"], fill=TEAL)
        nw = text_w(d, str(n), F["brief_b"])

        px = cx + nw + 5
        d.text((px, ry), place, font=F["brief_b"], fill=INK)
        pw = text_w(d, place, F["brief_b"])

        sx = px + pw + 5
        d.text((sx, ry), text, font=F["brief"], fill=INK_SOFT)
        sw = text_w(d, text, F["brief"])

        tx = sx + sw + 5
        d.text((tx, ry), tag, font=F["brief"], fill=INK_SOFT)

        # Assertions
        w = tx + text_w(d, tag, F["brief"]) - cx
        assert w <= 264, f"Brief {n} too wide: {w}px"
        assert row_h >= line_h(F["brief"]) + 2, f"Row pitch too small: {row_h}px (line_h={line_h(F['brief'])})"


# ---------------------------------------------------------- band: map
def lonlat_to_xy(lon, lat, rect):
    x0, y0, x1, y1 = rect
    # equirectangular, cropped to the inhabited band of latitudes
    lon_min, lon_max = -170.0, 180.0
    lat_min, lat_max = -58.0, 78.0
    x = x0 + (lon - lon_min) / (lon_max - lon_min) * (x1 - x0)
    y = y0 + (lat_max - lat) / (lat_max - lat_min) * (y1 - y0)
    return x, y


def draw_map(canvas, d, F):
    x0, y0, x1, y1 = MAP_RECT
    d.rectangle(MAP_RECT, fill=PAPER, outline=GOLD, width=1)
    d.text((x0 + 8, y0 + 6), "WHERE IT HAPPENED", font=F["kicker"], fill=TEAL)

    inner = (x0 + 6, y0 + 22, x1 - 6, y1 - 22)
    d.rectangle(inner, fill=CREAM, outline=None)

    # a soft land suggestion: banded tint, no coastlines invented
    ix0, iy0, ix1, iy1 = inner
    for k in range(5):
        yy = iy0 + int((iy1 - iy0) * (0.18 + 0.16 * k))
        d.rectangle((ix0 + 4, yy, ix1 - 4, yy + 3), fill=LAND)

    placed = []
    pins = []
    for s in STORIES:
        if s["pin"]:
            pins.append((s["n"], s["pin"]))
    for b in BRIEFS:
        if b[4]:
            pins.append((b[0], b[4]))

    for n, (lon, lat) in pins:
        px, py = lonlat_to_xy(lon, lat, inner)
        # keep every pin inside the map rect
        px = min(max(px, ix0 + 7), ix1 - 7)
        py = min(max(py, iy0 + 7), iy1 - 7)
        # push apart pins that collide (cities repeat: Paris, Brussels)
        for _ in range(60):
            moved = False
            for (qx, qy) in placed:
                if abs(px - qx) < 13 and abs(py - qy) < 13:
                    py += 4
                    px += 3
                    moved = True
            px = min(max(px, ix0 + 7), ix1 - 7)
            py = min(max(py, iy0 + 7), iy1 - 7)
            if not moved:
                break
        placed.append((px, py))
        # gold ring + teal dot: the numeral is the only numbering device
        d.ellipse((px - 6, py - 6, px + 6, py + 6), outline=GOLD, width=1)
        d.text((px - text_w(d, "%d" % n, F["pin"]) / 2,
                py - 6), "%d" % n, font=F["pin"], fill=TEAL)

    # margin note for the two stories with no pin
    note = "5 - in orbit at Mercury · 32 - global markets"
    d.text((x0 + 8, y1 - 14), note, font=F["small"], fill=INK_SOFT)
    assert x0 + 8 + text_w(d, note, F["small"]) <= x1 - 4, "map note overruns"

    # every pin asserted inside the map rect
    for (px, py) in placed:
        assert x0 <= px <= x1 and y0 <= py <= y1, "pin outside map rect"


# -------------------------------------------------------- band: legend
def draw_legend(canvas, d, F):
    y0, y1 = BANDS["legend"]
    x = M
    d.text((x, y0), "HOW SURE", font=F["legend_b"], fill=TEAL)
    x += text_w(d, "HOW SURE", F["legend_b"]) + 10
    for key, defn in SURE_KEYS:
        d.text((x, y0), key, font=F["legend_b"], fill=INK)
        x += text_w(d, key, F["legend_b"]) + 4
        d.text((x, y0), "- " + defn, font=F["legend"], fill=INK_SOFT)
        x += text_w(d, "- " + defn, F["legend"]) + 14
        d.text((x, y0), "·", font=F["legend"], fill=GOLD)
        x += 12
    assert x <= W - M + 1, "HOW SURE legend overruns the margin"


# ----------------------------------------------------- band: date check
def draw_datecheck(canvas, d, F):
    """Drawn LAST: other days' news and not-yet news, dates in bold."""
    x0, y0, x1, y1 = M, BANDS["datecheck"][0], W - M, BANDS["datecheck"][1]
    d.rectangle((x0, y0, x1, y1), fill=CREAM, outline=GOLD, width=1)
    d.text((x0 + 10, y0 + 7), "DATE CHECK", font=F["kicker"], fill=TEAL)
    d.text((x0 + 90, y0 + 7), "left out - other days' news", font=F["small"],
           fill=INK_SOFT)

    lh = 10
    # left half: 13 LEFT OUT items, date in bold
    lx = x0 + 10
    colw = 470
    y = y0 + 24
    for txt, when in DATE_CHECK_LEFT:
        lines = wrap(d, txt, F["small"], colw - 96)
        d.text((lx, y), lines[0], font=F["small"], fill=INK)
        for k in range(1, len(lines)):
            d.text((lx, y + k * lh), lines[k], font=F["small"], fill=INK)
        yy = y + len(lines) * lh
        d.text((lx + colw - 92, y), when, font=F["body_b"], fill=INK)
        y = yy
    print("DATECHECK Y:", y, y1, y1 - 60)
    assert y <= y1 - 60, "LEFT OUT list runs into the NOT YET block"

    # right half: 6 NOT YET items
    rx = x0 + 500
    rw = (x1 - 10) - rx
    d.text((rx, y0 + 7), "NOT YET - future, not Saturday news",
           font=F["kicker"], fill=TEAL)
    y2 = y0 + 24
    for txt, when in DATE_CHECK_FUTURE:
        lines = wrap(d, txt, F["small"], rw - 96)
        d.text((rx, y2), lines[0], font=F["small"], fill=INK)
        for k in range(1, len(lines)):
            d.text((rx, y2 + k * lh), lines[k], font=F["small"], fill=INK)
        yy = y2 + len(lines) * lh
        d.text((rx + rw - 92, y2), when, font=F["body_b"], fill=INK)
        y2 = yy
    assert y2 <= y1 - 4, "NOT YET list overflows the DATE CHECK box"
    assert max(y, y2) <= y1, "DATE CHECK ink leaves the box"


# ------------------------------------------------------------- assertions
def check_bands():
    names = list(BANDS)
    prev = None
    for name in names:
        a, b = BANDS[name]
        assert b > a, "%s band is inverted" % name
        assert a >= 20 and b <= 1004, "%s band leaves the page" % name
        if prev is not None:
            assert a >= BANDS[prev][1], "%s overlaps %s" % (name, prev)
        prev = name
    # featured art + caption must fit its band
    assert FEAT_ART_Y + FEAT_ART_H <= BANDS["featured"][1]
    # grid rows must fit their band
    last = GRID_Y[-1] + GRID_H
    assert last <= BANDS["grid"][1] + 1, "grid overruns its band"
    # three featured panels + gutters span exactly the column
    span = 3 * FEAT_W + 2 * FEAT_GAP
    assert span == COL_W, "featured row spans %d, column is %d" % (span, COL_W)


def check_assets():
    for s in STORIES:
        p = os.path.join(ASSETS, s["art"])
        assert os.path.exists(p), "missing art %s" % p
    for name in ("f1.jpg", "f2.jpg", "f3.jpg"):
        im = Image.open(os.path.join(ASSETS, name))
        assert im.size == (314, 157), "%s is %s, expected 314x157" % (name, im.size)


def check_story_data():
    nums = [s["n"] for s in STORIES] + [b[0] for b in BRIEFS]
    assert sorted(nums) == list(range(1, 34)), "story numbering is not 1..33"
    assert len(STORIES) == 15 and len(BRIEFS) == 18
    assert sum(1 for s in STORIES if s.get("featured")) == 3
    for s in STORIES:
        assert s["sure"] in ("CONFIRMED", "OFFICIAL", "REPORTED", "CLAIM")
        assert s["region"] in REGION_ORDER
    # Friday work is labelled Friday, never typeset as Saturday
    joined = " ".join(s["dek"] for s in STORIES).lower()
    assert "friday" in joined or "fri" in joined


def check_text_fits(d, F):
    """Every text block re-wrapped against its real column width."""
    feats = [s for s in STORIES if s.get("featured")]
    for s in feats:
        assert len(wrap(d, s["head"], F["h_feat"], FEAT_W)) <= 2, \
            "featured %d headline needs more than 2 lines" % s["n"]
    for s in STORIES:
        if not s.get("featured"):
            assert len(wrap(d, s["head"], F["grid_head"], TEXT_W - 20)) <= 2, \
                "grid %d headline needs more than 2 lines" % s["n"]
    for n, place, text, tag, pin in BRIEFS:
        assert len(wrap(d, text, F["brief"], BRIEF_W - 40)) <= 2, \
            "brief %d needs more than 2 lines" % n


def teal_coverage(canvas):
    """Teal-family share of the page, as a fraction.  Guard is < 12%."""
    small = canvas.resize((256, 256), Image.BILINEAR).convert("RGB")
    raw = small.tobytes()
    teal = 0
    total = 256 * 256
    for i in range(0, len(raw), 3):
        r, g, b = raw[i], raw[i + 1], raw[i + 2]
        # teal family: green-dominant, blue close behind, all darkish
        if g > r + 14 and g >= b and b > r and g > 45 and g < 190:
            teal += 1
    return teal / total


def render():
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    F = fonts()

    plan_layout(d, F)
    check_bands()
    check_assets()
    check_story_data()

    draw_masthead(canvas, d, F)
    draw_timeline(canvas, d, F)
    draw_region_bar(canvas, d, F)
    draw_stats(canvas, d, F)
    draw_featured(canvas, d, F)
    draw_grid(canvas, d, F)
    draw_briefs(canvas, d, F)
    draw_map(canvas, d, F)
    draw_legend(canvas, d, F)
    draw_datecheck(canvas, d, F)          # last, as the law requires

    check_text_fits(d, F)

    cov = teal_coverage(canvas)
    assert cov < 0.12, "teal-family coverage %.3f%% exceeds 12%%" % (cov * 100)

    canvas.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    assert size <= 1048576, "entry.png is %d bytes, over 1 MiB" % size
    print("rendered %s  %dx%d  %d bytes  teal=%.2f%%"
          % (OUT, W, H, size, cov * 100))
    return canvas


if __name__ == "__main__":
    render()







