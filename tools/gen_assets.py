#!/usr/bin/env python3
"""
Generates the isometric SVG assets for the github.com/rahatce98 profile README.

Everything is drawn from one true-isometric projection (30 degrees), so the hero
stack, the extruded bars and the little cube motifs all share the same geometry.
Re-run after editing PALETTES or CONTENT:

    python tools/gen_assets.py

Writes assets/hero-{dark,light}.svg and assets/stack-{dark,light}.svg.
No dependencies -- standard library only.
"""

import os
from string import Template

# ---------------------------------------------------------------- projection

COS30 = 0.8660254037844386
SIN30 = 0.5


def iso(lx, ly, cx, cy, h=0.0):
    """Local plane coords -> screen coords. h lifts the point off the plane."""
    return (cx + COS30 * (lx - ly), cy + SIN30 * (lx + ly) - h)


def f(p):
    return "%.2f,%.2f" % (p[0], p[1])


def poly(pts):
    return "M " + " L ".join(f(p) for p in pts) + " Z"


def drop(p, dy):
    return (p[0], p[1] + dy)


def slab(cx, cy, half, thick):
    """A flat isometric slab. Returns (top, left_face, right_face, corners)."""
    a = iso(-half, -half, cx, cy)   # far vertex
    b = iso(half, -half, cx, cy)    # right vertex
    c = iso(half, half, cx, cy)     # near vertex
    d = iso(-half, half, cx, cy)    # left vertex
    return (
        poly([a, b, c, d]),
        poly([d, c, drop(c, thick), drop(d, thick)]),
        poly([b, c, drop(c, thick), drop(b, thick)]),
        (a, b, c, d),
    )


def box(lx, ly, w, h, cx, cy):
    """An extruded box standing on the plane. Returns (top, left, right)."""
    a = iso(lx - w, ly - w, cx, cy, h)
    b = iso(lx + w, ly - w, cx, cy, h)
    c = iso(lx + w, ly + w, cx, cy, h)
    d = iso(lx - w, ly + w, cx, cy, h)
    return (
        poly([a, b, c, d]),
        poly([d, c, drop(c, h), drop(d, h)]),
        poly([b, c, drop(c, h), drop(b, h)]),
    )


def iso_grid(cx, cy, half, step):
    """Faint background lattice in the same projection as everything else."""
    out = []
    n = int(half / step)
    for i in range(-n, n + 1):
        v = i * step
        out.append("M %s L %s" % (f(iso(v, -half, cx, cy)), f(iso(v, half, cx, cy))))
        out.append("M %s L %s" % (f(iso(-half, v, cx, cy)), f(iso(half, v, cx, cy))))
    return " ".join(out)


# ------------------------------------------------------------------ palettes

PALETTES = {
    "dark": {
        "bg0": "#04070D", "bg1": "#0A1220", "bg2": "#0D1829",
        "grid": "#1B3A5C", "gridop": "0.34",
        "slab_a": "#17293F", "slab_b": "#0D1B2C",
        "face_l": "#101E30", "face_r": "#0A1523",
        "edge": "#3A5F8C", "border": "#1B2B42",
        "card_a": "#0C1727", "card_b": "#080F1C",
        "text": "#E8F0F7", "muted": "#93A9C0", "dim": "#5C748E",
        "a1": "#22D3EE", "a2": "#2DD4BF", "a3": "#F5A524", "a4": "#A78BFA",
        "shadow": "#000000", "shadowop": "0.55",
        "glowop": "0.34", "vignetteop": "0.55",
    },
    "light": {
        "bg0": "#FFFFFF", "bg1": "#EDF3F9", "bg2": "#E1EBF5",
        "grid": "#8FB2CE", "gridop": "0.20",
        "slab_a": "#FFFFFF", "slab_b": "#E6EFF7",
        "face_l": "#C4D6E5", "face_r": "#AEC4D7",
        "edge": "#A9C3D8", "border": "#CBDCEA",
        "card_a": "#FFFFFF", "card_b": "#F1F6FB",
        "text": "#08172A", "muted": "#476380", "dim": "#7A93AB",
        "a1": "#0E7490", "a2": "#0D9488", "a3": "#B45309", "a4": "#6D28D9",
        "shadow": "#25455F", "shadowop": "0.13",
        "glowop": "0.20", "vignetteop": "0.10",
    },
}

FONT = ("ui-sans-serif,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,"
        "Helvetica Neue,Arial,sans-serif")
MONO = ("ui-monospace,SFMono-Regular,SF Mono,Cascadia Code,Roboto Mono,"
        "Consolas,Liberation Mono,monospace")


# ------------------------------------------------------------------- content

NAME = "Md. Rahat Hossain"
EYEBROW = "CIVIL ENGINEER  &#183;  AUTOMATION  &#183;  DATA"
TAG_1 = "I build the software that runs"
TAG_2 = "the infrastructure I engineer."
META = ("dhaka, bangladesh   &#183;   water &amp; sewerage networks"
        "   &#183;   python &#183; gis &#183; excel")

HW, HH = 1200, 380
SCX = 950.0
HALF, THICK = 58.0, 11.0
LAYERS = [
    ("01", "DECIDE", 84.0, "a4"),
    ("02", "AUTOMATE", 156.0, "a1"),
    ("03", "MODEL", 228.0, "a2"),
    ("04", "FIELD", 300.0, "a3"),
]


def hero_glyphs(key, cy):
    """Per-layer content, drawn on the slab plane and clipped to its top face."""
    g = []
    ox = oy = 10.0   # nudge toward the near half, which stays visible in the stack

    if key == "DECIDE":
        # extruded bars -- the one place the stack breaks its own plane
        for t, h in [(-44, 20), (-22, 36), (0, 26), (22, 48), (44, 38)]:
            top, lf, rt = box(t + ox, -t + oy, 9.0, h, SCX, cy)
            g.append('<path d="%s" fill="$a4" opacity="0.16"/>' % lf)
            g.append('<path d="%s" fill="$a4" opacity="0.32"/>' % rt)
            g.append('<path d="%s" fill="$a4" opacity="0.88"/>' % top)

    elif key == "AUTOMATE":
        for i, w in enumerate([56, 34, 72, 26, 62, 40]):
            y = -38 + i * 15
            p0 = iso(-40 + ox, y + oy, SCX, cy)
            p1 = iso(-40 + w + ox, y + oy, SCX, cy)
            op = "0.85" if i in (0, 2, 4) else "0.42"
            g.append('<path d="M %s L %s" stroke="$a1" stroke-width="4" '
                     'stroke-linecap="round" opacity="%s"/>' % (f(p0), f(p1), op))
        caret = [iso(-54 + ox, -38 + oy, SCX, cy),
                 iso(-46 + ox, -30 + oy, SCX, cy),
                 iso(-54 + ox, -22 + oy, SCX, cy)]
        g.append('<path d="M %s L %s L %s" fill="none" stroke="$a1" stroke-width="3" '
                 'stroke-linecap="round" stroke-linejoin="round"/>'
                 % (f(caret[0]), f(caret[1]), f(caret[2])))

    elif key == "MODEL":
        nodes = [(-46, -26), (-14, -40), (12, -14), (-20, 8),
                 (18, 26), (46, 0), (-42, 34), (6, 46)]
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (3, 6), (4, 7), (2, 5)]
        sp = [iso(x + ox, y + oy, SCX, cy) for (x, y) in nodes]
        for i, j in edges:
            g.append('<path d="M %s L %s" stroke="$a2" stroke-width="1.9" '
                     'opacity="0.75"/>' % (f(sp[i]), f(sp[j])))
        for k, (x, y) in enumerate(nodes):
            if k in (1, 4, 5):   # junction structures stand proud of the network
                top, lf, rt = box(x + ox, y + oy, 5.0, 12.0, SCX, cy)
                g.append('<path d="%s" fill="$a2" opacity="0.20"/>' % lf)
                g.append('<path d="%s" fill="$a2" opacity="0.36"/>' % rt)
                g.append('<path d="%s" fill="$a2" opacity="0.95"/>' % top)
            else:
                g.append('<circle cx="%.2f" cy="%.2f" r="3.6" fill="$a2" '
                         'opacity="0.9"/>' % sp[k])

    elif key == "FIELD":
        for i in range(-2, 3):
            v = i * 24.0
            g.append('<path d="M %s L %s" stroke="$a3" stroke-width="1" opacity="0.34"/>'
                     % (f(iso(v + ox, -50 + oy, SCX, cy)),
                        f(iso(v + ox, 50 + oy, SCX, cy))))
            g.append('<path d="M %s L %s" stroke="$a3" stroke-width="1" opacity="0.34"/>'
                     % (f(iso(-50 + ox, v + oy, SCX, cy)),
                        f(iso(50 + ox, v + oy, SCX, cy))))
        for (x, y) in [(-24, -24), (24, 0), (0, 24), (-48, 24), (48, -48)]:
            g.append('<circle cx="%.2f" cy="%.2f" r="3.2" fill="$a3" opacity="0.95"/>'
                     % iso(x + ox, y + oy, SCX, cy))

    return "\n      ".join(g)


HERO_CSS = (
    ".f{animation:fl 8s ease-in-out infinite}"
    ".f2{animation-delay:-2s}.f3{animation-delay:-4s}.f4{animation-delay:-6s}"
    "@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-5px)}}"
    ".p{animation:rise 3.6s cubic-bezier(.45,0,.35,1) infinite;opacity:0}"
    ".p2{animation-delay:1.2s}.p3{animation-delay:2.4s}"
    ".q{animation:rise 4.4s cubic-bezier(.45,0,.35,1) infinite;opacity:0}"
    ".q2{animation-delay:2.2s}"
    "@keyframes rise{0%{transform:translateY(0);opacity:0}"
    "14%{opacity:1}86%{opacity:.85}100%{transform:translateY(-216px);opacity:0}}"
    ".pulse{animation:pu 6s ease-in-out infinite}"
    "@keyframes pu{0%,100%{opacity:.75}50%{opacity:1}}"
    "@media(prefers-reduced-motion:reduce){"
    ".f,.p,.q,.pulse{animation:none}.p,.q{opacity:.55}}"
)


def build_hero():
    o = []
    o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
             'height="%d" role="img" aria-label="%s. Civil engineer building smarter '
             'infrastructure with code.">' % (HW, HH, HW, HH, NAME))

    o.append('<defs>')
    o.append('<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="$bg0"/>'
             '<stop offset="0.55" stop-color="$bg1"/>'
             '<stop offset="1" stop-color="$bg2"/></linearGradient>')
    o.append('<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">'
             '<stop offset="0" stop-color="$a1" stop-opacity="$glowop"/>'
             '<stop offset="1" stop-color="$a1" stop-opacity="0"/></radialGradient>')
    o.append('<radialGradient id="vig" cx="0.5" cy="0.45" r="0.75">'
             '<stop offset="0.55" stop-color="$bg0" stop-opacity="0"/>'
             '<stop offset="1" stop-color="$bg0" stop-opacity="$vignetteop"/>'
             '</radialGradient>')
    o.append('<linearGradient id="slabf" x1="0" y1="0" x2="0.4" y2="1">'
             '<stop offset="0" stop-color="$slab_a"/>'
             '<stop offset="1" stop-color="$slab_b"/></linearGradient>')
    o.append('<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
             '<stop offset="0" stop-color="$a1"/>'
             '<stop offset="1" stop-color="$a2"/></linearGradient>')
    o.append('<linearGradient id="beam" x1="0" y1="1" x2="0" y2="0">'
             '<stop offset="0" stop-color="$a1" stop-opacity="0"/>'
             '<stop offset="0.5" stop-color="$a1" stop-opacity="0.28"/>'
             '<stop offset="1" stop-color="$a1" stop-opacity="0"/></linearGradient>')
    o.append('<filter id="soft" x="-60%" y="-60%" width="220%" height="220%">'
             '<feGaussianBlur stdDeviation="5"/></filter>')
    o.append('<filter id="tight" x="-80%" y="-80%" width="260%" height="260%">'
             '<feGaussianBlur stdDeviation="2.4"/></filter>')
    o.append('<clipPath id="frame"><rect x="0" y="0" width="%d" height="%d" rx="18"/>'
             '</clipPath>' % (HW, HH))
    for _n, key, cy, _c in LAYERS:
        top, _l, _r, _k = slab(SCX, cy, HALF, THICK)
        o.append('<clipPath id="clip%s"><path d="%s"/></clipPath>' % (key, top))
    o.append('</defs>')

    o.append('<style>%s</style>' % HERO_CSS)

    o.append('<g clip-path="url(#frame)">')
    o.append('<rect width="%d" height="%d" fill="url(#bg)"/>' % (HW, HH))
    o.append('<g opacity="$gridop"><path d="%s" fill="none" stroke="$grid" '
             'stroke-width="0.6"/></g>' % iso_grid(SCX - 120, 250, 520, 42))
    o.append('<ellipse class="pulse" cx="%.0f" cy="200" rx="330" ry="210" '
             'fill="url(#glow)"/>' % SCX)

    # left type block
    o.append('<text x="64" y="120" font-family="%s" font-size="11.5" letter-spacing="3.2" '
             'font-weight="600" fill="$a1">%s</text>' % (MONO, EYEBROW))
    o.append('<text x="62" y="172" font-family="%s" font-size="46" font-weight="700" '
             'letter-spacing="-1.1" fill="$text">%s</text>' % (FONT, NAME))
    o.append('<rect x="64" y="192" width="86" height="3" rx="1.5" fill="url(#rule)"/>')
    o.append('<text x="64" y="232" font-family="%s" font-size="20" fill="$muted">%s</text>'
             % (FONT, TAG_1))
    o.append('<text x="64" y="258" font-family="%s" font-size="20" fill="$muted">%s</text>'
             % (FONT, TAG_2))
    o.append('<text x="64" y="300" font-family="%s" font-size="12.5" fill="$dim">'
             '<tspan fill="$a2">&#9656; </tspan>%s</text>' % (MONO, META))

    # the stack, drawn far-to-near so upper layers overlap lower ones
    o.append('<rect x="%.0f" y="60" width="6" height="250" rx="3" fill="url(#beam)"/>'
             % (SCX - 3))
    for idx, (num, key, cy, col) in enumerate(reversed(LAYERS)):
        cls = ["f f4", "f f3", "f f2", "f"][idx]
        top, lf, rt, k = slab(SCX, cy, HALF, THICK)
        o.append('<g class="%s">' % cls)
        o.append('<ellipse cx="%.0f" cy="%.1f" rx="104" ry="26" fill="$shadow" '
                 'opacity="$shadowop" filter="url(#soft)"/>' % (SCX, cy + 30))
        o.append('<path d="%s" fill="$face_l" stroke="$edge" stroke-width="0.9" '
                 'opacity="0.95"/>' % lf)
        o.append('<path d="%s" fill="$face_r" stroke="$edge" stroke-width="0.9" '
                 'opacity="0.95"/>' % rt)
        o.append('<path d="%s" fill="url(#slabf)" stroke="$edge" stroke-width="1.1"/>' % top)
        o.append('<g clip-path="url(#clip%s)">%s</g>' % (key, hero_glyphs(key, cy)))
        # far edges catch the key light, near edge defines the slab thickness
        o.append('<path d="M %s L %s" stroke="$%s" stroke-width="1.6" opacity="0.55"/>'
                 % (f(k[3]), f(k[0]), col))
        o.append('<path d="M %s L %s" stroke="$%s" stroke-width="1.6" opacity="0.32"/>'
                 % (f(k[0]), f(k[1]), col))
        o.append('<path d="M %s L %s L %s" fill="none" stroke="$%s" stroke-width="1.3" '
                 'opacity="0.45"/>' % (f(k[3]), f(k[2]), f(k[1]), col))
        o.append('<path d="M 830 %.1f L 848 %.1f" stroke="$%s" stroke-width="1.2" '
                 'opacity="0.6"/>' % (cy, cy, col))
        o.append('<circle cx="826" cy="%.1f" r="2.6" fill="$%s"/>' % (cy, col))
        o.append('<text x="814" y="%.1f" text-anchor="end" font-family="%s" font-size="11.5" '
                 'letter-spacing="1.8" font-weight="600" fill="$muted">'
                 '<tspan fill="$dim">%s </tspan>%s</text>' % (cy + 4, MONO, num, key))
        o.append('</g>')

    # Data rising through the stack. The opacity attribute is the fallback for
    # renderers that drop the stylesheet -- any CSS rule outranks it, so the
    # animation still wins wherever CSS survives.
    for cls in ("p", "p p2", "p p3"):
        o.append('<g class="%s" opacity="0"><circle cx="%.0f" cy="300" r="3" fill="$a1" '
                 'filter="url(#tight)"/><circle cx="%.0f" cy="300" r="1.7" fill="$text"/>'
                 '</g>' % (cls, SCX, SCX))
    for cls, dx in (("q", -22), ("q q2", 24)):
        o.append('<g class="%s" opacity="0"><circle cx="%.0f" cy="300" r="2.1" fill="$a2" '
                 'filter="url(#tight)"/></g>' % (cls, SCX + dx))

    o.append('<rect width="%d" height="%d" fill="url(#vig)"/>' % (HW, HH))
    o.append('</g>')
    o.append('<rect x="0.5" y="0.5" width="%.0f" height="%.0f" rx="18" fill="none" '
             'stroke="$border" stroke-width="1"/>' % (HW - 1, HH - 1))
    o.append('</svg>')
    return "\n".join(o)


# --------------------------------------------------------------- stack sheet

SW, SH = 1200, 348
CARD_W, CARD_H, CARD_Y = 270, 300, 24
CARD_X = [24, 318, 612, 906]

COLUMNS = [
    ("a3", "DESIGN &amp; GIS", [
        "AutoCAD", "ArcGIS", "WaterGEMS", "SewerGEMS",
        "Field survey &amp; levelling",
    ]),
    ("a1", "DATA &amp; AUTOMATION", [
        "Python", "Power Query", "Excel automation", "PowerShell", "KoboToolbox",
    ]),
    ("a2", "BUILD", [
        "HTML / CSS / JS", "Google Apps Script", "Git &amp; GitHub",
        "GitHub Pages", "AI-assisted dev",
    ]),
    ("a4", "DOMAIN", [
        "Water distribution networks", "Sewerage &amp; drainage",
        "Construction supervision", "Quantity &amp; progress monitoring",
        "FIDIC contract administration",
    ]),
]


def build_stack():
    o = []
    o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
             'height="%d" role="img" aria-label="Tooling: design and GIS, data and '
             'automation, build, domain.">' % (SW, SH, SW, SH))

    o.append('<defs>')
    o.append('<linearGradient id="sbg" x1="0" y1="0" x2="1" y2="1">'
             '<stop offset="0" stop-color="$bg0"/>'
             '<stop offset="1" stop-color="$bg1"/></linearGradient>')
    o.append('<linearGradient id="card" x1="0" y1="0" x2="0.3" y2="1">'
             '<stop offset="0" stop-color="$card_a"/>'
             '<stop offset="1" stop-color="$card_b"/></linearGradient>')
    o.append('</defs>')

    o.append('<rect width="%d" height="%d" rx="18" fill="url(#sbg)"/>' % (SW, SH))
    o.append('<g opacity="$gridop"><path d="%s" fill="none" stroke="$grid" '
             'stroke-width="0.5"/></g>' % iso_grid(600, 174, 620, 46))

    for i, (col, title, items) in enumerate(COLUMNS):
        x = CARD_X[i]
        o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="14" fill="url(#card)" '
                 'stroke="$border" stroke-width="1"/>' % (x, CARD_Y, CARD_W, CARD_H))
        o.append('<rect x="%d" y="%d" width="34" height="3" rx="1.5" fill="$%s"/>'
                 % (x + 20, CARD_Y + 24, col))
        o.append('<text x="%d" y="%d" font-family="%s" font-size="11.5" letter-spacing="2.4" '
                 'font-weight="700" fill="$%s">%s</text>'
                 % (x + 20, CARD_Y + 60, MONO, col, title))
        for j, item in enumerate(items):
            y = CARD_Y + 102 + j * 30
            o.append('<rect x="%d" y="%d" width="6" height="6" rx="1" fill="$%s" '
                     'opacity="0.75" transform="rotate(45 %d %d)"/>'
                     % (x + 21, y - 5, col, x + 24, y - 2))
            o.append('<text x="%d" y="%d" font-family="%s" font-size="13" fill="$muted">'
                     '%s</text>' % (x + 38, y, FONT, item))
        # isometric cube motif, ties the sheet back to the hero
        mx, my = x + CARD_W - 46, CARD_Y + CARD_H - 40
        top, lf, rt, _k = slab(mx, my - 20, 18.0, 20.0)
        o.append('<g opacity="0.30"><path d="%s" fill="none" stroke="$%s" '
                 'stroke-width="1.2"/><path d="%s" fill="none" stroke="$%s" '
                 'stroke-width="1.2"/><path d="%s" fill="none" stroke="$%s" '
                 'stroke-width="1.2"/></g>' % (lf, col, rt, col, top, col))

    o.append('<rect x="0.5" y="0.5" width="%.0f" height="%.0f" rx="18" fill="none" '
             'stroke="$border" stroke-width="1"/>' % (SW - 1, SH - 1))
    o.append('</svg>')
    return "\n".join(o)


# ---------------------------------------------------------------------- main

def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "assets")
    os.makedirs(out, exist_ok=True)

    for name, builder in (("hero", build_hero), ("stack", build_stack)):
        body = Template(builder())
        for theme, palette in PALETTES.items():
            path = os.path.join(out, "%s-%s.svg" % (name, theme))
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(body.substitute(palette))
            print("wrote %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    main()
