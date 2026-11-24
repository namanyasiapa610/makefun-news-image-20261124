#!/usr/bin/env python3
"""THE MORNING LEDGER — NI24 compose engine, Akun 14.
Renders Tuesday 24 November 2026 as a one-page newspaper at 3900x3900,
then downscales to the 1024x1024 entry. All artwork is drawn in code with
flat layered scenes; no photographs. Written fresh in this session.
Usage: python3 compose.py --variant A --out /tmp/ni24-akun14-A.png
"""
import argparse
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

IVORY = (247, 241, 227)
PAPER = (255, 253, 247)
INK = (35, 33, 29)
GOLD = (176, 138, 46)
GOLD_D = (140, 109, 31)
GOLD_L = (214, 182, 106)
RED = (158, 43, 37)
NAVY = (31, 58, 95)
GREEN = (46, 107, 52)
TEAL = (47, 107, 107)
OCHRE = (176, 122, 31)
BROWN = (122, 74, 33)
GREY = (90, 88, 82)
LINE = (198, 182, 148)
SKY = (214, 228, 238)
SEA = (38, 84, 124)
SEA_D = (24, 58, 92)
ORANGE = (214, 110, 44)
PINK = (198, 92, 110)
PURPLE = (94, 68, 120)
SAND = (226, 205, 160)

REGION_COLOR = {
    "EUROPE": NAVY, "MIDDLE EAST": RED, "AMERICAS": GREEN,
    "ASIA-PACIFIC": OCHRE, "AFRICA": BROWN, "OCEANIA": TEAL,
    "GLOBAL": GREY, "WORLD": GREY,
}

# ---------------------------------------------------------------- data
# Cards: (pool_no, region, place, headline, deck, source, chip, scene, lat, lon)
CARDS = [
    (2, "EUROPE", "GULF OF FINLAND",
     "Russian cargo ship Sparta II hit, towed clear",
     "Hit by two drones; Finland led rescue, all 16 crew safe. Towed out Sunday.",
     
     "Reuters / Times / WSJ", "16 CREW SAFE", "sea", 60.4, 26.5),
    (3, "EUROPE", "KYIV REGION, UKRAINE",
     "Russian strikes kill at least 15 near Kyiv",
     "11 killed in a Dymer block of flats; drone hit Kyiv, 5 injured.",
     
     "Times / AP", "15 KILLED", "city", 50.45, 30.52),
    (10, "AMERICAS", "LOS ANGELES",
     "GTA VI takes $3.8bn on day one",
     "Biggest entertainment launch ever \u2014 past all games, all films.",
     "ActiveInvestorMag", "$3.8BN DAY ONE", "sunset", 34.05, -118.25),
    (1, "EUROPE", "BENGHAZI, LIBYA",
     "Ukraine sinks Russian warship Merkury",
     "Seven sea drones; Merkury sunk at Benghazi, Ka-27 lost.",
     "CNN / Times / WSJ / AP", "7 SEA DRONES", "shipfire", 32.12, 20.07),
    (4, "WORLD", "ANTALYA, T\u00dcRKIYE",
     "COP31 ends with no deal \u2014 first since 2000",
     "Antalya Pact not adopted; text dropped all fossil fuels.",
     "Times / Guardian", "NO DEAL", "summit", 36.9, 30.7),
    (5, "MIDDLE EAST", "WASHINGTON",
     "US sanctions ~30 Iran-linked exchange houses",
     "Treasury sanctions ~30 Iran exchange houses, executives.",
     "AP / Treasury", "~30 SANCTIONED", "bank", 38.9, -77.04),
    (6, "MIDDLE EAST", "GAZA CITY",
     "Israeli strikes kill 3 in Gaza",
     "Three killed Monday, incl. a UNRWA employee; Shifa confirms.",
     "AP", "3 KILLED", "gaza", 31.5, 34.47),
    (7, "MIDDLE EAST", "WESTERN YEMEN",
     "Strike kills 11 in western Yemen",
     "Houthis: Saudi-backed strike Monday killed 11, wounded 19.",
     "AP", "11 KILLED", "desert", 15.3, 44.2),
    (8, "AMERICAS", "NEW YORK",
     "Gold rebounds 1.5% to $3,588",
     "$3,588/oz after worst week in 8 months; PCE due 25 Nov.",
     "Reuters", "$3,588/OZ", "gold", 40.71, -74.0),
    (9, "GLOBAL", "HONG KONG",
     "Bitcoin steadies near $61,284",
     "$61,284 at 12:52 UTC Mon, +1.1%; Kraken crash to ~$17,000.",
     "CoinPaprika", "$61,284", "bitcoin", 22.32, 114.17),
    (11, "OCEANIA", "WELLINGTON",
     "New Zealand bat out draw with India",
     "NZ 239/5 draw in Wellington: Mitchell 49*, Phillips 26*.",
     "HS / WicketPulse", "DRAW 239/5", "cricket", -41.29, 174.78),
    (12, "EUROPE", "LIVERPOOL",
     "Liverpool 4\u20130 Man Utd; Pochettino debut ruined",
     "Yoro off in 8th minute; United 19th in league on 8 points.",
     "Mint / NextSportsWeb", "4\u20130", "football", 53.41, -2.99),
    (13, "AMERICAS", "WASHINGTON",
     "Trump: work with Democrats to cap card rates",
     "Trump: cap card rates with Democrats; Schumer challenged.",
     "ActiveInvestorMag", "RATE CAP", "capitol", 38.9, -77.04),
    (14, "AMERICAS", "WASHINGTON",
     "Democrats take both chambers",
     "Largest House majority since 1992: 258\u2013173.",
     "BBC / ActiveInvestorMag", "258\u2013173", "tally", 38.9, -77.04),
    (20, "AMERICAS", "SANTA CLARA",
     "Nvidia brings back Jensen Huang as CEO",
     "Board reinstates Huang; shares +31%, Nasdaq +6%, S&P +5%.",
     "Reuters", "+31% HUANG BACK", "chip", 37.35, -121.95),
]

# Briefs 16-40: single dense lines (number, text, source).
BRIEFS = [
    "FBI probes hack of its crime database; states pause checks \u2014 AP",
    "North Korea weighs shutting Swiss office \u2014 KCNA / Reuters",
    "US discussing military training for Syrian forces \u2014 Reuters",
    "Congo halts cobalt exports from 30 Nov until further notice \u2014 Reuters",
    "Indonesia: 24 killed in factory blaze, dozens missing \u2014 Reuters",
    "CrowdStrike snaps up Zscaler in a $44bn deal \u2014 Reuters",
    "Trump hosts gala for meme-coin investors as token plunges \u2014 Reuters",
    "US Army to detonate lead stockpile in Iowa, 68 barrels \u2014 Reuters",
    "India considers rice export duties as prices rise \u2014 Reuters",
    "Euro zone PMI 51.7, fifth straight month of expansion \u2014 Reuters",
    "Nepal PM Balendra Shah ends Delhi visit; met Modi Mon \u2014 IANS",
    "Thousands march in Lisbon over cost of living \u2014 JagranJosh",
    "UK\u2013EU Brexit reset deal: Burnham calls it \u201clandmark\u201d \u2014 BBC",
    "India\u2013EU free-trade pact likely signed 16 Dec \u2014 JagranJosh",
    "Tata Steel sells pipe unit to APL Apollo, \u20b928,000 cr \u2014 ObserverVoice",
    "SpiceJet pilot seeks audit; IndiGo holds 65.9% \u2014 ObserverVoice",
    "Solana launches solana.ai for autonomous AI agents \u2014 Gadgets360",
    "Modi opens AI Centre at IIT Patna + \u20b9400 cr projects \u2014 ObserverVoice",
    "Amit Shah launches \u20b94,000 cr infra push in Arunachal \u2014 ObserverVoice",
    "UN states agree to keep negotiating lethal AI weapons \u2014 salonvision",
    "Miley Cyrus marries Maxx Morando in California \u2014 BBC / Reuters",
    "Google invests $5m in AI research at IIT Kharagpur \u2014 JagranJosh",
    "US stocks fall again as AI shares swing; Nasdaq fut. +3% \u2014 AP",
    "KOSPI falls ~3% Mon to 10-month low; Taiwan steadies \u2014 Reuters",
    "Mets + A.J. Ewing agree $95m, 8-year deal \u2014 AP",
]

NUMBERS_A = [
    ("7", "SEA DRONES LAUNCHED"), ("15", "KILLED NEAR KYIV"),
    ("NO DEAL", "COP31 \u00b7 FIRST SINCE 2000"), ("~30", "IRAN HOUSES SANCTIONED"),
    ("$3,588", "GOLD / OZ \u00b7 +1.5%"), ("$61,284", "BITCOIN \u00b7 12:52 UTC"),
    ("$3.8BN", "GTA VI DAY ONE"), ("+31%", "NVIDIA \u00b7 HUANG BACK"),
]
NUMBERS_B = [
    ("7", "SEA DRONES LAUNCHED"), ("15", "KILLED NEAR KYIV"),
    ("NO DEAL", "COP31 \u00b7 FIRST SINCE 2000"), ("44 HRS", "COP OVERTIME \u00b7 LONGEST EVER"),
    ("~30", "IRAN HOUSES SANCTIONED"), ("$3,588", "GOLD / OZ \u00b7 +1.5%"),
    ("$3.8BN", "GTA VI DAY ONE"), ("+31%", "NVIDIA \u00b7 HUANG BACK"),
]

# Timeline: Tuesday 24 Nov verified times (zones written explicitly).
TIMELINE = [
    ("00:23 GMT TUE", "Gold $3,645 as buyers return", "Reuters"),
    ("04:24 WIB TUE", "KCNA: Pyongyang weighs closing Swiss office", "Reuters"),
    ("TUE MORNING WIB", "Asia rallies: KOSPI +7.5%, Nikkei +4.5%", "Reuters"),
    ("TUE MORNING WIB", "Dollar nears 20-month high on AI rally", "Reuters"),
    ("TUE \u00b7 REUTERS", "Probes facing Nvidia and Huang detailed", "Reuters"),
]

DATECHECK = [
    ("186-drone night over Ukraine, 161 downed", "Fri 21\u2013Sun 22 Nov"),
    ("Hong Kong Election Committee results", "Sun 22 Nov"),
    ("Alcaraz beats Zverev, first ATP Finals title", "Sun 22 Nov"),
    ("Verstappen wins Las Vegas Grand Prix", "Sun 22 Nov"),
    ("Wembanyama scores 50, Spurs 114\u201391 Pelicans", "Sun 22 Nov"),
    ("India declare 720/9 in Wellington", "Sun 22 Nov"),
    ("Nvidia CEO Jensen Huang resigns", "Thu 12 Nov"),
]

REGION_STRIP = [("EUROPE", 5, NAVY), ("MIDDLE EAST", 3, RED),
                ("AMERICAS", 5, GREEN), ("GLOBAL", 1, GREY), ("OCEANIA", 1, TEAL)]

# Simplified world polygons (lon, lat), drawn from geography.
NA = [(-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 58),
      (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24),
      (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
      (-80, 9), (-77, 8), (-80, 25), (-81, 26), (-80, 32), (-76, 35),
      (-74, 40), (-70, 42), (-68, 45), (-65, 44), (-60, 47), (-55, 52),
      (-60, 55), (-65, 58), (-68, 58), (-75, 62), (-78, 62), (-85, 66),
      (-90, 69), (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71),
      (-165, 68), (-168, 66)]
SA = [(-77, 8), (-75, 10), (-72, 12), (-64, 11), (-60, 8), (-55, 6),
      (-52, 5), (-50, 0), (-44, -3), (-40, -5), (-35, -8), (-38, -15),
      (-40, -22), (-48, -28), (-52, -33), (-58, -38), (-62, -41), (-65, -45),
      (-68, -50), (-69, -52), (-71, -54), (-73, -50), (-73, -44), (-72, -37),
      (-71, -30), (-70, -23), (-75, -15), (-78, -8), (-81, -4), (-80, 1),
      (-77, 4), (-77, 8)]
AF = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
      (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (12, 2), (13, -1),
      (12, -6), (13, -12), (12, -18), (14, -22), (16, -28), (18, -32),
      (20, -35), (26, -34), (30, -30), (33, -26), (36, -22), (36, -18),
      (40, -15), (40, -10), (42, -4), (44, 0), (46, 5), (48, 10), (51, 12),
      (48, 11), (44, 12), (42, 15), (39, 18), (38, 22), (35, 25), (33, 28),
      (32, 31), (30, 31), (25, 32), (20, 32), (15, 33), (11, 34), (10, 35),
      (-6, 35)]
EU = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50),
      (0, 51), (3, 53), (5, 53), (8, 55), (8, 57), (10, 59), (12, 58),
      (18, 56), (21, 55), (24, 58), (24, 60), (21, 60), (23, 65), (25, 70),
      (30, 70), (35, 68), (40, 68), (45, 68), (50, 69), (55, 69), (60, 69),
      (65, 70), (70, 71), (75, 72), (80, 73), (85, 74), (90, 75), (95, 76),
      (100, 77), (105, 78), (110, 76), (115, 73), (120, 73), (125, 72),
      (130, 71), (135, 71), (140, 72), (145, 72), (150, 70), (155, 69),
      (160, 69), (165, 66), (170, 66), (175, 65), (178, 65), (178, 64),
      (170, 60), (162, 60), (158, 55), (156, 51), (150, 59), (142, 55),
      (142, 50), (140, 45), (138, 40), (135, 35), (132, 33), (130, 35),
      (127, 35), (126, 38), (127, 40), (130, 42), (132, 43), (135, 44),
      (138, 46), (140, 50), (142, 55), (150, 59), (158, 55), (162, 56),
      (170, 60), (178, 62), (178, 65), (170, 66), (162, 64), (158, 60),
      (156, 52), (150, 50), (142, 46), (140, 40), (135, 35), (130, 33),
      (127, 35), (124, 38), (120, 38), (122, 32), (120, 28), (118, 25),
      (115, 23), (112, 22), (110, 20), (108, 18), (106, 16), (105, 10),
      (103, 8), (100, 8), (98, 10), (95, 15), (92, 18), (90, 22), (88, 22),
      (86, 20), (84, 19), (82, 17), (80, 14), (78, 8), (77, 8), (75, 12),
      (73, 16), (70, 20), (68, 22), (66, 25), (63, 25), (60, 25), (58, 24),
      (56, 26), (54, 27), (52, 27), (50, 29), (49, 30), (47, 30), (45, 29),
      (43, 29), (42, 28), (40, 30), (38, 31), (36, 36), (34, 36), (32, 36),
      (30, 36), (27, 37), (26, 38), (23, 36), (22, 37), (20, 40), (18, 40),
      (15, 44), (12, 45), (10, 44), (8, 44), (6, 43), (3, 43), (0, 40),
      (-2, 37), (-6, 36), (-9, 37), (-10, 36)]
AU = [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32),
      (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
      (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
      (137, -12), (135, -12), (132, -12), (130, -13), (126, -14), (122, -17),
      (118, -20), (114, -22), (113, -22)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
      (-3, 50), (-5, 50)]
JP = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
      (141, 38), (141, 41), (142, 44), (144, 44), (141, 42), (139, 39),
      (137, 37), (134, 36), (132, 34), (130, 32), (130, 31)]
NZ = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38), (178, -37),
      (175, -40), (172, -43), (168, -46), (167, -45)]
WORLD = [NA, SA, AF, EU, AU, UK, JP, NZ]

PIN_DX = {5: (-14, -12), 13: (16, 10), 14: (12, -18)}  # spread the 3 Washington pins

# ---------------------------------------------------------------- helpers
MANIFEST = []  # (text, px_at_1024) for the freshness/margin check


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def log_text(text, px3900):
    MANIFEST.append((text, round(px3900 * 1024.0 / 3900.0, 1)))


def wrap(d, text, fnt, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, fnt, fill, width, leading=None, max_lines=None):
    if leading is None:
        leading = int(fnt.size * 1.18)
    lines = wrap(d, text, fnt, width)
    if max_lines is not None and len(lines) > max_lines:
        print(f"CLIPPED: {text[:60]!r} wraps to {len(lines)} lines, keeping {max_lines}", file=sys.stderr)
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        log_text(ln, fnt.size)
        y += leading
    return y


def centered(d, cx, y, text, fnt, fill):
    w = d.textlength(text, font=fnt)
    d.text((cx - w / 2, y), text, font=fnt, fill=fill)
    log_text(text, fnt.size)
    return y + int(fnt.size * 1.18)


def chip(d, x, y, text, fnt, fill, fg, pad=14):
    w = d.textlength(text, font=fnt) + pad * 2
    h = int(fnt.size * 1.9)
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill)
    d.text((x + pad, y + (h - fnt.size) // 2 - 2), text, font=fnt, fill=fg)
    log_text(text, fnt.size)
    return w


def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xin = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xin:
                inside = not inside
        j = i
    return inside


# ---------------------------------------------------------------- scenes
def scene(d, kind, x, y, w, h):
    """Flat layered illustration filling box (x,y,w,h)."""
    cx, cy = x + w // 2, y + h // 2
    s = min(w, h)
    if kind == "sea":
        d.rectangle([x, y, x + w, y + h], fill=SKY)
        d.rectangle([x, y + h * 0.45, x + w, y + h], fill=SEA)
        d.ellipse([x + w * 0.68, y + h * 0.08, x + w * 0.86, y + h * 0.08 + s * 0.22], fill=GOLD_L)
        for i, yy in enumerate((0.55, 0.68, 0.82, 0.94)):
            d.arc([x - 40, y + h * yy, x + w + 40, y + h * yy + 60], 0, 180, fill=(255, 255, 255), width=7)
        d.polygon([(x + w * 0.18, y + h * 0.62), (x + w * 0.82, y + h * 0.62),
                   (x + w * 0.72, y + h * 0.42), (x + w * 0.30, y + h * 0.42)], fill=INK)
        d.rectangle([x + w * 0.40, y + h * 0.30, x + w * 0.60, y + h * 0.44], fill=INK)
        d.rectangle([x + w * 0.47, y + h * 0.18, x + w * 0.53, y + h * 0.32], fill=INK)
        d.ellipse([x + w * 0.60, y + h * 0.30, x + w * 0.76, y + h * 0.30 + s * 0.20], fill=ORANGE)
        d.ellipse([x + w * 0.64, y + h * 0.34, x + w * 0.72, y + h * 0.34 + s * 0.12], fill=(255, 220, 120))
    elif kind == "city":
        d.rectangle([x, y, x + w, y + h], fill=(226, 214, 190))
        d.ellipse([x + w * 0.70, y + h * 0.06, x + w * 0.88, y + h * 0.06 + s * 0.20], fill=RED)
        for i, bx in enumerate((0.04, 0.22, 0.42, 0.62, 0.80)):
            bh = (0.55, 0.72, 0.62, 0.80, 0.58)[i]
            d.rectangle([x + w * bx, y + h * (1 - bh), x + w * (bx + 0.15), y + h], fill=(52, 48, 44))
            for wy in range(3):
                d.rectangle([x + w * (bx + 0.03), y + h * (1 - bh) + 26 + wy * 52,
                             x + w * (bx + 0.12), y + h * (1 - bh) + 46 + wy * 52], fill=GOLD_L)
        d.ellipse([x + w * 0.28, y + h * 0.10, x + w * 0.44, y + h * 0.10 + s * 0.18], fill=(120, 118, 112))
        d.ellipse([x + w * 0.36, y + h * 0.02, x + w * 0.50, y + h * 0.02 + s * 0.14], fill=(140, 138, 132))
    elif kind == "sunset":
        for i, c in enumerate((PURPLE, PINK, ORANGE, GOLD)):
            d.rectangle([x, y + h * i / 4, x + w, y + h * (i + 1) / 4], fill=c)
        d.ellipse([cx - s * 0.22, cy - s * 0.30, cx + s * 0.22, cy + s * 0.14], fill=(255, 226, 140))
        d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(58, 32, 66))
        for px in (0.14, 0.30, 0.72, 0.86):
            d.polygon([(x + w * px, y + h * 0.80), (x + w * (px + 0.05), y + h * 0.80),
                       (x + w * (px + 0.025), y + h * 0.55)], fill=(40, 22, 46))
            for a in (-0.5, -0.25, 0.0, 0.25, 0.5):
                d.line([x + w * (px + 0.025), y + h * 0.58,
                        x + w * (px + 0.025) + a * s * 0.22, y + h * 0.58 - s * 0.10],
                       fill=(40, 22, 46), width=8)
    elif kind == "shipfire":
        d.rectangle([x, y, x + w, y + h], fill=SEA_D)
        d.rectangle([x, y + h * 0.55, x + w, y + h], fill=SEA)
        d.polygon([(x + w * 0.15, y + h * 0.70), (x + w * 0.85, y + h * 0.70),
                   (x + w * 0.74, y + h * 0.48), (x + w * 0.28, y + h * 0.48)], fill=INK)
        for k in range(12):
            ang = k * math.pi / 6
            d.line([cx, cy - s * 0.05, cx + math.cos(ang) * s * 0.34,
                    cy - s * 0.05 + math.sin(ang) * s * 0.34],
                   fill=GOLD_L if k % 2 == 0 else ORANGE, width=14)
        d.ellipse([cx - s * 0.13, cy - s * 0.18, cx + s * 0.13, cy + s * 0.08], fill=RED)
        d.ellipse([cx - s * 0.06, cy - s * 0.11, cx + s * 0.06, cy + s * 0.01], fill=(255, 220, 120))
        d.ellipse([x + w * 0.72, y + h * 0.16, x + w * 0.84, y + h * 0.16 + s * 0.12], fill=(200, 210, 220))
    elif kind == "summit":
        d.rectangle([x, y, x + w, y + h], fill=(198, 222, 214))
        d.ellipse([cx - s * 0.34, cy - s * 0.10, cx + s * 0.34, cy + s * 0.58], fill=TEAL)
        d.ellipse([cx - s * 0.34, cy - s * 0.10, cx + s * 0.34, cy + s * 0.58], outline=(255, 255, 255), width=6)
        d.arc([cx - s * 0.20, cy - s * 0.02, cx + s * 0.20, cy + s * 0.38], 0, 180, fill=GOLD_L, width=10)
        d.ellipse([x + w * 0.10, y + h * 0.10, x + w * 0.24, y + h * 0.10 + s * 0.16], fill=GOLD)
        for fx in (0.08, 0.24, 0.40, 0.56, 0.72, 0.86):
            d.line([x + w * fx, y + h * 0.86, x + w * fx, y + h * 0.62], fill=INK, width=6)
            d.polygon([(x + w * fx, y + h * 0.62), (x + w * (fx + 0.10), y + h * 0.66),
                       (x + w * fx, y + h * 0.70)], fill=(RED, NAVY, GREEN, OCHRE, TEAL, GOLD)[int(fx * 10) % 6])
    elif kind == "bank":
        d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
        d.rectangle([x + w * 0.10, y + h * 0.28, x + w * 0.90, y + h * 0.36], fill=INK)
        for bx in (0.16, 0.36, 0.56, 0.76):
            d.rectangle([x + w * bx, y + h * 0.36, x + w * (bx + 0.07), y + h * 0.78], fill=INK)
        d.rectangle([x + w * 0.08, y + h * 0.78, x + w * 0.92, y + h * 0.86], fill=INK)
        for i in range(4):
            d.ellipse([x + w * (0.68 + i * 0.02), y + h * (0.60 - i * 0.09),
                       x + w * (0.80 + i * 0.02), y + h * (0.60 - i * 0.09) + s * 0.11], fill=GOLD)
        d.rectangle([x, y + h * 0.86, x + w, y + h], fill=RED)
    elif kind == "gaza":
        d.rectangle([x, y, x + w, y + h], fill=(228, 216, 188))
        for i, bx in enumerate((0.03, 0.20, 0.40, 0.60, 0.78)):
            bh = (0.60, 0.75, 0.55, 0.70, 0.50)[i]
            d.rectangle([x + w * bx, y + h * (1 - bh), x + w * (bx + 0.15), y + h], fill=(74, 66, 58))
        d.ellipse([x + w * 0.30, y + h * 0.08, x + w * 0.48, y + h * 0.08 + s * 0.18], fill=(110, 106, 100))
        d.ellipse([x + w * 0.55, y + h * 0.18, x + w * 0.70, y + h * 0.18 + s * 0.15], fill=(130, 126, 120))
        d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(96, 84, 66))
    elif kind == "desert":
        d.rectangle([x, y, x + w, y + h], fill=(240, 214, 160))
        d.ellipse([x + w * 0.70, y + h * 0.08, x + w * 0.88, y + h * 0.08 + s * 0.20], fill=GOLD)
        d.polygon([(x, y + h * 0.55), (x + w * 0.30, y + h * 0.30), (x + w * 0.60, y + h * 0.55)], fill=(178, 138, 88))
        d.polygon([(x + w * 0.45, y + h * 0.55), (x + w * 0.72, y + h * 0.34), (x + w, y + h * 0.55)], fill=(158, 118, 72))
        d.arc([x - w * 0.2, y + h * 0.62, x + w * 0.7, y + h * 1.15], 180, 360, fill=(214, 170, 110), width=10)
        d.arc([x + w * 0.3, y + h * 0.70, x + w * 1.2, y + h * 1.20], 180, 360, fill=(214, 170, 110), width=10)
        d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(196, 152, 96))
    elif kind == "gold":
        d.rectangle([x, y, x + w, y + h], fill=(42, 38, 30))
        for i in range(3):
            d.rectangle([x + w * (0.10 + i * 0.26), y + h * 0.62, x + w * (0.32 + i * 0.26), y + h * 0.80], fill=GOLD)
            d.rectangle([x + w * (0.14 + i * 0.26), y + h * 0.58, x + w * (0.28 + i * 0.26), y + h * 0.62], fill=GOLD_L)
        d.rectangle([x + w * 0.23, y + h * 0.44, x + w * 0.45, y + h * 0.58], fill=GOLD)
        d.rectangle([x + w * 0.55, y + h * 0.44, x + w * 0.77, y + h * 0.58], fill=GOLD)
        pts = [(x + w * 0.08, y + h * 0.42), (x + w * 0.30, y + h * 0.34),
               (x + w * 0.52, y + h * 0.36), (x + w * 0.74, y + h * 0.20), (x + w * 0.94, y + h * 0.12)]
        d.line(pts, fill=(120, 220, 120), width=10)
        d.polygon([(x + w * 0.86, y + h * 0.02), (x + w * 0.94, y + h * 0.12), (x + w * 0.86, y + h * 0.12)], fill=(120, 220, 120))
    elif kind == "bitcoin":
        d.rectangle([x, y, x + w, y + h], fill=(24, 32, 48))
        d.ellipse([cx - s * 0.26, cy - s * 0.30, cx + s * 0.26, cy + s * 0.22], fill=GOLD)
        bf = font("PlayfairDisplay-Black.ttf", int(s * 0.42))
        d.text((cx - d.textlength("\u20bf", font=bf) / 2, cy - s * 0.30), "\u20bf", font=bf, fill=(255, 255, 255))
        log_text("BITCOIN", int(s * 0.42))
        pts = [(x + w * 0.06, y + h * 0.82), (x + w * 0.28, y + h * 0.70),
               (x + w * 0.48, y + h * 0.74), (x + w * 0.70, y + h * 0.58), (x + w * 0.94, y + h * 0.48)]
        d.line(pts, fill=(120, 220, 120), width=9)
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(126, 164, 96))
        d.rectangle([x, y + h * 0.42, x + w, y + h * 0.58], fill=(196, 178, 130))
        for sx in (0.30, 0.36, 0.42):
            d.rectangle([x + w * sx, y + h * 0.30, x + w * (sx + 0.03), y + h * 0.44], fill=GOLD)
        d.rectangle([x + w * 0.28, y + h * 0.28, x + w * 0.47, y + h * 0.31], fill=GOLD)
        d.polygon([(x + w * 0.60, y + h * 0.30), (x + w * 0.68, y + h * 0.30),
                   (x + w * 0.60, y + h * 0.72), (x + w * 0.52, y + h * 0.72)], fill=(120, 84, 52))
        d.ellipse([x + w * 0.76, y + h * 0.62, x + w * 0.84, y + h * 0.62 + s * 0.09], fill=RED)
        d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(74, 110, 58))
    elif kind == "football":
        d.rectangle([x, y, x + w, y + h], fill=(52, 122, 66))
        d.rectangle([x + w * 0.06, y + h * 0.10, x + w * 0.94, y + h * 0.90], outline=(255, 255, 255), width=6)
        d.line([cx, y + h * 0.10, cx, y + h * 0.90], fill=(255, 255, 255), width=6)
        d.ellipse([cx - s * 0.16, cy - s * 0.16, cx + s * 0.16, cy + s * 0.16], outline=(255, 255, 255), width=6)
        d.ellipse([x + w * 0.68, y + h * 0.60, x + w * 0.82, y + h * 0.60 + s * 0.15], fill=(255, 255, 255))
        d.rectangle([x + w * 0.06, y + h * 0.06, x + w * 0.42, y + h * 0.06 + s * 0.22], fill=INK)
        sf = font("DejaVuSans-Bold.ttf", int(s * 0.16))
        d.text((x + w * 0.10, y + h * 0.06 + 4), "4\u20130", font=sf, fill=(255, 255, 255))
        log_text("4-0", int(s * 0.16))
    elif kind == "capitol":
        d.rectangle([x, y, x + w, y + h], fill=(210, 216, 228))
        d.ellipse([x + w * 0.68, y + h * 0.08, x + w * 0.86, y + h * 0.08 + s * 0.20], fill=GOLD_L)
        d.rectangle([x + w * 0.30, y + h * 0.55, x + w * 0.70, y + h * 0.88], fill=(240, 238, 230))
        d.pieslice([x + w * 0.32, y + h * 0.28, x + w * 0.68, y + h * 0.62], 180, 360, fill=(240, 238, 230))
        d.rectangle([x + w * 0.47, y + h * 0.20, x + w * 0.53, y + h * 0.32], fill=(240, 238, 230))
        for bx in (0.32, 0.42, 0.52, 0.62):
            d.rectangle([x + w * bx, y + h * 0.60, x + w * (bx + 0.05), y + h * 0.86], fill=INK)
        d.rectangle([x + w * 0.22, y + h * 0.88, x + w * 0.78, y + h * 0.94], fill=INK)
    elif kind == "tally":
        d.rectangle([x, y, x + w, y + h], fill=(236, 230, 216))
        d.rectangle([x + w * 0.08, y + h * 0.22, x + w * 0.08 + w * 0.60, y + h * 0.44], fill=NAVY)
        d.rectangle([x + w * 0.08, y + h * 0.56, x + w * 0.08 + w * 0.40, y + h * 0.78], fill=RED)
        tf = font("DejaVuSans-Bold.ttf", int(s * 0.15))
        d.text((x + w * 0.12, y + h * 0.24), "258", font=tf, fill=(255, 255, 255))
        d.text((x + w * 0.12, y + h * 0.58), "173", font=tf, fill=(255, 255, 255))
        log_text("258-173", int(s * 0.15))
        d.ellipse([x + w * 0.72, y + h * 0.14, x + w * 0.90, y + h * 0.14 + s * 0.18], fill=GOLD)
    elif kind == "chip":
        d.rectangle([x, y, x + w, y + h], fill=(26, 34, 30))
        d.rectangle([cx - s * 0.20, cy - s * 0.20, cx + s * 0.20, cy + s * 0.20], fill=(40, 90, 60))
        d.rectangle([cx - s * 0.20, cy - s * 0.20, cx + s * 0.20, cy + s * 0.20], outline=GOLD, width=6)
        for i in range(4):
            d.line([cx - s * 0.20 + i * s * 0.13, cy - s * 0.28, cx - s * 0.20 + i * s * 0.13, cy - s * 0.20], fill=GOLD, width=7)
            d.line([cx - s * 0.20 + i * s * 0.13, cy + s * 0.20, cx - s * 0.20 + i * s * 0.13, cy + s * 0.28], fill=GOLD, width=7)
        pts = [(x + w * 0.08, y + h * 0.80), (x + w * 0.30, y + h * 0.66),
               (x + w * 0.52, y + h * 0.70), (x + w * 0.74, y + h * 0.50), (x + w * 0.94, y + h * 0.38)]
        d.line(pts, fill=(120, 220, 120), width=10)
        d.polygon([(x + w * 0.86, y + h * 0.28), (x + w * 0.94, y + h * 0.38), (x + w * 0.86, y + h * 0.38)], fill=(120, 220, 120))
    else:
        d.rectangle([x, y, x + w, y + h], fill=SKY)


# ---------------------------------------------------------------- layout
W = H = 3900
M = 80
CW = W - 2 * M


def draw_map(d, x, y, w, h, pins, pin_r=34):
    d.rectangle([x, y, x + w, y + h], fill=(228, 236, 242))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=4)
    lon0, lon1, lat0, lat1 = -180.0, 180.0, 84.0, -58.0

    def to_xy(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return px, py

    step = 17
    yy = y + 8
    while yy < y + h - 6:
        xx = x + 8
        while xx < x + w - 6:
            lon = lon0 + (xx - x) / w * (lon1 - lon0)
            lat = lat0 - (yy - y) / h * (lat0 - lat1)
            if any(point_in_poly(lon, lat, p) for p in WORLD):
                d.ellipse([xx - 5, yy - 5, xx + 5, yy + 5], fill=NAVY)
            xx += step
        yy += step
    nf = font("DejaVuSans-Bold.ttf", 30)
    for num, lat, lon in pins:
        px, py = to_xy(lon, lat)
        dx, dy = PIN_DX.get(num, (0, 0))
        px, py = px + dx, py + dy
        px = max(x + pin_r + 4, min(x + w - pin_r - 4, px))
        py = max(y + pin_r + 4, min(y + h - pin_r - 4, py))
        d.ellipse([px - pin_r, py - pin_r, px + pin_r, py + pin_r], fill=RED, outline=(255, 255, 255), width=5)
        t = str(num)
        tf = font("DejaVuSans-Bold.ttf", 34)
        d.text((px - d.textlength(t, font=tf) / 2, py - 24), t, font=tf, fill=(255, 255, 255))
        log_text(t, 34)
    return to_xy


def render(variant):
    img = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(img)
    lead_order = [0, 1, 2] if variant == "A" else [2, 0, 1]
    numbers = NUMBERS_A if variant == "A" else NUMBERS_B
    map_left = variant == "A"
    y = 58

    # Kicker
    kf = font("DejaVuSans-Bold.ttf", 40)
    kicker = "40 STORIES  \u00b7  7 REGIONS  \u00b7  EVERY ONE FROM TUESDAY 24 NOVEMBER 2026"
    d.line([M, y + 28, M + 330, y + 28], fill=GOLD, width=5)
    d.line([W - M - 330, y + 28, W - M, y + 28], fill=GOLD, width=5)
    centered(d, W // 2, y, kicker, kf, INK)
    y += 78

    # Masthead
    if variant == "B":
        d.rectangle([M, y - 8, W - M, y + 330], fill=INK)
        mf = font("PlayfairDisplay-Black.ttf", 196)
        centered(d, W // 2, y, "THE MORNING LEDGER", mf, IVORY)
        y += 250
        df = font("PlayfairDisplay-Black.ttf", 118)
        centered(d, W // 2, y, "TUESDAY 24 NOVEMBER 2026", df, GOLD_L)
        y += 168
    else:
        mf = font("PlayfairDisplay-Black.ttf", 200)
        centered(d, W // 2, y, "THE MORNING LEDGER", mf, INK)
        y += 252
        d.line([M + 500, y + 8, W - M - 500, y + 8], fill=GOLD, width=6)
        df = font("PlayfairDisplay-Black.ttf", 128)
        centered(d, W // 2, y + 18, "TUESDAY 24 NOVEMBER 2026", df, GOLD_D)
        y += 186

    # Deck
    deckf = font("PlayfairDisplay-Italic.ttf", 48)
    centered(d, W // 2, y, "Seven sea drones off Libya. Fifteen dead near Kyiv. A $3.8bn opening day.", deckf, RED)
    y += 84

    # Numbers strip
    d.rectangle([M, y, W - M, y + 208], fill=PAPER, outline=LINE, width=3)
    d.line([M, y + 44, W - M, y + 44], fill=GOLD, width=3)
    labf = font("DejaVuSans-Bold.ttf", 26)
    d.text((M + 18, y + 8), "THE DAY IN NUMBERS", font=labf, fill=GOLD_D)
    log_text("THE DAY IN NUMBERS", 26)
    cell_w = CW / len(numbers)
    nbf = font("PlayfairDisplay-Black.ttf", 82)
    nlf = font("DejaVuSans-Bold.ttf", 27)
    for i, (num, lab) in enumerate(numbers):
        cx = M + cell_w * i + cell_w / 2
        if i:
            d.line([M + cell_w * i, y + 56, M + cell_w * i, y + 196], fill=LINE, width=2)
        nw = d.textlength(num, font=nbf)
        d.text((cx - nw / 2, y + 58), num, font=nbf, fill=INK)
        log_text(num, 82)
        lw = d.textlength(lab, font=nlf)
        d.text((cx - lw / 2, y + 158), lab, font=nlf, fill=GREY)
        log_text(lab, 27)
    y += 208 + 22

    # Region strip
    rf = font("DejaVuSans-Bold.ttf", 30)
    d.text((M, y), "CARDS BY REGION:", font=rf, fill=INK)
    log_text("CARDS BY REGION:", 30)
    rx = M + d.textlength("CARDS BY REGION:  ", font=rf)
    for name, cnt, col in REGION_STRIP:
        t = f"{name} {cnt}"
        wch = chip(d, rx, y - 6, t, rf, col, (255, 255, 255))
        rx += wch + 22
    y += 62

    # Leads row + right rail
    lead_h = 740
    rail_w = 640
    lead_w = (CW - rail_w - 3 * 22) // 3
    ly = y
    lead_cards = [CARDS[i] for i in lead_order]
    for i, c in enumerate(lead_cards):
        lx = M + i * (lead_w + 22)
        num, region, place, head, deck, src, chip_t, kind, lat, lon = c
        d.rectangle([lx, ly, lx + lead_w, ly + lead_h], fill=PAPER, outline=INK, width=4)
        scene(d, kind, lx + 4, ly + 4, lead_w - 8, 292)
        chip(d, lx + 22, ly + 314, chip_t, font("DejaVuSans-Bold.ttf", 32), GOLD, INK)
        cy = ly + 372
        kicker_f = font("DejaVuSans-Bold.ttf", 29)
        d.text((lx + 22, cy), f"{num}  \u00b7  {place}", font=kicker_f, fill=REGION_COLOR[region])
        log_text(f"{num} {place}", 29)
        cy += 46
        hf = font("PlayfairDisplay-Bold.ttf", 78)
        cy = text_block(d, lx + 22, cy, head, hf, INK, lead_w - 44, leading=88, max_lines=2)
        cy += 10
        dkf = font("DejaVuSans.ttf", 35)
        cy = text_block(d, lx + 22, cy, deck, dkf, (58, 55, 48), lead_w - 44, leading=42, max_lines=2)
        tf = font("DejaVuSans-Bold.ttf", 28)
        d.text((lx + 22, ly + lead_h - 46), f"REPORTED \u00b7 {src}", font=tf, fill=GREY)
        log_text(f"REPORTED {src}", 28)
    # Right rail: THE DAY IN NUMBERS vertical (7 items, tight fit)
    rx0 = W - M - rail_w
    d.rectangle([rx0, ly, rx0 + rail_w, ly + lead_h], fill=INK)
    rf2 = font("DejaVuSans-Bold.ttf", 28)
    centered(d, rx0 + rail_w // 2, ly + 16, "THE DAY IN NUMBERS", rf2, GOLD_L)
    d.line([rx0 + 40, ly + 58, rx0 + rail_w - 40, ly + 58], fill=GOLD, width=4)
    rail_nums = [("7", "SEA DRONES"), ("15", "KILLED, KYIV"),
                 ("44", "HRS COP OVERTIME"), ("~30", "IRAN HOUSES"),
                 ("$3,588", "GOLD / OZ"), ("$3.8BN", "GTA VI DAY ONE"),
                 ("+31%", "NVIDIA")]
    ry = ly + 76
    for num, lab in rail_nums:
        bf = font("PlayfairDisplay-Black.ttf", 54)
        centered(d, rx0 + rail_w // 2, ry, num, bf, (255, 255, 255))
        ry += 58
        lf = font("DejaVuSans-Bold.ttf", 24)
        centered(d, rx0 + rail_w // 2, ry, lab, lf, GOLD_L)
        ry += 36
    y = ly + lead_h + 22

    # Timeline
    d.rectangle([M, y, W - M, y + 144], fill=(232, 222, 196), outline=LINE, width=3)
    tf0 = font("DejaVuSans-Bold.ttf", 28)
    d.text((M + 18, y + 12), "TUESDAY IN TIME", font=tf0, fill=GOLD_D)
    log_text("TUESDAY IN TIME", 28)
    slot_w = (CW - 36) / len(TIMELINE)
    for i, (tm, ev, src) in enumerate(TIMELINE):
        sx = M + 18 + i * slot_w
        tf1 = font("DejaVuSans-Bold.ttf", 30)
        d.text((sx, y + 52), tm, font=tf1, fill=RED)
        log_text(tm, 30)
        ef = font("DejaVuSans.ttf", 29)
        text_block(d, sx, y + 90, ev, ef, INK, slot_w - 24, leading=34)
    y += 144 + 22

    # Mini grid 4 x 3 (cards 4..15 in pool order)
    minis = [CARDS[i] for i in range(3, 15)]
    mini_w = (CW - 3 * 20) // 4
    mini_h = 322
    for r in range(3):
        for col in range(4):
            c = minis[r * 4 + col]
            num, region, place, head, deck, src, chip_t, kind, lat, lon = c
            mx = M + col * (mini_w + 20)
            my = y + r * (mini_h + 18)
            d.rectangle([mx, my, mx + mini_w, my + mini_h], fill=PAPER, outline=INK, width=3)
            scene(d, kind, mx + 3, my + 3, 260, mini_h - 6)
            tx = mx + 280
            kf2 = font("DejaVuSans-Bold.ttf", 27)
            d.text((tx, my + 14), f"{num} \u00b7 {place}", font=kf2, fill=REGION_COLOR[region])
            log_text(f"{num} {place}", 27)
            chip(d, tx, my + 52, chip_t, font("DejaVuSans-Bold.ttf", 26), GOLD, INK)
            hf = font("PlayfairDisplay-Bold.ttf", 46)
            yy = text_block(d, tx, my + 98, head, hf, INK, mini_w - 300, leading=54, max_lines=2)
            dkf = font("DejaVuSans.ttf", 32)
            text_block(d, tx, yy + 2, deck, dkf, (58, 55, 48), mini_w - 300, leading=38, max_lines=2)
            tf = font("DejaVuSans-Bold.ttf", 25)
            d.text((tx, my + mini_h - 34), f"REPORTED \u00b7 {src}", font=tf, fill=GREY)
            log_text(f"REPORTED {src}", 25)
    y += 3 * mini_h + 2 * 18 + 22

    # Map + DATE CHECK
    map_h = 428
    pins = [(c[0], c[8], c[9]) for c in CARDS]
    if map_left:
        draw_map(d, M, y, 2280, map_h, pins)
        dc_x, dc_w = M + 2280 + 24, CW - 2280 - 24
    else:
        dc_x, dc_w = M, CW - 2280 - 24
        draw_map(d, M + dc_w + 24, y, 2280, map_h, pins)
    d.rectangle([dc_x, y, dc_x + dc_w, y + map_h], fill=(250, 238, 232), outline=RED, width=4)
    dcf = font("DejaVuSans-Bold.ttf", 34)
    d.text((dc_x + 20, y + 14), "DATE CHECK \u2014 NOT TODAY", font=dcf, fill=RED)
    log_text("DATE CHECK NOT TODAY", 34)
    yy = y + 62
    bf = font("DejaVuSans.ttf", 30)
    for txt, when in DATECHECK:
        d.text((dc_x + 20, yy), "\u2715", font=bf, fill=RED)
        log_text(txt, 30)
        yy = text_block(d, dc_x + 56, yy, f"{txt} \u2014 {when}", bf, INK, dc_w - 76, leading=36)
        yy += 2
    cf = font("PlayfairDisplay-Italic.ttf", 32)
    d.text((dc_x + 20, y + map_h - 44),
           "Tonight\u2019s real count: 7 sea drones, at the top of this page.",
           font=cf, fill=RED)
    log_text("Tonight's real count: 7 sea drones", 32)
    y += map_h + 22

    # ALSO ON
    af = font("DejaVuSans-Bold.ttf", 34)
    d.text((M, y), "ALSO ON", font=af, fill=INK)
    log_text("ALSO ON", 34)
    d.line([M + 260, y + 20, W - M, y + 20], fill=GOLD, width=4)
    y += 54
    col_w = (CW - 2 * 30) // 3
    bf2 = font("DejaVuSans.ttf", 31)
    per_col = 9
    for ci in range(3):
        cx0 = M + ci * (col_w + 30)
        for ri in range(per_col):
            idx = ci * per_col + ri
            if idx >= len(BRIEFS):
                break
            by = y + ri * 40
            num = 16 + idx
            nf2 = font("DejaVuSans-Bold.ttf", 31)
            d.text((cx0, by), f"{num}", font=nf2, fill=GOLD_D)
            log_text(str(num), 31)
            nw = d.textlength(f"{num}  ", font=nf2)
            d.text((cx0 + nw, by), BRIEFS[idx], font=bf2, fill=INK)
            log_text(BRIEFS[idx], 31)
    y += per_col * 40 + 18

    # Footer
    d.line([M, y, W - M, y], fill=GOLD, width=4)
    y += 14
    ff = font("DejaVuSans.ttf", 28)
    foot = ("Sources: Reuters \u00b7 AP \u00b7 CNN \u00b7 Times \u00b7 WSJ \u00b7 BBC \u00b7 Guardian \u00b7 Treasury \u00b7 "
            "CoinPaprika \u00b7 IANS \u00b7 JagranJosh \u00b7 ObserverVoice.  REPORTED = as reported by the source named; "
            "no speculation shown as fact.")
    y = text_block(d, M, y, foot, ff, GREY, CW, leading=36)
    y += 6
    lf2 = font("DejaVuSans-Bold.ttf", 28)
    d.text((M, y), "Pictures and map: original, drawn in code.  THE MORNING LEDGER \u00b7 Tuesday 24 November 2026.",
           font=lf2, fill=INK)
    log_text("Pictures and map: original, drawn in code.", 28)
    y += 40
    if y > H - 30:
        print(f"WARNING overflow: bottom y={y} > {H-30}", file=sys.stderr)
    print(f"layout bottom y={y} (canvas {H})")
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="A")
    ap.add_argument("--out", required=True)
    ap.add_argument("--manifest", default="")
    args = ap.parse_args()
    img = render(args.variant)
    small = img.resize((1024, 1024), Image.LANCZOS)
    small = small.convert("P", palette=Image.ADAPTIVE, colors=256)
    small.save(args.out, optimize=True)
    size = os.path.getsize(args.out)
    print(f"variant {args.variant}: {args.out} {size} bytes")
    prev = img.resize((300, 300), Image.LANCZOS)
    prev.save(args.out.replace(".png", "-300.png"))
    if args.manifest:
        with open(args.manifest, "w") as f:
            json.dump(MANIFEST, f)
        print(f"manifest: {len(MANIFEST)} text items")


if __name__ == "__main__":
    main()
