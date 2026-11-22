#!/usr/bin/env python3
"""Build the Rasikh Arabic headline font (Regular + Bold).

Every glyph is described as a skeleton (centre-line paths) that is stroked
with an elliptical pen, then merged into clean outlines. Changing the pen
size gives a new weight; changing a skeleton changes the letter everywhere.

Usage:  python3 build.py            -> writes dist/*.ttf, *.otf, *.woff2
"""
import os
from shapely.geometry import LineString, LinearRing, Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity
from shapely.geometry.polygon import orient
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
FAMILY = "Rasikh"
VERSION = "0.1"

WEIGHTS = {  # name: (pen half-width x, pen half-width y, usWeightClass)
    "Regular": (40, 30, 400),
    "Bold": (56, 42, 700),
}

# vertical metrics (font units, UPM 1000)
WX = 1.42     # horizontal stretch applied to Arabic letter skeletons
A = 640      # alef / ascender stems
T = 215      # tooth height (ب ت ث ...)
H = 265      # head height (ح ع)
BOT = -160   # centre line of the flat bowls (ن ى ل س ص ق)


# ---------------------------------------------------------------- path DSL
class P:
    def __init__(self, x, y):
        self.pts = [(x, y)]

    def L(self, x, y):
        self.pts.append((x, y))
        return self

    def Q(self, cx, cy, x, y, n=12):
        x0, y0 = self.pts[-1]
        for i in range(1, n + 1):
            t = i / n
            a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t * t
            self.pts.append((a * x0 + b * cx + c * x, a * y0 + b * cy + c * y))
        return self

    def C(self, c1x, c1y, c2x, c2y, x, y, n=18):
        x0, y0 = self.pts[-1]
        for i in range(1, n + 1):
            t = i / n
            a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
            self.pts.append((a * x0 + b * c1x + c * c2x + d * x,
                             a * y0 + b * c1y + c * c2y + d * y))
        return self


def ellipse(cx, cy, ex, ey, n=56):
    import math
    return [(cx + ex * math.cos(2 * math.pi * i / n), cy + ey * math.sin(2 * math.pi * i / n))
            for i in range(n)]


class Glyph:
    def __init__(self, adv):
        self.adv = adv
        self.open = []     # list of point lists
        self.closed = []   # list of closed point lists (loops)
        self.shapes = []   # finished shapely polygons (dots, marks)
        self.thin = []     # open paths stroked with the thin (mark) pen
        self.sx = 1.0      # horizontal stretch of the skeleton

    def s(self, p):
        self.open.append(p.pts if isinstance(p, P) else p)
        return self

    def loop(self, pts):
        self.closed.append(pts)
        return self


class Font:
    """Holds the pen for one weight and builds geometry."""

    def __init__(self, rx, ry):
        self.rx, self.ry = rx, ry
        self.B = ry                      # centre of the baseline stroke
        self.S = 2 * rx * 1.02           # dot size
        self.mrx, self.mry = max(rx * 0.55, 20), max(ry * 0.55, 15)

    def stroke(self, pts, closed=False, thin=False):
        rx, ry = (self.mrx, self.mry) if thin else (self.rx, self.ry)
        k = rx / ry
        sc = [(x, y * k) for x, y in pts]
        g = LinearRing(sc) if closed else LineString(sc)
        poly = g.buffer(rx, cap_style=2, join_style=1, quad_segs=10)
        return affinity.scale(poly, 1, 1 / k, origin=(0, 0))

    def dot(self, x, y, s=None):
        s = s or self.S
        r = s * 0.18
        return box(x - s / 2 + r, y - s / 2 + r, x + s / 2 - r, y + s / 2 - r).buffer(r, quad_segs=6)

    def dots(self, n, x, y, below=False):
        s, g = self.S, self.S * 0.62
        if n == 1:
            return [self.dot(x, y)]
        if n == 2:
            return [self.dot(x - g, y), self.dot(x + g, y)]
        dy = s * 1.08 * (-1 if below else 1)
        return [self.dot(x - g, y), self.dot(x + g, y), self.dot(x, y + dy)]

    def geom(self, g):
        sx = g.sx
        st = lambda pts: [(x * sx, y) for x, y in pts]
        shift = lambda pts: [(x + sum(p[0] for p in pts) / len(pts) * (sx - 1), y) for x, y in pts]
        parts = [self.stroke(st(p)) for p in g.open]
        parts += [self.stroke(st(p), closed=True) for p in g.closed]
        parts += [self.stroke(shift(p), thin=True) for p in g.thin]
        parts += [affinity.translate(s, s.centroid.x * (sx - 1), 0) for s in g.shapes]
        geom = unary_union(parts)
        # extend the joining strokes a hair past the edges so neighbours overlap (no seams)
        return geom


# ------------------------------------------------------------ marks (shapes)
def hamza_path(f, cx, y0, sc=1.0):
    """Hamza ء as a thin-pen path, bottom-left near (cx-60*sc, y0)."""
    pts = P(105, 150).C(45, 172, 8, 105, 52, 80).L(118, 52).L(12, 18).pts
    return [(cx + (x - 62) * sc, y0 + y * sc) for x, y in pts]


def madda_path(cx, y0, sc=1.0):
    pts = P(0, 20).C(25, 70, 50, 62, 68, 38).C(86, 14, 110, 6, 136, 50).pts
    return [(cx + (x - 68) * sc, y0 + y * sc) for x, y in pts]


def add_hamza(f, g, cx, y0, below=False, sc=0.62):
    g.thin.append(hamza_path(f, cx, y0 - (110 * sc if below else 0), sc))


def add_madda(f, g, cx, y0):
    g.thin.append(madda_path(cx, y0, 0.95))


# ----------------------------------------------------------- letter skeletons
def build_glyphs(f):
    """Return {glyphname: (Glyph, unicode or None, kind)} kind in base/mark."""
    B, S = f.B, f.S
    out = {}
    up = lambda h: h + S * 0.95       # dot centre above a stroke whose top is h

    stretch = [True]

    def put(name, g, uni=None, kind="base"):
        if stretch[0] and kind == "base":
            g.sx = WX
            g.adv = round(g.adv * WX)
        out[name] = (g, uni, kind)

    # --- helpers --------------------------------------------------------
    def flat_bowl(xs, depth=BOT, left=40, tip=55):
        """from (xs,B) down into a flat bowl ending with a small up-tick on the left."""
        return (P(xs, B).Q(xs - 75, B, xs - 75, depth + 85)
                .Q(xs - 75, depth, xs - 160, depth).L(left + 95, depth)
                .Q(left, depth, left, depth + 95).L(left, tip))

    def flat_body(xs, left=40):
        return P(xs, B).L(left + 70, B).Q(left, B, left, B + 105)

    def teeth(g, xs, h=T):
        for x in xs:
            g.s(P(x, B).L(x, h))

    def join_r(g, x_from):
        """incoming connection from the right edge to x_from."""
        g.s(P(g.adv + 4, B).L(x_from, B))

    # --- alef family -------------------------------------------------------
    def alef(fina):
        adv = 190 if fina else 170
        g = Glyph(adv)
        x = 85
        g.s(P(x, 0).L(x, A))
        if fina:
            join_r(g, x)
        return g, x

    for fina in (False, True):
        sfx = ".fina" if fina else ""
        g, x = alef(fina); put("alef" + sfx, g, None if fina else 0x0627)
        g, x = alef(fina); add_hamza(f, g, x + 8, A + 55); put("alefHamzaAbove" + sfx, g, None if fina else 0x0623)
        g, x = alef(fina); add_hamza(f, g, x + 8, -75, below=True); put("alefHamzaBelow" + sfx, g, None if fina else 0x0625)
        g, x = alef(fina); add_madda(f, g, x, A + 40); put("alefMadda" + sfx, g, None if fina else 0x0622)

    # --- beh family (teeth) -------------------------------------------------
    def beh_init():
        g = Glyph(130); x = 80
        g.s(P(x, T).L(x, B).L(-4, B)); return g, x

    def beh_medi():
        g = Glyph(130); x = 65
        g.s(P(g.adv + 4, B).L(-4, B)); teeth(g, [x]); return g, x

    def beh_isol():
        g = Glyph(560)
        g.s(P(g.adv - 55, 175).Q(g.adv - 55, B, g.adv - 130, B).L(110, B).Q(40, B, 40, B + 105))
        return g, g.adv / 2

    def beh_fina():
        g = Glyph(500)
        g.s(flat_body(g.adv)); return g, g.adv / 2 + 20

    # (name, unicode, dots, below)
    beh_like = [("beh", 0x0628, 1, True), ("teh", 0x062A, 2, False), ("theh", 0x062B, 3, False)]
    for name, uni, n, below in beh_like:
        for form, fn in (("", beh_isol), (".init", beh_init), (".medi", beh_medi), (".fina", beh_fina)):
            g, x = fn()
            if below:
                g.shapes += f.dots(n, x, -S * 1.15, below=True)
            else:
                top = T if form in (".init", ".medi") else B + 60
                g.shapes += f.dots(n, x, up(top) + (0 if form in (".init", ".medi") else 30))
            put(name + form, g, uni if form == "" else None)

    # noon / yeh / alef maksura share teeth for init/medi, flat bowl for isol/fina
    def noon_isol():
        g = Glyph(400)
        g.s(P(g.adv - 55, 200).L(g.adv - 55, BOT + 85).Q(g.adv - 55, BOT, g.adv - 140, BOT)
            .L(135, BOT).Q(40, BOT, 40, BOT + 95).L(40, 55))
        return g, g.adv / 2

    def noon_fina():
        g = Glyph(400)
        g.s(flat_bowl(g.adv)); return g, g.adv / 2 - 20

    for form, fn in (("", noon_isol), (".fina", noon_fina), (".init", beh_init), (".medi", beh_medi)):
        g, x = fn()
        y = up(T) if form in (".init", ".medi") else B + 95
        g.shapes += f.dots(1, x, y)
        put("noon" + form, g, 0x0646 if form == "" else None)

    def yeh_isol():
        g = Glyph(430)
        g.s(P(g.adv - 45, 160).Q(g.adv - 45, B, g.adv - 120, B).L(g.adv - 140, B)
            .Q(g.adv - 205, B, g.adv - 205, BOT + 80).Q(g.adv - 205, BOT, g.adv - 290, BOT)
            .L(130, BOT).Q(40, BOT, 40, BOT + 95).L(40, 55))
        return g, g.adv / 2 - 30

    def yeh_fina():
        g = Glyph(380)
        g.s(flat_bowl(g.adv)); return g, g.adv / 2 - 20

    for base, uni, nd in (("yeh", 0x064A, 2), ("alefMaksura", 0x0649, 0), ("yehHamza", 0x0626, 0)):
        for form, fn in (("", yeh_isol), (".fina", yeh_fina), (".init", beh_init), (".medi", beh_medi)):
            g, x = fn()
            if nd:
                y = -S * 1.15 if form in (".init", ".medi") else BOT - S * 1.25
                g.shapes += f.dots(nd, x, y)
            if base == "yehHamza":
                hy = T + 70 if form in (".init", ".medi") else B + 90
                add_hamza(f, g, x, hy)
            put(base + form, g, uni if form == "" else None)

    # --- jeem / hah / khah --------------------------------------------------
    def hah_top(p, xr):
        """gently arched top stroke running left to the head's turning point."""
        return p.Q(xr * 0.55, H + 35, 60, H + 15)

    def hah_init():
        g = Glyph(320)
        p = hah_top(P(g.adv - 25, H - 15), g.adv)
        g.s(p.C(115, H - 45, g.adv - 95, 120, g.adv - 110, B).L(-4, B))
        return g, 150

    def hah_medi():
        g = Glyph(330)
        p = P(g.adv + 4, B).C(g.adv - 35, B, g.adv - 35, H - 40, g.adv - 75, H - 5)
        g.s(hah_top(p, g.adv - 50).C(115, H - 45, g.adv - 110, 120, g.adv - 125, B).L(-4, B))
        return g, 150

    def hah_bowl(p, adv):
        return p.C(-5, H - 25, 15, -70, 115, -170).C(185, -238, 330, -250, adv - 15, -195)

    def hah_isol():
        g = Glyph(440)
        g.s(hah_bowl(hah_top(P(g.adv - 25, H - 15), g.adv), g.adv))
        return g, 235

    def hah_fina():
        g = Glyph(450)
        p = P(g.adv + 4, B).C(g.adv - 35, B, g.adv - 35, H - 40, g.adv - 75, H - 5)
        g.s(hah_bowl(hah_top(p, g.adv - 50), g.adv))
        return g, 235

    for name, uni, where in (("hah", 0x062D, None), ("jeem", 0x062C, "in"), ("khah", 0x062E, "top")):
        for form, fn in (("", hah_isol), (".init", hah_init), (".medi", hah_medi), (".fina", hah_fina)):
            g, x = fn()
            if where == "in":
                if form in ("", ".fina"):
                    g.shapes += f.dots(1, x, 40)
                else:
                    g.shapes += f.dots(1, x + 10, -S * 1.15)
            elif where == "top":
                g.shapes += f.dots(1, x, up(H + 25) + 10)
            put(name + form, g, uni if form == "" else None)

    # --- dal / thal ----------------------------------------------------------
    def dal(fina):
        g = Glyph(300 if not fina else 310)
        g.s(P(70, 330).L(215, 105).Q(245, B, 175, B).L(40, B))
        if fina:
            join_r(g, 200)
        return g

    for fina in (False, True):
        sfx = ".fina" if fina else ""
        put("dal" + sfx, dal(fina), None if fina else 0x062F)
        g = dal(fina); g.shapes += f.dots(1, 95, up(330) + 20); put("thal" + sfx, g, None if fina else 0x0630)

    # --- reh / zain ----------------------------------------------------------
    def reh(fina):
        g = Glyph(270)
        if fina:
            g.s(P(g.adv + 4, B).L(215, B).C(185, B, 150, -150, 20, -215))
        else:
            g.s(P(215, 185).C(215, 40, 150, -150, 20, -215))
        return g

    for fina in (False, True):
        sfx = ".fina" if fina else ""
        put("reh" + sfx, reh(fina), None if fina else 0x0631)
        g = reh(fina); g.shapes += f.dots(1, 210, up(185) + (0 if not fina else -40)); put("zain" + sfx, g, None if fina else 0x0632)

    # --- seen / sheen --------------------------------------------------------
    TS = 175
    def seen_init():
        g = Glyph(350); xs = [300, 195, 90]
        g.s(P(xs[0], B).L(-4, B)); teeth(g, xs, TS); return g, xs[1]

    def seen_medi():
        g = Glyph(330); xs = [270, 165, 60]
        g.s(P(g.adv + 4, B).L(-4, B)); teeth(g, xs, TS); return g, xs[1]

    def seen_isol():
        g = Glyph(630); xs = [585, 480, 375]
        g.s(P(xs[0], B).L(xs[2], B)); teeth(g, xs, TS)
        g.s(flat_bowl(xs[2] + 20)); return g, xs[1]

    def seen_fina():
        g = Glyph(610); xs = [550, 445, 340]
        g.s(P(g.adv + 4, B).L(xs[2], B)); teeth(g, xs, TS)
        g.s(flat_bowl(xs[2] + 20)); return g, xs[1]

    for name, uni, n in (("seen", 0x0633, 0), ("sheen", 0x0634, 3)):
        for form, fn in (("", seen_isol), (".init", seen_init), (".medi", seen_medi), (".fina", seen_fina)):
            g, x = fn()
            if n:
                g.shapes += f.dots(n, x, up(TS))
            put(name + form, g, uni if form == "" else None)

    # --- sad / dad (loop + tooth) -----------------------------------------
    HS = 190
    def sad_loop(xl, xr):
        return (P(xl, B).L(xr - 75, B).C(xr + 5, B, xr + 5, HS, xr - 75, HS)
                .L(xl + 70, HS).C(xl + 15, HS, xl, B + 70, xl, B).pts)

    def sad_init():
        g = Glyph(390); g.loop(sad_loop(165, 375)); g.s(P(170, B).L(-4, B)); teeth(g, [80], 140)
        return g, 270

    def sad_medi():
        g = Glyph(410); g.loop(sad_loop(165, 375)); g.s(P(g.adv + 4, B).L(-4, B)); teeth(g, [80], 140)
        return g, 270

    def sad_isol():
        g = Glyph(640); g.loop(sad_loop(370, 610)); g.s(P(375, B).L(300, B)); teeth(g, [300], 140)
        g.s(flat_bowl(300)); return g, 490

    def sad_fina():
        g = Glyph(650); g.loop(sad_loop(370, 600)); g.s(P(g.adv + 4, B).L(300, B)); teeth(g, [300], 140)
        g.s(flat_bowl(300)); return g, 485

    for name, uni, n in (("sad", 0x0635, 0), ("dad", 0x0636, 1)):
        for form, fn in (("", sad_isol), (".init", sad_init), (".medi", sad_medi), (".fina", sad_fina)):
            g, x = fn()
            if n:
                g.shapes += f.dots(1, x, up(HS) + 10)
            put(name + form, g, uni if form == "" else None)

    # --- tah / zah -----------------------------------------------------------
    def tah(form):
        joinr = form in (".medi", ".fina")
        joinl = form in (".init", ".medi")
        adv = {"": 380, ".init": 370, ".medi": 390, ".fina": 400}[form]
        g = Glyph(adv)
        xl, xr = 110, 350
        g.loop(sad_loop(xl, xr))
        g.s(P(xl + 55, B).L(xl + 55, A - 40))
        g.s(P(xl + 5, B).L(0 if joinl else 40, B))
        if joinr:
            join_r(g, xr - 40)
        return g, xr - 75

    for name, uni, n in (("tah", 0x0637, 0), ("zah", 0x0638, 1)):
        for form in ("", ".init", ".medi", ".fina"):
            g, x = tah(form)
            if n:
                g.shapes += f.dots(1, x + 10, up(HS) + 10)
            put(name + form, g, uni if form == "" else None)

    # --- ain / ghain ---------------------------------------------------------
    def ain_head():
        return P(70, 255).C(120, 305, 235, 295, 235, 200).C(235, 120, 160, B, 80, B)

    def ain_init():
        g = Glyph(270); g.s(ain_head().L(-4, B)); return g, 160

    def ain_medi():
        g = Glyph(220)
        g.loop([(g.adv, B), (g.adv - 55, 185), (55, 185), (0, B)])
        g.s(P(g.adv + 4, B).L(-4, B)); return g, g.adv / 2

    def ain_isol():
        g = Glyph(380)
        g.s(P(70, 255).C(120, 305, 255, 295, 255, 200).C(255, 125, 190, 70, 140, 40)
            .C(60, -10, 15, -60, 40, -140).C(70, -230, 230, -255, g.adv - 15, -210))
        return g, 165

    def ain_fina():
        g = Glyph(390)
        g.loop([(g.adv, B), (g.adv - 55, 180), (130, 180), (175, B)])
        g.s(P(g.adv + 4, B).L(175, B).C(70, B - 10, 15, -60, 40, -140)
            .C(70, -230, 230, -255, g.adv - 15, -210))
        return g, 260

    for name, uni, n in (("ain", 0x0639, 0), ("ghain", 0x063A, 1)):
        for form, fn in (("", ain_isol), (".init", ain_init), (".medi", ain_medi), (".fina", ain_fina)):
            g, x = fn()
            if n:
                top = {"": 300, ".init": 300, ".medi": 185, ".fina": 180}[form]
                g.shapes += f.dots(1, x, up(top) + 10)
            put(name + form, g, uni if form == "" else None)

    # --- feh / qaf -------------------------------------------------------------
    def fl(cx):
        return ellipse(cx, B + 78, 78, 70)

    def feh_init():
        g = Glyph(240); g.loop(fl(150)); g.s(P(150, B).L(-4, B)); return g, 150

    def feh_medi():
        g = Glyph(240); g.loop(fl(125)); g.s(P(g.adv + 4, B).L(-4, B)); return g, 125

    def feh_isol():
        g = Glyph(560); g.loop(fl(g.adv - 115)); g.s(flat_body(g.adv - 115)); return g, g.adv - 115

    def feh_fina():
        g = Glyph(580); g.loop(fl(g.adv - 130)); g.s(flat_body(g.adv)); return g, g.adv - 130

    def qaf_isol():
        g = Glyph(430); g.loop(fl(g.adv - 115)); g.s(flat_bowl(g.adv - 115)); return g, g.adv - 115

    def qaf_fina():
        g = Glyph(450); g.loop(fl(g.adv - 130)); g.s(P(g.adv + 4, B).L(g.adv - 130, B)); g.s(flat_bowl(g.adv - 130))
        return g, g.adv - 130

    for name, uni, n, forms in (
            ("feh", 0x0641, 1, (("", feh_isol), (".init", feh_init), (".medi", feh_medi), (".fina", feh_fina))),
            ("qaf", 0x0642, 2, (("", qaf_isol), (".init", feh_init), (".medi", feh_medi), (".fina", qaf_fina)))):
        for form, fn in forms:
            g, x = fn()
            g.shapes += f.dots(n, x, up(B + 148) + 10)
            put(name + form, g, uni if form == "" else None)

    # --- kaf -------------------------------------------------------------------
    def kaf_init():
        g = Glyph(250)
        g.s(P(55, A - 10).L(g.adv - 55, 470).L(g.adv - 55, B).L(-4, B))
        return g

    def kaf_medi():
        g = Glyph(260)
        g.s(P(g.adv + 4, B).L(-4, B)); g.s(P(45, A - 10).L(g.adv - 70, 470).L(g.adv - 70, B))
        return g

    def kaf_sign(g, x, y):
        g.thin.append(P(x + 40, y).L(x - 30, y + 40).L(x + 40, y + 80).pts)

    def kaf_isol():
        g = Glyph(470); xs = g.adv - 70
        g.s(P(xs, A - 40).L(xs, B).L(110, B).Q(40, B, 40, B + 105)); kaf_sign(g, xs - 150, 150)
        return g

    def kaf_fina():
        g = Glyph(480); xs = g.adv - 80
        g.s(P(xs, A - 40).L(xs, B).L(110, B).Q(40, B, 40, B + 105)); join_r(g, xs)
        kaf_sign(g, xs - 150, 150)
        return g

    for form, fn in (("", kaf_isol), (".init", kaf_init), (".medi", kaf_medi), (".fina", kaf_fina)):
        put("kaf" + form, fn(), 0x0643 if form == "" else None)

    # --- lam ---------------------------------------------------------------------
    def lam_init():
        g = Glyph(150); g.s(P(85, A).L(85, B).L(-4, B)); return g

    def lam_medi():
        g = Glyph(150); g.s(P(g.adv + 4, B).L(-4, B)); g.s(P(75, B).L(75, A)); return g

    def lam_isol():
        g = Glyph(430); x = g.adv - 65
        g.s(P(x, A).L(x, BOT + 85).Q(x, BOT, x - 85, BOT).L(135, BOT).Q(40, BOT, 40, BOT + 95).L(40, 55))
        return g

    def lam_fina():
        g = Glyph(440); x = g.adv - 75
        g.s(P(x, A).L(x, BOT + 85).Q(x, BOT, x - 85, BOT).L(135, BOT).Q(40, BOT, 40, BOT + 95).L(40, 55))
        join_r(g, x)
        return g

    for form, fn in (("", lam_isol), (".init", lam_init), (".medi", lam_medi), (".fina", lam_fina)):
        put("lam" + form, fn(), 0x0644 if form == "" else None)

    # lam-alef ligatures
    def lamalef(fina, extra=None):
        g = Glyph(400 if not fina else 420)
        xr = 320
        g.s(P(xr, A).L(xr, B).L(205, B).L(70, A))
        if fina:
            join_r(g, xr)
        if extra == "hamzaA":
            add_hamza(f, g, 85, A + 50)
        elif extra == "hamzaB":
            add_hamza(f, g, 200, -75, below=True)
        elif extra == "madda":
            add_madda(f, g, 85, A + 40)
        return g

    for fina in (False, True):
        sfx = ".fina" if fina else ""
        put("lam_alef" + sfx, lamalef(fina))
        put("lam_alefHamzaAbove" + sfx, lamalef(fina, "hamzaA"))
        put("lam_alefHamzaBelow" + sfx, lamalef(fina, "hamzaB"))
        put("lam_alefMadda" + sfx, lamalef(fina, "madda"))

    # --- meem ----------------------------------------------------------------------
    def meem_init():
        g = Glyph(240); g.loop(ellipse(150, B + 65, 80, 62)); g.s(P(140, B).L(-4, B)); return g

    def meem_medi():
        g = Glyph(240); g.loop(ellipse(120, B + 65, 80, 62)); g.s(P(g.adv + 4, B).L(-4, B)); return g

    def meem_isol():
        g = Glyph(270); g.loop(ellipse(175, B + 65, 82, 62))
        g.s(P(165, B).L(125, B).Q(70, B, 70, -60).L(70, -240)); return g

    def meem_fina():
        g = Glyph(290); g.loop(ellipse(170, B + 65, 82, 62))
        g.s(P(g.adv + 4, B).L(125, B).Q(70, B, 70, -60).L(70, -240)); return g

    for form, fn in (("", meem_isol), (".init", meem_init), (".medi", meem_medi), (".fina", meem_fina)):
        put("meem" + form, fn(), 0x0645 if form == "" else None)

    # --- heh / teh marbuta ---------------------------------------------------------
    def heh_isol():
        g = Glyph(300); g.loop(ellipse(150, B + 115, 105, 115)); return g, 150, B + 230

    def heh_init():
        g = Glyph(260)
        g.loop([(70, B), (220, B), (220, 260), (150, 300), (70, 240)])
        g.s(P(75, B).L(-4, B)); g.s(P(85, 60).L(200, 220)); return g, 145, 300

    def heh_medi():
        g = Glyph(220)
        g.s(P(g.adv + 4, B).L(-4, B))
        g.loop(ellipse(110, B + 95, 60, 95)); g.loop(ellipse(110, -75, 48, 70)); return g, 110, B + 190

    def heh_fina():
        g = Glyph(250)
        g.s(P(g.adv + 4, B).L(110, B)); g.loop(ellipse(110, B + 105, 75, 105)); return g, 110, B + 210

    for form, fn in (("", heh_isol), (".init", heh_init), (".medi", heh_medi), (".fina", heh_fina)):
        g, x, top = fn()
        put("heh" + form, g, 0x0647 if form == "" else None)
    for form, fn in (("", heh_isol), (".fina", heh_fina)):
        g, x, top = fn()
        g.shapes += f.dots(2, x, up(top) + 10)
        put("tehMarbuta" + form, g, 0x0629 if form == "" else None)

    # --- waw ------------------------------------------------------------------------
    def waw(fina, hamza=False):
        g = Glyph(300)
        g.loop(ellipse(195, B + 95, 70 + f.rx * 0.5, 92 + f.ry * 0.6))
        if fina:
            join_r(g, 195)
        g.s(P(200, B).L(150, B).C(115, B, 120, -60, 60, -140).C(30, -180, 0, -205, -45, -225))
        if hamza:
            add_hamza(f, g, 195, B + 200)
        return g

    for fina in (False, True):
        sfx = ".fina" if fina else ""
        put("waw" + sfx, waw(fina), None if fina else 0x0648)
        put("wawHamza" + sfx, waw(fina, True), None if fina else 0x0624)

    # --- hamza / tatweel ----------------------------------------------------------
    g = Glyph(200); g.s(hamza_path(f, 100, 20, 1.15)); put("hamza", g, 0x0621)
    g = Glyph(160); g.s(P(g.adv + 4, B).L(-4, B)); put("tatweel", g, 0x0640)

    stretch[0] = False

    # --- digits (western) ------------------------------------------------------------
    D = 560
    def dg(adv):
        return Glyph(adv)

    g = dg(440); g.loop(ellipse(220, D / 2, 150, D / 2 - 15)); put("zero", g, 0x30)
    g = dg(360); g.s(P(220, 0).L(220, D).L(115, D - 90)); put("one", g, 0x31)
    g = dg(430); g.s(P(85, 440).C(100, 590, 345, 590, 345, 420).C(345, 300, 95, 200, 85, B).L(355, B)); put("two", g, 0x32)
    g = dg(430); g.s(P(90, 500).C(170, 590, 340, 580, 335, 445).C(330, 340, 230, 320, 175, 315))
    g.s(P(175, 315).C(380, 300, 380, 15, 205, 15).C(150, 15, 110, 40, 75, 85)); put("three", g, 0x33)
    g = dg(440); g.s(P(290, 0).L(290, D).L(60, 175).L(385, 175)); put("four", g, 0x34)
    g = dg(430); g.s(P(345, D - 15).L(125, D - 15).L(100, 320).C(190, 360, 365, 350, 355, 180).C(345, 10, 140, 0, 75, 85)); put("five", g, 0x35)
    g = dg(440); g.s(P(320, D).C(160, 510, 85, 350, 90, 210)); g.loop(ellipse(225, 185, 140, 165)); put("six", g, 0x36)
    g = dg(420); g.s(P(70, D - 15).L(355, D - 15).L(165, 0)); put("seven", g, 0x37)
    g = dg(440); g.loop(ellipse(220, 425, 115, 118)); g.loop(ellipse(220, 165, 140, 150)); put("eight", g, 0x38)
    g = dg(440); g.loop(ellipse(215, 375, 140, 165)); g.s(P(350, 380).C(355, 210, 280, 50, 120, 0)); put("nine", g, 0x39)

    # --- arabic-indic digits -----------------------------------------------------------
    g = dg(330); g.shapes.append(f.dot(165, 260, S * 1.1)); put("zero.ar", g, 0x0660)
    g = dg(300); g.s(P(150, 0).L(150, 520)); put("one.ar", g, 0x0661)
    g = dg(360); g.s(P(130, 0).L(120, 520).L(300, 520)); put("two.ar", g, 0x0662)
    g = dg(400); g.s(P(120, 0).L(110, 520).L(200, 450).L(240, 520).L(330, 450).L(370, 520)); put("three.ar", g, 0x0663)
    g = dg(370); g.s(P(290, 520).C(130, 520, 110, 300, 240, 280).C(80, 280, 60, 30, 300, 30)); put("four.ar", g, 0x0664)
    g = dg(380); g.s(P(190, 0).C(40, 0, 40, 330, 190, 470).C(340, 330, 340, 0, 190, 0)); put("five.ar", g, 0x0665)
    g = dg(330); g.s(P(60, 520).L(260, 520).L(250, 0)); put("six.ar", g, 0x0666)
    g = dg(400); g.s(P(70, 520).L(200, 0).L(330, 520)); put("seven.ar", g, 0x0667)
    g = dg(400); g.s(P(70, 0).L(200, 520).L(330, 0)); put("eight.ar", g, 0x0668)
    g = dg(360); g.loop(ellipse(160, 410, 95, 100)); g.s(P(255, 410).L(250, 0)); put("nine.ar", g, 0x0669)

    # --- punctuation --------------------------------------------------------------------
    g = dg(250); put("space", g, 0x20)
    g = dg(250); put("nbspace", g, 0xA0)
    g = dg(0); put("zwnj", g, 0x200C)
    g = dg(0); put("zwj", g, 0x200D)
    g = dg(200); g.shapes.append(f.dot(100, S / 2)); put("period", g, 0x2E)
    g = dg(220); g.shapes.append(f.dot(100, S / 2)); g.s(P(115, S / 2).L(70, -110)); put("comma", g, 0x2C)
    g = dg(220); g.shapes.append(f.dot(110, S * 0.6)); g.s(P(105, S * 0.6).Q(75, 120, 130, 230)); put("comma.ar", g, 0x060C)
    g = dg(220); g.shapes.append(f.dot(110, S * 0.6)); g.s(P(105, S * 0.6).Q(75, 120, 130, 230))
    g.shapes.append(f.dot(110, 360)); put("semicolon.ar", g, 0x061B)
    g = dg(200); g.shapes += [f.dot(100, S / 2), f.dot(100, 330)]; put("colon", g, 0x3A)
    g = dg(210); g.s(P(105, 220).L(105, D)); g.shapes.append(f.dot(105, S / 2)); put("exclam", g, 0x21)
    g = dg(400); g.s(P(85, 470).C(95, 590, 320, 595, 320, 450).C(320, 330, 200, 320, 200, 190)); g.shapes.append(f.dot(200, S / 2)); put("question", g, 0x3F)
    g = dg(400); g.s(P(315, 470).C(305, 590, 80, 595, 80, 450).C(80, 330, 200, 320, 200, 190)); g.shapes.append(f.dot(200, S / 2)); put("question.ar", g, 0x061F)
    g = dg(300); g.s(P(95, D).L(95, 400)); g.s(P(205, D).L(205, 400)); put("quotedbl", g, 0x22)
    g = dg(180); g.s(P(90, D).L(90, 400)); put("quotesingle", g, 0x27)
    g = dg(380); g.s(P(170, 120).L(70, 260).L(170, 400)); g.s(P(310, 120).L(210, 260).L(310, 400)); put("guillemetleft", g, 0xAB)
    g = dg(380); g.s(P(70, 120).L(170, 260).L(70, 400)); g.s(P(210, 120).L(310, 260).L(210, 400)); put("guillemetright", g, 0xBB)
    g = dg(260); g.s(P(200, 700).C(60, 560, 60, 0, 200, -140)); put("parenleft", g, 0x28)
    g = dg(260); g.s(P(60, 700).C(200, 560, 200, 0, 60, -140)); put("parenright", g, 0x29)
    g = dg(300); g.s(P(60, 260).L(240, 260)); put("hyphen", g, 0x2D)
    g = dg(500); g.s(P(40, 260).L(460, 260)); put("endash", g, 0x2013)
    g = dg(400); g.s(P(0, -80).L(400, -80)); put("underscore", g, 0x5F)
    g = dg(320); g.s(P(60, -60).L(260, D)); put("slash", g, 0x2F)
    g = dg(480); g.s(P(180, 0).L(220, D)); g.s(P(300, 0).L(340, D)); g.s(P(70, 180).L(420, 180)); g.s(P(80, 380).L(430, 380)); put("numbersign", g, 0x23)
    g = dg(560); g.loop(ellipse(140, 440, 70, 90)); g.loop(ellipse(420, 120, 70, 90)); g.s(P(90, 0).L(470, D)); put("percent", g, 0x25)
    g = dg(380)
    import math
    for i in range(3):
        a = math.pi / 3 * i + math.pi / 2
        g.s(P(190 - 130 * math.cos(a), 420 - 130 * math.sin(a)).L(190 + 130 * math.cos(a), 420 + 130 * math.sin(a)))
    put("asterisk", g, 0x2A)

    # --- combining marks (drawn around x=0; top marks sit on y>=0, bottom marks below y<=0) --
    def mark(name, uni, paths, loops=(), pos="top"):
        g = Glyph(0)
        g.thin += [p.pts if isinstance(p, P) else p for p in paths]
        for lp in loops:
            g.shapes.append(f.stroke(lp, closed=True, thin=True))
        put(name, g, uni, "mark-" + pos)

    damma = lambda dx=0, dy=0: ([P(dx + 15, dy + 70).Q(dx - 5, dy + 10, dx - 60, dy)],
                                [ellipse(dx + 28, dy + 85, 30, 30)])
    mark("fatha", 0x064E, [P(-70, 0).L(70, 55)])
    mark("kasra", 0x0650, [P(-70, -55).L(70, 0)], pos="bottom")
    p, l = damma(); mark("damma", 0x064F, p, l)
    mark("sukun", 0x0652, [], [ellipse(0, 45, 40, 40)])
    mark("shadda", 0x0651, [P(-80, 75).L(-55, 0).L(-10, 60).L(30, 0).L(75, 75)])
    mark("fathatan", 0x064B, [P(-70, 0).L(70, 50), P(-70, 80).L(70, 130)])
    mark("kasratan", 0x064D, [P(-70, -50).L(70, 0), P(-70, -130).L(70, -80)], pos="bottom")
    p1, l1 = damma(-45); p2, l2 = damma(55); mark("dammatan", 0x064C, p1 + p2, l1 + l2)
    mark("alefSuperscript", 0x0670, [P(0, 0).L(0, 140)])
    mark("maddaAbove", 0x0653, [madda_path(0, 0, 0.9)])
    mark("hamzaAbove", 0x0654, [hamza_path(f, 0, 0, 0.6)])
    mark("hamzaBelow", 0x0655, [hamza_path(f, 0, -100, 0.6)], pos="bottom")
    return out


# --------------------------------------------------------------- features
JOIN_DUAL = ["beh", "teh", "theh", "noon", "yeh", "alefMaksura", "yehHamza", "jeem", "hah", "khah",
             "seen", "sheen", "sad", "dad", "tah", "zah", "ain", "ghain", "feh", "qaf", "kaf", "lam",
             "meem", "heh"]
JOIN_RIGHT = ["alef", "alefHamzaAbove", "alefHamzaBelow", "alefMadda", "dal", "thal", "reh", "zain",
              "waw", "wawHamza", "tehMarbuta"]


def features(glyphs, anchors):
    fea = ["languagesystem DFLT dflt;", "languagesystem arab dflt;", ""]
    for feat, forms in (("init", JOIN_DUAL), ("medi", JOIN_DUAL), ("fina", JOIN_DUAL + JOIN_RIGHT)):
        src = [g for g in forms if f"{g}.{feat}" in glyphs]
        fea.append(f"feature {feat} {{ lookupflag IgnoreMarks;")
        fea.append(f"  sub [{' '.join(src)}] by [{' '.join(g + '.' + feat for g in src)}];")
        fea.append(f"}} {feat};")
    fea.append("feature rlig { lookupflag IgnoreMarks;")
    for a in ("alef", "alefHamzaAbove", "alefHamzaBelow", "alefMadda"):
        fea.append(f"  sub lam.init {a}.fina by lam_{a};")
        fea.append(f"  sub lam.medi {a}.fina by lam_{a}.fina;")
    fea.append("} rlig;")

    marks_top = [n for n, (_, _, k) in glyphs.items() if k == "mark-top"]
    marks_bot = [n for n, (_, _, k) in glyphs.items() if k == "mark-bottom"]
    bases = [n for n, (_, _, k) in glyphs.items() if k == "base"]
    for n in marks_top:
        x, y = anchors[n]["m"]
        fea.append(f"markClass {n} <anchor {x} {y}> @TOP;")
    for n in marks_bot:
        x, y = anchors[n]["m"]
        fea.append(f"markClass {n} <anchor {x} {y}> @BOTTOM;")
    fea.append("feature mark {")
    for n in bases:
        tx, ty = anchors[n]["top"]
        bx, by = anchors[n]["bottom"]
        fea.append(f"  pos base {n} <anchor {tx} {ty}> mark @TOP <anchor {bx} {by}> mark @BOTTOM;")
    fea.append("} mark;")
    fea.append("feature mkmk {")
    for n in marks_top:
        x, y = anchors[n]["mk"]
        fea.append(f"  pos mark {n} <anchor {x} {y}> mark @TOP;")
    fea.append("} mkmk;")
    fea.append("table GDEF { GlyphClassDef [%s], , [%s], ; } GDEF;" % (
        " ".join(bases), " ".join(marks_top + marks_bot)))
    return "\n".join(fea)


# --------------------------------------------------------------- outlines
def polys(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, MultiPolygon):
        return list(geom.geoms)
    return [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]


def draw(geom, pen, cubic):
    for poly in polys(geom.simplify(0.8)):
        poly = orient(poly, sign=1.0 if cubic else -1.0)  # CFF: ccw outer; TT: cw outer
        rings = [poly.exterior] + list(poly.interiors)
        for ring in rings:
            pts = [(round(x), round(y)) for x, y in list(ring.coords)[:-1]]
            dedup = [p for i, p in enumerate(pts) if p != pts[i - 1]]
            if len(dedup) < 3:
                continue
            pen.moveTo(dedup[0])
            for p in dedup[1:]:
                pen.lineTo(p)
            pen.closePath()


def build(weight):
    rx, ry, wclass = WEIGHTS[weight]
    f = Font(rx, ry)
    glyphs = build_glyphs(f)
    order = [".notdef"] + list(glyphs)
    geoms = {n: f.geom(g) for n, (g, _, _) in glyphs.items()}

    anchors = {}
    for n, (g, _, kind) in glyphs.items():
        gm = geoms[n]
        if gm.is_empty:
            x0 = y0 = 0; x1 = g.adv; y1 = 2 * f.ry
        else:
            x0, y0, x1, y1 = gm.bounds
        if kind == "base":
            cx = round((x0 + x1) / 2) if g.adv == 0 else round(min(max((x0 + x1) / 2, 0), g.adv))
            anchors[n] = {"top": (cx, round(max(y1, 2 * f.ry) + 55)), "bottom": (cx, round(min(y0, 0) - 55))}
        elif kind == "mark-top":
            anchors[n] = {"m": (round((x0 + x1) / 2), round(y0)), "mk": (round((x0 + x1) / 2), round(y1 + 35))}
        else:
            anchors[n] = {"m": (round((x0 + x1) / 2), round(y1))}

    cmap = {u: n for n, (_, u, _) in glyphs.items() if u}
    metrics = {".notdef": (500, 50)}
    for n, (g, _, _) in glyphs.items():
        gm = geoms[n]
        lsb = round(gm.bounds[0]) if not gm.is_empty else 0
        metrics[n] = (g.adv, lsb)

    names = {"familyName": FAMILY, "styleName": weight, "uniqueFontIdentifier": f"{FAMILY}-{weight}-{VERSION}",
             "fullName": f"{FAMILY} {weight}", "psName": f"{FAMILY}-{weight}", "version": f"Version {VERSION}",
             "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
             "licenseInfoURL": "https://openfontlicense.org"}
    os.makedirs(DIST, exist_ok=True)

    for flavour in ("ttf", "otf"):
        cubic = flavour == "otf"
        fb = FontBuilder(1000, isTTF=not cubic)
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap(cmap)
        if cubic:
            charstrings = {}
            for n in order:
                pen = T2CharStringPen(metrics[n][0], None)
                if n != ".notdef":
                    draw(geoms[n], pen, True)
                else:
                    notdef(pen)
                charstrings[n] = pen.getCharString()
            fb.setupCFF(f"{FAMILY}-{weight}", {"FullName": f"{FAMILY} {weight}"}, charstrings, {})
        else:
            gl = {}
            for n in order:
                pen = TTGlyphPen(None)
                if n != ".notdef":
                    draw(geoms[n], pen, False)
                else:
                    notdef(pen)
                gl[n] = pen.glyph()
            fb.setupGlyf(gl)
        fb.setupHorizontalMetrics(metrics)
        fb.setupHorizontalHeader(ascent=1000, descent=-420)
        fb.setupNameTable(names)
        fb.setupOS2(sTypoAscender=780, sTypoDescender=-320, sTypoLineGap=200, usWinAscent=1000,
                    usWinDescent=420, usWeightClass=wclass, fsSelection=0x40 if weight == "Regular" else 0x20,
                    achVendID="NONE", ulCodePageRange1=(1 << 0) | (1 << 6))
        fb.setupPost()
        fb.font["head"].macStyle = 1 if weight == "Bold" else 0
        addOpenTypeFeaturesFromString(fb.font, features(glyphs, anchors))
        path = os.path.join(DIST, f"{FAMILY}-{weight}.{flavour}")
        fb.save(path)
        if not cubic:
            fb.font.flavor = "woff2"
            fb.font.save(os.path.join(DIST, f"{FAMILY}-{weight}.woff2"))
        print("wrote", path)


def notdef(pen):
    for ring in ([(50, 0), (50, 700), (450, 700), (450, 0)], [(100, 50), (400, 50), (400, 650), (100, 650)]):
        pen.moveTo(ring[0])
        for p in ring[1:]:
            pen.lineTo(p)
        pen.closePath()


if __name__ == "__main__":
    for w in WEIGHTS:
        build(w)
