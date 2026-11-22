#!/usr/bin/env python3
"""Assemble the Rasikh font from letter forms traced with VectorCraft.

Input:  traced/<glyph>.svg (one per letter form, from trace.sh) and
        traced/meta.json   (where each form was cut out of its source line).
Output: dist/Rasikh-Regular.{ttf,otf,woff2}

Letter forms that never appear in the source images are composed from traced
parts (a bowl from one letter, a loop from another), so every shape on the page
still comes from the original lettering. Digits, harakat and Latin punctuation
come from build.py's pen-drawn set.
"""
import json, os, sys, math
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
from svgelements import SVG, Path, Shape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as pen  # noqa: E402

TRACED = os.path.join(HERE, "traced")
TH_PX = 44            # baseline stroke in the source bitmaps
STROKE = 100          # ... in font units
S = STROKE / TH_PX    # font units per bitmap pixel
J = STROKE / 2        # centre line of the joining stroke (its bottom sits on y=0)
SB = 55               # side bearing next to an unjoined edge


# ------------------------------------------------------------------ loading
def svg_polys(path):
    """Filled outlines of an SVG as shapely geometry (even-odd)."""
    shapes = []
    for el in SVG.parse(path).elements():
        if not isinstance(el, Shape):
            continue
        p = Path(el)
        if p.fill is None or p.fill.value is None or p.fill.alpha == 0:
            continue
        geom = None
        for sub in p.as_subpaths():
            sp = Path(sub)
            n = max(int(sp.length(error=1e-2) / 3), 12)
            pts = [sp.point(t / n) for t in range(n)]
            pts = [(q.x, q.y) for q in pts if q is not None]
            if len(pts) < 3:
                continue
            ring = Polygon(pts).buffer(0)
            if ring.is_empty:
                continue
            geom = ring if geom is None else geom.symmetric_difference(ring)
        if geom is not None:
            shapes.append(geom)
    return unary_union(shapes)


def bitmap_bbox(png):
    from PIL import Image
    a = np.array(Image.open(png).convert("L")) < 128
    ys, xs = np.nonzero(a)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def load(name, meta):
    m = meta[name]
    g = svg_polys(os.path.join(TRACED, name + ".svg"))
    # map the SVG's coordinates onto the cut-out bitmap's pixels (fits its ink box)
    bx0, by0, bx1, by1 = bitmap_bbox(os.path.join(TRACED, name + ".png"))
    sx0, sy0, sx1, sy1 = g.bounds
    kx, ky = (bx1 - bx0) / (sx1 - sx0), (by1 - by0) / (sy1 - sy0)
    g = affinity.affine_transform(g, [kx, 0, 0, ky, bx0 - sx0 * kx, by0 - sy0 * ky])
    # bitmap -> source line pixels
    g = affinity.translate(g, m["ox"], m["oy"])
    X0, _, X1, _ = m["bbox"]
    left = m["xl"] if m["xl"] is not None else X0 - SB / S
    right = m["xr"] if m["xr"] is not None else X1 + SB / S
    js = [v for v in (m["jl"], m["jr"]) if v is not None]
    jc = sum(js) / len(js) if js else m["bl"]
    # line pixels -> font units (y up)
    g = affinity.affine_transform(g, [S, 0, 0, -S, -left * S, jc * S + J])
    return Form(g, (right - left) * S, m["xl"] is not None, m["xr"] is not None)


class Form:
    def __init__(self, geom, adv, jl, jr):
        geom = geom.buffer(0)
        parts = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
        self.body = unary_union([p for p in parts if p.area >= 2.3 * STROKE ** 2]) if parts else Polygon()
        self.marks = [p for p in parts if p.area < 2.3 * STROKE ** 2]
        self.adv, self.jl, self.jr = adv, jl, jr

    def copy(self, marks=True):
        f = Form.__new__(Form)
        f.body, f.marks, f.adv, f.jl, f.jr = self.body, list(self.marks) if marks else [], self.adv, self.jl, self.jr
        return f

    def geom(self):
        return unary_union([self.body] + self.marks)


# ------------------------------------------------------------------ editing
def band():
    return (J - STROKE * 0.75, J + STROKE * 0.75)


def outside_band_xs(f):
    """x positions where the body rises or drops out of the joining band."""
    lo, hi = band()
    xs = []
    x0, _, x1, _ = f.body.bounds
    for x in np.arange(x0, x1, 4):
        seg = f.body.intersection(box(x, -2000, x + 4, 2000))
        if seg.is_empty:
            continue
        _, y0, _, y1 = seg.bounds
        if y1 > hi + 6 or y0 < lo - 6:
            xs.append(x)
    return xs


def strip_right(f):
    """drop the incoming connection on the right (fina -> isol, medi -> init)."""
    xs = outside_band_xs(f)
    cut = max(xs) + 6
    g = f.copy()
    g.body = f.body.intersection(box(-3000, -3000, cut, 3000)).buffer(0)
    g.adv, g.jr = cut + SB, False
    return g


def strip_left(f):
    """drop the outgoing connection on the left (init -> isol, medi -> fina)."""
    xs = outside_band_xs(f)
    cut = min(xs) - 6
    g = f.copy()
    g.body = affinity.translate(f.body.intersection(box(cut, -3000, 6000, 3000)).buffer(0), SB - cut, 0)
    g.marks = [affinity.translate(m, SB - cut, 0) for m in f.marks]
    g.adv, g.jl = f.adv - cut + SB, False
    return g


def stub(x0, x1):
    lo, hi = J - STROKE / 2, J + STROKE / 2
    return box(x0, lo, x1, hi)


def add_right(f, length=90):
    g = f.copy()
    x = max(outside_band_xs(f)) if not f.jr else f.adv
    g.body = unary_union([f.body.intersection(box(-3000, -3000, x + 4, 3000)), stub(x - 10, x + length)])
    g.adv, g.jr = x + length, True
    return g


def add_left(f, length=90):
    g = f.copy()
    x = min(outside_band_xs(f))
    body = unary_union([f.body.intersection(box(x - 4, -3000, 6000, 3000)), stub(x - length, x + 10)])
    shift = length - x
    g.body = affinity.translate(body, shift, 0)
    g.marks = [affinity.translate(m, shift, 0) for m in f.marks]
    g.adv, g.jl = f.adv + shift, True
    return g


def square_joins(f):
    """make every connection the same stroke, flush with the glyph edge."""
    parts = [f.body]
    if f.jl:
        parts.append(stub(-2, 24))
    if f.jr:
        parts.append(stub(f.adv - 24, f.adv + 2))
    g = f.copy()
    g.body = unary_union(parts)
    return g


def trim_joins(f, length=70):
    """shorten long connections (kashidas in the source) to a standard stub."""
    xs = outside_band_xs(f)
    if not xs:
        return f
    g = f.copy()
    body, marks = f.body, list(f.marks)
    if f.jr and f.adv - max(xs) > length:
        cut = max(xs) + length
        body = body.intersection(box(-3000, -3000, cut, 3000))
        g.adv = cut
    if f.jl and min(xs) > length:
        cut = min(xs) - length
        body = affinity.translate(body.intersection(box(cut, -3000, 6000, 3000)), -cut, 0)
        marks = [affinity.translate(m, -cut, 0) for m in marks]
        g.adv -= cut
    g.body, g.marks = body.buffer(0), marks
    return g


def part(f, x0, x1, y0=-3000, y1=3000):
    return f.body.intersection(box(x0, y0, x1, y1)).buffer(0)


# ------------------------------------------------------------------ dots
class Dots:
    def __init__(self, sample):
        d = sample
        c = d.centroid
        self.shape = affinity.translate(d, -c.x, -c.y)
        x0, y0, x1, y1 = self.shape.bounds
        self.w = x1 - x0

    def put(self, f, n, cx, y, below=False):
        gap = self.w * 1.12
        pos = {1: [(0, 0)], 2: [(-gap / 2, 0), (gap / 2, 0)],
               3: [(-gap / 2, 0), (gap / 2, 0), (0, (-1 if below else 1) * self.w * 1.05)]}[n]
        return [affinity.translate(self.shape, cx + dx, y + dy) for dx, dy in pos]

    def above(self, f, n, cx=None, extra=0):
        cx = f.adv / 2 if cx is None else cx
        col = f.body.intersection(box(cx - 70, -3000, cx + 70, 3000))
        top = col.bounds[3] if not col.is_empty else 2 * STROKE
        return self.put(f, n, cx, top + self.w * 0.95 + extra)

    def below(self, f, n, cx=None):
        cx = f.adv / 2 if cx is None else cx
        col = f.body.intersection(box(cx - 70, -3000, cx + 70, 3000))
        bot = min(col.bounds[1], 0) if not col.is_empty else 0
        return self.put(f, n, cx, bot - self.w * 0.95, below=True)


def tooth_x(f):
    """x of the tallest column (a tooth or stem), ignoring the joins."""
    best, bx = -1e9, f.adv / 2
    x0, _, x1, _ = f.body.bounds
    for x in np.arange(x0 + 10, x1 - 10, 4):
        seg = f.body.intersection(box(x, -3000, x + 4, 3000))
        if not seg.is_empty and seg.bounds[3] > best:
            best, bx = seg.bounds[3], x
    return bx


# ------------------------------------------------------------------ assembly
def assemble():
    meta = json.load(open(os.path.join(TRACED, "meta.json")))
    T = {n: load(n, meta) for n in meta}
    dots = Dots(T["jeem.fina"].marks[0])
    hamza = max(T["lam_alefHamzaAbove.fina"].marks, key=lambda m: m.area)
    hc = hamza.centroid
    hamza0 = affinity.translate(hamza, -hc.x, -hamza.bounds[1])   # bottom-centre at origin

    def bare(name):
        f = T[name].copy(marks=False)
        return f

    def with_hamza(f, cx, y, below=False):
        g = f.copy()
        h = hamza0 if not below else affinity.translate(hamza0, 0, -hamza0.bounds[3])
        g.marks.append(affinity.translate(h, cx, y))
        return g

    out = {}

    def put(name, f, uni=None):
        out[name] = (square_joins(trim_joins(f)), uni)

    # --- alef family
    alef = bare("alefHamzaBelow")
    alef_fina = add_right(alef, 60)
    ax = tooth_x(alef)
    atop = alef.body.bounds[3]
    put("alef", alef, 0x0627); put("alef.fina", alef_fina)
    put("alefHamzaAbove.fina", with_hamza(alef_fina, ax, atop + 45))
    put("alefHamzaAbove", with_hamza(alef, ax, atop + 45), 0x0623)
    put("alefHamzaBelow", T["alefHamzaBelow"], 0x0625)
    put("alefHamzaBelow.fina", add_right(T["alefHamzaBelow"], 70))
    madda = pen.madda_path(0, 0, 1.0)
    from shapely.geometry import LineString
    madda_g = LineString(madda).buffer(STROKE * 0.32, cap_style=2)

    def with_madda(f, cx, y):
        g = f.copy(); g.marks.append(affinity.translate(madda_g, cx, y)); return g
    put("alefMadda", with_madda(alef, ax, atop + 60), 0x0622)
    put("alefMadda.fina", with_madda(alef_fina, tooth_x(alef_fina), atop + 60))

    # --- beh group (tooth rasm for init/medi, flat body for fina/isol)
    r_init = bare("teh.init"); r_medi = bare("teh.medi"); r_fina = bare("teh.fina"); r_isol = bare("teh")
    bowl_fina = bare("yeh.fina"); bowl_isol = strip_right(bowl_fina)
    for name, uni, n, below in (("beh", 0x0628, 1, True), ("teh", 0x062A, 2, False), ("theh", 0x062B, 3, False)):
        for form, r in (("", r_isol), (".init", r_init), (".medi", r_medi), (".fina", r_fina)):
            g = r.copy()
            cx = tooth_x(g) if form in (".init", ".medi") else g.adv / 2 + (20 if form == "" else 0)
            g.marks = dots.below(g, n, cx) if below else dots.above(g, n, cx)
            put(name + form, g, uni if form == "" else None)
    for form, r in ((".init", r_init), (".medi", r_medi)):
        for name, n, below in (("noon", 1, False), ("yeh", 2, True), ("alefMaksura", 0, False), ("yehHamza", 0, False)):
            g = r.copy(); cx = tooth_x(g)
            if n:
                g.marks = dots.below(g, n, cx) if below else dots.above(g, n, cx)
            if name == "yehHamza":
                g = with_hamza(g, cx, g.body.bounds[3] + 30)
            put(name + form, g)
    sf = bare("seen.fina")
    tx = [x for x in outside_band_xs(sf) if x > sf.adv * 0.45]
    b_end = min(tx) - 10
    flat = part(sf, -3000, b_end)
    nb_fina = Form.__new__(Form); nb_fina.body = unary_union([flat, stub(b_end - 30, b_end + 70)]); nb_fina.marks = []
    nb_fina.adv, nb_fina.jl, nb_fina.jr = b_end + 70, False, True
    nb_isol = nb_fina.copy(); nb_isol.body = unary_union([flat, stub(b_end - 30, b_end + 10)]); nb_isol.adv, nb_isol.jr = b_end + 10 + SB, False
    for form, r in (("", nb_isol), (".fina", nb_fina)):
        cx = (flat.bounds[0] + flat.bounds[2]) / 2
        g = r.copy(); g.marks = dots.put(g, 1, cx, J + STROKE * 1.4); put("noon" + form, g, 0x0646 if form == "" else None)
        g = r.copy(); g.marks = dots.put(g, 2, cx, flat.bounds[1] - dots.w * 1.1); put("yeh" + form, g, 0x064A if form == "" else None)
        put("alefMaksura" + form, r.copy(), 0x0649 if form == "" else None)
        put("yehHamza" + form, with_hamza(r, cx, J + STROKE), 0x0626 if form == "" else None)

    # --- hah group
    h_init, h_medi, h_fina = bare("hah.init"), bare("hah.medi"), bare("jeem.fina")
    h_isol = strip_right(h_fina)
    for name, uni, where in (("hah", 0x062D, None), ("jeem", 0x062C, "in"), ("khah", 0x062E, "top")):
        for form, r in (("", h_isol), (".init", h_init), (".medi", h_medi), (".fina", h_fina)):
            g = r.copy()
            if where == "in":
                if form in ("", ".fina"):
                    src = T["jeem.fina"]
                    g.marks = list(src.marks) if form == ".fina" else strip_right(src).marks
                else:
                    g.marks = dots.below(g, 1, g.adv * 0.55)
            elif where == "top":
                g.marks = dots.above(g, 1, g.adv * 0.6)
            put(name + form, g, uni if form == "" else None)

    # --- dal / reh
    d_fina = bare("dal.fina"); d_isol = bare("thal")
    r_fina = bare("reh.fina"); r_isol = strip_right(r_fina)
    for form, r in (("", d_isol), (".fina", d_fina)):
        put("dal" + form, r, 0x062F if form == "" else None)
        g = r.copy(); g.marks = dots.above(g, 1, tooth_x(g) - 20); put("thal" + form, g, 0x0630 if form == "" else None)
    for form, r in (("", r_isol), (".fina", r_fina)):
        put("reh" + form, r, 0x0631 if form == "" else None)
        g = r.copy(); g.marks = dots.above(g, 1, tooth_x(g)); put("zain" + form, g, 0x0632 if form == "" else None)

    # --- seen / sheen
    s_init, s_medi, s_fina = bare("seen.init"), bare("seen.medi"), bare("seen.fina")
    s_isol = strip_right(s_fina)
    for name, uni, n in (("seen", 0x0633, 0), ("sheen", 0x0634, 3)):
        for form, r in (("", s_isol), (".init", s_init), (".medi", s_medi), (".fina", s_fina)):
            g = r.copy()
            if n:
                xs = outside_band_xs(g); mid = (min(xs) + max(xs)) / 2 if form in (".init", ".medi") else None
                if mid is None:   # teeth are the part to the right of the bowl
                    teeth = [x for x in xs if x > g.adv * 0.45]
                    mid = (min(teeth) + max(teeth)) / 2
                g.marks = dots.above(g, 3, mid)
            put(name + form, g, uni if form == "" else None)

    # --- sad / dad (bowl borrowed from seen's final form)
    sd_raw = bare("sad.init")   # the cut-out also caught the next letters: keep the loop only
    sd_init = sd_raw.copy()
    sd_init.body = affinity.translate(part(sd_raw, 585, 6000), -585, 0)
    sd_init.adv = sd_raw.adv - 585
    sd_medi = add_right(sd_init, 70)
    teeth_x = [x for x in outside_band_xs(s_fina) if x > s_fina.adv * 0.45]
    bowl_end = min(teeth_x) - 10
    bowl = part(s_fina, -3000, bowl_end)

    def sad_with_bowl(src, joinr):
        loop = src.body.intersection(box(min(outside_band_xs(src)) - 8, -3000, 6000, 3000))
        lx = loop.bounds[0]
        shift = bowl_end - lx
        g = src.copy(marks=False)
        g.body = unary_union([bowl.buffer(0), affinity.translate(loop, shift, 0), stub(bowl_end - 20, bowl_end + 30)])
        g.adv = src.adv + shift
        g.jl, g.jr = False, joinr
        return g
    sd_fina = sad_with_bowl(sd_medi, True)
    sd_isol = sad_with_bowl(sd_init, False)
    for name, uni, n in (("sad", 0x0635, 0), ("dad", 0x0636, 1)):
        for form, r in (("", sd_isol), (".init", sd_init), (".medi", sd_medi), (".fina", sd_fina)):
            g = r.copy()
            if n:
                loop_cx = (max(outside_band_xs(g)) + min(x for x in outside_band_xs(g) if x > max(outside_band_xs(g)) - 260)) / 2
                g.marks = dots.above(g, 1, loop_cx)
            put(name + form, g, uni if form == "" else None)

    # --- tah / zah (sad's loop + alef's stem)
    stem = alef.body.intersection(box(-3000, J, 6000, 3000))
    sx0, _, sx1, _ = stem.bounds

    def tah_from(src):
        xs = outside_band_xs(src)
        x_at = min(xs) + 0.33 * (max(xs) - min(xs))
        g = src.copy(marks=False)
        g.body = unary_union([src.body, affinity.translate(stem, x_at - (sx0 + sx1) / 2, 0)])
        return g
    for form, r in (("", strip_left(sd_init)), (".init", sd_init), (".medi", sd_medi), (".fina", strip_left(sd_medi))):
        g = tah_from(r)
        put("tah" + form, g, 0x0637 if form == "" else None)
        z = g.copy(); xs = outside_band_xs(r); z.marks = dots.above(r, 1, max(xs) - 70)
        put("zah" + form, z, 0x0638 if form == "" else None)

    # --- ain / ghain (bowl borrowed from jeem's final form)
    a_init, a_medi = bare("ain.init"), bare("ain.medi")
    jb = h_fina.body
    jx = max(outside_band_xs(h_fina))
    jbowl = jb.intersection(box(-3000, -3000, 6000, J - STROKE * 0.6)).buffer(0)

    def ain_bowl(head):
        hx0 = min(outside_band_xs(head))
        b = affinity.translate(jbowl, hx0 - jbowl.bounds[0] - 40, 0)
        g = head.copy(marks=False)
        body = head.body.intersection(box(hx0 - 10, -3000, 6000, 3000))
        g.body = unary_union([body, b, stub(hx0 - 30, hx0 + 40)])
        shift = max(0, SB - g.body.bounds[0])
        g.body = affinity.translate(g.body, shift, 0)
        g.adv = head.adv + shift
        g.jl = False
        return g
    a_fina = ain_bowl(a_medi)
    a_isol = ain_bowl(a_init)
    for name, uni, n in (("ain", 0x0639, 0), ("ghain", 0x063A, 1)):
        for form, r in (("", a_isol), (".init", a_init), (".medi", a_medi), (".fina", a_fina)):
            g = r.copy()
            if n:
                g.marks = dots.above(g, 1, (min(outside_band_xs(r)) + max(outside_band_xs(r))) / 2 if form in (".init", ".medi") else max(outside_band_xs(r)) - 80)
            put(name + form, g, uni if form == "" else None)

    # --- feh / qaf
    f_medi, f_fina = bare("feh.medi"), bare("feh.fina")
    f_init = strip_right(f_medi)
    f_isol = strip_right(f_fina)
    q_medi = bare("qaf.medi")
    loop_q = q_medi.body.intersection(box(-3000, J - STROKE * 0.5, 6000, 3000))

    def qaf_bowl(joinr):
        qx0, _, qx1, _ = loop_q.bounds
        b = bowl_fina if joinr else bowl_isol
        bxr = b.adv
        g = b.copy(marks=False)
        g.body = unary_union([b.body, affinity.translate(loop_q, bxr - 30 - qx1 - (0 if joinr else 0), 0)])
        if not joinr:
            g.adv = g.body.bounds[2] + SB
        return g
    q_fina, q_isol = qaf_bowl(True), qaf_bowl(False)
    for name, uni, n, forms in (
            ("feh", 0x0641, 1, (("", f_isol), (".init", f_init), (".medi", f_medi), (".fina", f_fina))),
            ("qaf", 0x0642, 2, (("", q_isol), (".init", f_init), (".medi", q_medi), (".fina", q_fina)))):
        for form, r in forms:
            g = r.copy()
            loop = g.body.intersection(box(-3000, J + STROKE * 0.6, 6000, 3000))
            lx = (loop.bounds[0] + loop.bounds[2]) / 2 if not loop.is_empty else g.adv / 2
            g.marks = dots.above(g, n, lx)
            put(name + form, g, uni if form == "" else None)

    # --- kaf
    k_init, k_medi = bare("kaf.init"), bare("kaf.medi.c")
    kstem = stem

    k_fina = T["kaf.fina"].copy()          # keep the small mark inside the final kaf
    k_fina.marks = [m for m in k_fina.marks if m.centroid.y > J + STROKE * 0.6]
    if not k_fina.marks:   # the source's inner mark merged with the stroke: add a small hamza in its place
        xs = outside_band_xs(k_fina)
        kx = max(x for x in xs if x < k_fina.adv - 80)
        k_fina.marks = [affinity.translate(affinity.scale(hamza0, 0.6, 0.6, origin=(0, 0)), kx - 170, J + STROKE * 0.9)]
    k_isol = strip_right(k_fina)
    for form, r in (("", k_isol), (".init", k_init), (".medi", k_medi), (".fina", k_fina)):
        put("kaf" + form, r, 0x0643 if form == "" else None)

    # --- lam
    l_fina = bare("lam.fina")
    l_init = alef.copy(); l_init.body = unary_union([alef.body, stub(-2, ax + 20)]); l_init.jl = True
    put("lam", strip_right(l_fina), 0x0644)
    put("lam.init", l_init); put("lam.fina", l_fina)
    put("lam.medi", add_right(l_init, 60))

    # lam-alef: lam's stem + alef, joined at the foot (from the traced final form with hamza)
    la_fina = bare("lam_alefHamzaAbove.fina")
    la_isol = strip_right(la_fina)
    lah = T["lam_alefHamzaAbove.fina"]
    for form, r in (("", la_isol), (".fina", la_fina)):
        put("lam_alef" + form, r)
        g = r.copy(); g.marks = [m for m in (lah.marks if form else strip_right(lah).marks)]
        put("lam_alefHamzaAbove" + form, g)
        ax0 = min(outside_band_xs(r)) + 40
        put("lam_alefHamzaBelow" + form, with_hamza(r, ax0 + 40, -40, below=True))
        put("lam_alefMadda" + form, with_madda(r, ax0 + 40, atop + 60))

    # --- meem
    m_init, m_medi = bare("meem.init.b"), bare("meem.medi")
    def meem_final(src):
        """the loop with a short tail dropping from its left side, as in the source's final meem."""
        g = strip_left(src)
        x0, _, x1, _ = g.body.bounds
        w = STROKE * 0.95
        tail = Polygon([(x0, J + STROKE * 0.5), (x0 + w, J + STROKE * 0.5), (x0 + w * 0.75, -250), (x0 + w * 0.2, -265)])
        g.body = unary_union([g.body, tail])
        return g
    for form, r in (("", meem_final(m_init)), (".init", m_init), (".medi", m_medi), (".fina", meem_final(m_medi))):
        put("meem" + form, r, 0x0645 if form == "" else None)

    # --- heh / teh marbuta
    he_fina = bare("tehMarbuta.fina")
    for form, r in (("", bare("heh")), (".init", bare("heh.init")), (".medi", bare("heh.medi")), (".fina", he_fina)):
        put("heh" + form, r, 0x0647 if form == "" else None)
    g = he_fina.copy(); g.marks = dots.above(g, 2, tooth_x(g)); put("tehMarbuta.fina", g)
    g = bare("heh"); g.marks = dots.above(g, 2, tooth_x(g)); put("tehMarbuta", g, 0x0629)

    # --- waw
    wf = bare("waw.fina.b"); w = strip_right(wf)
    put("waw", w, 0x0648); put("waw.fina", wf)
    put("wawHamza", with_hamza(w, tooth_x(w), w.body.bounds[3] + 25), 0x0624)
    put("wawHamza.fina", with_hamza(wf, tooth_x(wf), wf.body.bounds[3] + 25))

    # --- hamza, tatweel, arabic punctuation
    hz = Form.__new__(Form); hz.body = affinity.scale(hamza0, 1.35, 1.35, origin=(0, 0)); hz.marks = []
    hz.body = affinity.translate(hz.body, 120, 20); hz.adv, hz.jl, hz.jr = 240, False, False
    put("hamza", hz, 0x0621)
    tw = Form.__new__(Form); tw.body = stub(-2, 162); tw.marks = []; tw.adv, tw.jl, tw.jr = 160, True, True
    put("tatweel", tw, 0x0640)
    put("question.ar", T["question.ar"], 0x061F)
    return out


# ------------------------------------------------------------------ font
def build_font():
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.pens.t2CharStringPen import T2CharStringPen
    from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

    arabic = assemble()
    # non-Arabic + marks from the pen-built set, at a matching stroke
    f = pen.Font(40, 34)
    penglyphs = pen.build_glyphs(f)
    glyphs, geoms = {}, {}
    for n, (g, u, kind) in penglyphs.items():
        if n in arabic or kind == "base" and u and 0x0600 <= u <= 0x06FF and n not in (
                "comma.ar", "semicolon.ar", "zero.ar", "one.ar", "two.ar", "three.ar", "four.ar", "five.ar",
                "six.ar", "seven.ar", "eight.ar", "nine.ar"):
            continue
        if kind == "base" and u is None and n not in ("zero.ar",):
            continue   # pen-built positional forms are replaced by the traced ones
        glyphs[n] = (g.adv, u, kind); geoms[n] = f.geom(g)
    for n, (form, u) in arabic.items():
        glyphs[n] = (round(form.adv), u, "base"); geoms[n] = form.geom()

    anchors = {}
    for n, (adv, u, kind) in glyphs.items():
        gm = geoms[n]
        x0, y0, x1, y1 = gm.bounds if not gm.is_empty else (0, 0, adv, 2 * STROKE)
        if kind == "base":
            cx = round(min(max((x0 + x1) / 2, 0), max(adv, 1)))
            anchors[n] = {"top": (cx, round(max(y1, 2 * STROKE) + 55)), "bottom": (cx, round(min(y0, 0) - 55))}
        elif kind == "mark-top":
            anchors[n] = {"m": (round((x0 + x1) / 2), round(y0)), "mk": (round((x0 + x1) / 2), round(y1 + 35))}
        else:
            anchors[n] = {"m": (round((x0 + x1) / 2), round(y1))}

    order = [".notdef"] + list(glyphs)
    cmap = {u: n for n, (_, u, _) in glyphs.items() if u}
    metrics = {".notdef": (500, 50)}
    for n, (adv, _, _) in glyphs.items():
        gm = geoms[n]
        metrics[n] = (adv, round(gm.bounds[0]) if not gm.is_empty else 0)

    gl3 = {n: (None, u, k) for n, (_, u, k) in glyphs.items()}
    fea = pen.features(gl3, anchors)
    os.makedirs(pen.DIST, exist_ok=True)
    names = {"familyName": pen.FAMILY, "styleName": "Regular", "uniqueFontIdentifier": f"{pen.FAMILY}-Regular-0.2",
             "fullName": f"{pen.FAMILY} Regular", "psName": f"{pen.FAMILY}-Regular", "version": "Version 0.2",
             "licenseDescription": "This Font Software is licensed under the SIL Open Font License, Version 1.1.",
             "licenseInfoURL": "https://openfontlicense.org"}
    for flavour in ("ttf", "otf"):
        cubic = flavour == "otf"
        fb = FontBuilder(1000, isTTF=not cubic)
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap(cmap)
        if cubic:
            cs = {}
            for n in order:
                p = T2CharStringPen(metrics[n][0], None)
                pen.notdef(p) if n == ".notdef" else pen.draw(geoms[n], p, True)
                cs[n] = p.getCharString()
            fb.setupCFF(f"{pen.FAMILY}-Regular", {"FullName": f"{pen.FAMILY} Regular"}, cs, {})
        else:
            gl = {}
            for n in order:
                p = TTGlyphPen(None)
                pen.notdef(p) if n == ".notdef" else pen.draw(geoms[n], p, False)
                gl[n] = p.glyph()
            fb.setupGlyf(gl)
        fb.setupHorizontalMetrics(metrics)
        fb.setupHorizontalHeader(ascent=1000, descent=-420)
        fb.setupNameTable(names)
        fb.setupOS2(sTypoAscender=780, sTypoDescender=-320, sTypoLineGap=200, usWinAscent=1000, usWinDescent=420,
                    usWeightClass=400, fsSelection=0x40, achVendID="NONE", ulCodePageRange1=(1 << 0) | (1 << 6))
        fb.setupPost()
        addOpenTypeFeaturesFromString(fb.font, fea)
        path = os.path.join(pen.DIST, f"{pen.FAMILY}-Regular.{flavour}")
        fb.save(path)
        if not cubic:
            fb.font.flavor = "woff2"
            fb.font.save(os.path.join(pen.DIST, f"{pen.FAMILY}-Regular.woff2"))
        print("wrote", path)


if __name__ == "__main__":
    build_font()
