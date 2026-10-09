#!/usr/bin/env python3
"""Generates the animated SVG assets used by the profile README.

Every asset is a self-contained SVG (inline CSS + SMIL, no scripts, no external
fonts) so GitHub can render it through <img>. Run:  python3 scripts/generate.py

Design rules shared by every file:
  * the *resting* style of each element is its final, visible state, and
    entrance keyframes run with `animation-fill-mode: both`; so with
    prefers-reduced-motion (all animations disabled) everything is readable.
  * text that has to fit a fixed box uses textLength, so fallback fonts can't
    break the layout.
"""
import json
import math
import os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")
ICONS = json.load(open(os.path.join(os.path.dirname(__file__), "icons.json")))

# ---------------------------------------------------------------- tokens ---
# Palette follows ahmetakyapi.com (deep navy, ice ink, blue / violet / teal).
BG = "#050a14"
SURFACE = "#0a1322"
INK = "#e3e9f0"
MUTED = "#7d8aa0"
DIM = "#2a3446"
BLUE = "#3b9cff"
VIOLET = "#8b7bff"
TEAL = "#5eead4"

SANS = "'Inter','SF Pro Display','Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
SERIF = "'Instrument Serif','Playfair Display','Iowan Old Style',Georgia,'Times New Roman',serif"
MONO = "'JetBrains Mono','SF Mono',ui-monospace,Menlo,Consolas,'DejaVu Sans Mono',monospace"

EXPO_OUT = "cubic-bezier(.16,1,.3,1)"
EXPO_IN_OUT = "cubic-bezier(.76,0,.24,1)"

BASE_CSS = f"""
.sans{{font-family:{SANS}}}
.serif{{font-family:{SERIF};font-style:italic;font-weight:400}}
.mono{{font-family:{MONO};letter-spacing:.12em}}
.rise{{animation:rise 1.1s {EXPO_OUT} both}}
.rise-xl{{animation:rise-xl 1.3s {EXPO_OUT} both}}
.fade{{animation:fade 1s ease both}}
.fade-up{{animation:fade-up 1s {EXPO_OUT} both}}
.draw-x{{transform-box:fill-box;transform-origin:0 50%;animation:draw-x 1.4s {EXPO_IN_OUT} both}}
.draw-y{{transform-box:fill-box;transform-origin:50% 0;animation:draw-y 1.4s {EXPO_IN_OUT} both}}
.pop{{transform-box:fill-box;transform-origin:center;animation:pop .9s {EXPO_OUT} both}}
.spin{{transform-box:fill-box;transform-origin:center;animation:spin 18s linear infinite}}
.pulse{{transform-box:fill-box;transform-origin:center;animation:pulse 2.4s ease-out infinite}}
.blink{{animation:blink 1.6s ease-in-out infinite}}
@keyframes rise{{from{{transform:translateY(80px)}}}}
@keyframes rise-xl{{from{{transform:translateY(260px)}}}}
@keyframes fade{{from{{opacity:0}}}}
@keyframes fade-up{{from{{opacity:0;transform:translateY(24px)}}}}
@keyframes draw-x{{from{{transform:scaleX(0)}}}}
@keyframes draw-y{{from{{transform:scaleY(0)}}}}
@keyframes pop{{from{{transform:scale(0)}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes pulse{{0%{{transform:scale(.6);opacity:.9}}100%{{transform:scale(2.6);opacity:0}}}}
@keyframes blink{{50%{{opacity:.25}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def d(sec):
    """Inline animation-delay."""
    return f'style="animation-delay:{sec:.2f}s"'


def svg(w, h, body, css="", defs="", title="", radius=28, bg=BG):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<defs>
<clipPath id="card"><rect width="{w}" height="{h}" rx="{radius}"/></clipPath>
<filter id="grain" x="0" y="0" width="100%" height="100%">
<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>
<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/>
</filter>
{defs}
</defs>
<style>{BASE_CSS}{css}</style>
<g clip-path="url(#card)">
<rect width="{w}" height="{h}" fill="{bg}"/>
{body}
<rect width="{w}" height="{h}" filter="url(#grain)" opacity=".05"/>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{radius}" fill="none" stroke="{INK}" stroke-opacity=".08"/>
</svg>
"""


def masked(cid, x, y, w, h, inner, cls="rise", delay=0.0):
    """A line of content that slides up from behind a clip window."""
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><g class="{cls}" {d(delay)}>{inner}</g></g>')


def rich(parts):
    """[('text', 'serif'|None|'#color'|...)] -> tspans. Style tuple: (text, cls, fill)."""
    out = []
    for p in parts:
        text, cls, fill = (p + (None, None))[:3] if isinstance(p, tuple) else (p, None, None)
        a = []
        if cls:
            a.append(f'class="{cls}"')
        if fill:
            a.append(f'fill="{fill}"')
        out.append(f'<tspan {" ".join(a)}>{escape(text)}</tspan>')
    return "".join(out)


def header_row(w, index, label, right, delay=0.1):
    """Top meta row used by every section card: (01) LABEL ............ RIGHT."""
    return f"""
{masked(f"hr{index}a", 0, 40, w / 2, 40,
        f'<text x="56" y="68" class="mono" font-size="13" fill="{MUTED}"><tspan fill="{TEAL}">({index:02d})</tspan>  {escape(label)}</text>',
        delay=delay)}
{masked(f"hr{index}b", w / 2, 40, w / 2, 40,
        f'<text x="{w - 56}" y="68" text-anchor="end" class="mono" font-size="13" fill="{MUTED}">{escape(right)}</text>',
        delay=delay + .08)}
<rect x="56" y="92" width="{w - 112}" height="1" fill="{INK}" fill-opacity=".14" class="draw-x" {d(delay + .1)}/>
"""


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  assets/{name:<22} {len(content.encode()) / 1024:6.1f} KB")


# ================================================================== HERO ===
def hero():
    W, H = 1200, 700
    cols = 6
    colw = W / cols
    LOAD = 2.0          # counter finishes
    REVEAL = 2.75       # hero content starts

    # Preloader: odometer counter + progress bar on an ice-white sheet.
    steps = ["000", "007", "019", "034", "048", "063", "079", "091", "100"]
    rowh = 150
    reel = "".join(f'<text x="0" y="{i * rowh}" class="mono" font-size="150" letter-spacing="-6" fill="{BG}">{s}</text>'
                   for i, s in enumerate(steps))
    n = len(steps) - 1
    kf = ["0%{transform:translateY(0)}"]
    for i in range(1, n + 1):
        pct = 100 * i / n
        kf.append(f"{pct - 100 / n * .45:.1f}%{{transform:translateY({-(i - 1) * rowh}px);animation-timing-function:{EXPO_IN_OUT}}}"
                  f"{pct:.1f}%{{transform:translateY({-i * rowh}px)}}")
    reel_css = ("@keyframes reel{" + "".join(kf) + "}"
                f".reel{{animation:reel {LOAD - .2:.2f}s linear .2s both;transform:translateY({-n * rowh}px)}}")

    sheets = []
    for i in range(cols):
        x = i * colw
        sheets.append(f'<rect class="wipe" x="{x - .5:.1f}" y="0" width="{colw + 1:.1f}" height="{H}" fill="{BLUE}" {d(LOAD + .25 + i * .055)}/>')
    for i in range(cols):
        x = i * colw
        sheets.append(f'<rect class="wipe" x="{x - .5:.1f}" y="0" width="{colw + 1:.1f}" height="{H}" fill="{INK}" {d(LOAD + .05 + i * .055)}/>')

    loader = f"""
<g class="loader-out" {d(LOAD - .05)}>
  <text x="56" y="68" class="mono" font-size="13" fill="{BG}">AHMET AKYAPI — PORTFOLIO</text>
  <text x="{W - 56}" y="68" text-anchor="end" class="mono" font-size="13" fill="{BG}">LOADING EXPERIENCE</text>
  <g transform="translate(56 560)">
    <clipPath id="reelclip"><rect x="0" y="-124" width="600" height="150"/></clipPath>
    <g clip-path="url(#reelclip)"><g class="reel">{reel}</g></g>
  </g>
  <text x="{W - 56}" y="560" text-anchor="end" class="serif" font-size="64" fill="{BG}">Full-Stack &amp; AI</text>
  <rect x="56" y="610" width="{W - 112}" height="2" fill="{BG}" fill-opacity=".15"/>
  <rect x="56" y="610" width="{W - 112}" height="2" fill="{BG}" class="bar"/>
  <text x="56" y="646" class="mono" font-size="12" fill="{BG}" fill-opacity=".6">ISTANBUL, TR</text>
  <text x="{W - 56}" y="646" text-anchor="end" class="mono" font-size="12" fill="{BG}" fill-opacity=".6">©2026</text>
</g>"""

    css = reel_css + f"""
.wipe{{transform:translateY(-{H + 10}px);animation:wipe 1s {EXPO_IN_OUT} both}}
@keyframes wipe{{from{{transform:translateY(0)}}}}
.loader-out{{opacity:0;animation:loader-out .45s ease-in both}}
@keyframes loader-out{{from{{opacity:1}}to{{opacity:0;transform:translateY(-30px)}}}}
.bar{{transform-box:fill-box;transform-origin:0 50%;animation:bar {LOAD - .2:.2f}s cubic-bezier(.65,0,.35,1) .2s both}}
@keyframes bar{{from{{transform:scaleX(0)}}}}
.blob{{transform-box:fill-box;transform-origin:center}}
.b1{{animation:drift1 16s ease-in-out infinite alternate}}
.b2{{animation:drift2 19s ease-in-out infinite alternate}}
.b3{{animation:drift3 13s ease-in-out infinite alternate}}
@keyframes drift1{{to{{transform:translate(-180px,-90px) scale(1.15)}}}}
@keyframes drift2{{to{{transform:translate(220px,120px) scale(.85)}}}}
@keyframes drift3{{to{{transform:translate(-120px,80px) scale(1.3)}}}}
.marquee{{animation:marquee 32s linear infinite}}
@keyframes marquee{{to{{transform:translateX(-1500px)}}}}
"""

    defs = f"""
<filter id="blur" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="90"/></filter>
<linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="330" y1="0" x2="1110" y2="0">
  <stop offset="0" stop-color="{INK}"/><stop offset=".38" stop-color="{INK}"/>
  <stop offset=".48" stop-color="{VIOLET}"/><stop offset=".55" stop-color="{TEAL}"/>
  <stop offset=".66" stop-color="{INK}"/><stop offset="1" stop-color="{INK}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="-900 0;900 0;900 0" keyTimes="0;.55;1" dur="7s" begin="{REVEAL + .8}s" repeatCount="indefinite"/>
</linearGradient>
<path id="ring" d="M 0,-74 a 74,74 0 1,1 0,148 a 74,74 0 1,1 0,-148"/>
"""

    grid = "".join(
        f'<rect x="{56 + i * (W - 112) / 6:.1f}" y="92" width="1" height="528" fill="{INK}" fill-opacity=".05" class="draw-y" {d(REVEAL - .3 + i * .06)}/>'
        for i in range(7))

    items = ["Next.js", "React", "TypeScript", "AI Agents", "PostgreSQL", "Angular", "Node.js", "Motion", "Drizzle", "Tailwind"]

    def marquee_line(x):
        parts = []
        for i, it in enumerate(items):
            parts.append((it + "  ", "serif" if i % 2 else None, INK if i % 2 == 0 else MUTED))
            parts.append(("✦  ", None, TEAL))
        return f'<text x="{x}" y="672" class="sans" font-size="30" font-weight="500" textLength="1480" lengthAdjust="spacingAndGlyphs">{rich(parts)}</text>'

    para = ["( FULL-STACK & AI DEVELOPER )", "I build web products end to",
            "end — interface, system and", "ship. Fast to load, easy to", "read, correct to run."]
    para_svg = "".join(
        masked(f"p{i}", 56, 392 + i * 26 - 20, 300, 28,
               f'<text x="56" y="{392 + i * 26}" class="mono" font-size="12.5" fill="{TEAL if i == 0 else MUTED}" letter-spacing=".04em">{escape(t)}</text>',
               delay=REVEAL + .45 + i * .07)
        for i, t in enumerate(para))

    body = f"""
<g filter="url(#blur)" class="fade" {d(REVEAL - .2)}>
  <circle class="blob b1" cx="980" cy="520" r="250" fill="#1d4ed8" opacity=".55"/>
  <circle class="blob b2" cx="220" cy="140" r="210" fill="#5b42d6" opacity=".5"/>
  <circle class="blob b3" cx="720" cy="360" r="140" fill="#2f7a6d" opacity=".55"/>
</g>
{grid}

{masked("m1", 0, 40, 400, 40, f'<text x="56" y="68" class="mono" font-size="13" fill="{MUTED}">AHMET AKYAPI <tspan fill="{TEAL}">©2026</tspan></text>', delay=REVEAL)}
{masked("m2", 400, 40, 400, 40, f'<text x="600" y="68" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">41.0082° N — 28.9784° E</text>', delay=REVEAL + .08)}
{masked("m3", 800, 40, 400, 40, f'<text x="{W - 80}" y="68" text-anchor="end" class="mono" font-size="13" fill="{INK}">BUILDING WITH AI AGENTS</text>', delay=REVEAL + .16)}
<g class="pop" {d(REVEAL + .4)}><circle cx="{W - 62}" cy="63" r="5" fill="{TEAL}"/></g>
<circle class="pulse" cx="{W - 62}" cy="63" r="5" fill="{TEAL}"/>
<rect x="56" y="92" width="{W - 112}" height="1" fill="{INK}" fill-opacity=".14" class="draw-x" {d(REVEAL)}/>

{masked("t1", 0, 110, W, 240, f'<text x="44" y="310" class="sans" font-size="236" font-weight="700" fill="{INK}" textLength="650" lengthAdjust="spacingAndGlyphs">Ahmet</text>', cls="rise-xl", delay=REVEAL + .1)}
{masked("t2", 0, 345, W, 270, f'<text x="350" y="560" class="serif" font-size="262" fill="url(#sheen)" textLength="760" lengthAdjust="spacingAndGlyphs">Akyapı</text>', cls="rise-xl", delay=REVEAL + .24)}
{para_svg}

{masked("c1", 700, 150, 260, 26, f'<text x="720" y="170" class="mono" font-size="12" fill="{MUTED}">CURRENTLY</text>', delay=REVEAL + .5)}
{masked("c2", 700, 178, 260, 30, f'<text x="720" y="200" class="sans" font-size="20" fill="{INK}">AI Developer <tspan class="serif" fill="{TEAL}">at</tspan> Nar</text>', delay=REVEAL + .58)}
{masked("c3", 700, 210, 260, 26, f'<text x="720" y="230" class="mono" font-size="12" fill="{MUTED}">ENERGY · SINCE 2021</text>', delay=REVEAL + .66)}

<g transform="translate(1050 230)">
  <g class="pop" {d(REVEAL + .7)}>
    <g class="spin">
      <text class="mono" font-size="12.5" fill="{INK}" letter-spacing=".3em"><textPath href="#ring" textLength="462">FULL-STACK · AI DEVELOPER · ISTANBUL · </textPath></text>
    </g>
    <circle r="46" fill="{TEAL}"/>
    <g class="spin" style="animation-duration:9s;animation-direction:reverse">
      <path d="M0 -20 L4 -4 L20 0 L4 4 L0 20 L-4 4 L-20 0 L-4 -4 Z" fill="{BG}"/>
    </g>
  </g>
</g>

<g class="fade" {d(REVEAL + .6)}>
  <rect x="0" y="620" width="{W}" height="80" fill="{BG}" fill-opacity=".55"/>
  <rect x="0" y="620" width="{W}" height="1" fill="{INK}" fill-opacity=".14"/>
  <g class="marquee">{marquee_line(0)}{marquee_line(1500)}</g>
</g>

<g>{"".join(sheets)}</g>
{loader}
"""
    write("hero.svg", svg(W, H, body, css, defs,
                          "Ahmet Akyapı — Full-Stack & AI Developer, Istanbul. Currently AI Developer at Nar Sistem Teknoloji."))


# ================================================================= ABOUT ===
def about():
    W, H = 1200, 640
    lines = [
        [("I build web products ", None), ("end to end", "serif", TEAL), (" —", None)],
        [("designing the interface and the system,", None)],
        [("then shipping it. From enterprise ", None), ("energy", "serif", TEAL)],
        [("systems", "serif", TEAL), (" to my own products, I chase", None)],
        [("work that's ", None), ("fast, clear", "serif", TEAL), (" and ", None), ("correct.", "serif", TEAL)],
    ]
    out = []
    for i, ln in enumerate(lines):
        y = 196 + i * 64
        x = 176 if i == 0 else 56
        out.append(masked(f"l{i}", 0, y - 54, W, 70,
                          f'<text x="{x}" y="{y}" class="sans lit" font-size="46" font-weight="500" letter-spacing="-.02em" {d(1.1 + i * .32)}>{rich(ln)}</text>',
                          delay=.25 + i * .09))

    cols = [("ROLE", "AI Developer @ Nar"), ("EXPERIENCE", "Since 2021 · Energy"),
            ("SHIPPED", "13 own products"), ("BASED IN", "Istanbul, Turkey")]
    info = []
    cw = (W - 112) / 4
    for i, (k, v) in enumerate(cols):
        x = 56 + i * cw
        info.append(masked(f"i{i}a", x, 528, cw, 26, f'<text x="{x}" y="546" class="mono" font-size="11.5" fill="{MUTED}">{k}</text>', delay=.9 + i * .08))
        info.append(masked(f"i{i}b", x, 556, cw, 34, f'<text x="{x}" y="582" class="sans" font-size="21" fill="{INK}">{escape(v)}</text>', delay=.98 + i * .08))
        if i:
            info.append(f'<rect x="{x - 20:.1f}" y="528" width="1" height="60" fill="{INK}" fill-opacity=".1" class="draw-y" {d(.9 + i * .08)}/>')

    star = "".join(f'<rect x="-2" y="-34" width="4" height="68" rx="2" fill="{TEAL}" transform="rotate({a})"/>' for a in range(0, 180, 30))
    css = f"""
.lit{{fill:{INK};animation:lit 1.2s ease both}}
@keyframes lit{{from{{fill:{DIM}}}}}
"""
    body = f"""
{header_row(W, 1, "ABOUT", "WHO I AM")}
<g transform="translate(96 152)"><g class="pop" {d(.4)}><g class="spin" style="animation-duration:14s">{star}</g></g></g>
{"".join(out)}
<rect x="56" y="500" width="{W - 112}" height="1" fill="{INK}" fill-opacity=".14" class="draw-x" {d(.8)}/>
{"".join(info)}
"""
    write("about.svg", svg(W, H, body, css, title=(
        "About — I build web products end to end: designing the interface and the system, then shipping it. "
        "From enterprise energy systems to my own products, I chase work that's fast, clear and correct. "
        "AI Developer at Nar, since 2021 in energy, 13 own products, based in Istanbul.")))


# ================================================================= STACK ===
STACK_ROWS = [
    [("nextdotjs", "Next.js", INK), ("react", "React", "#61dafb"), ("typescript", "TypeScript", "#4b8fe0"),
     ("tailwindcss", "Tailwind CSS", "#38bdf8"), ("angular", "Angular", "#f0365b"), ("framer", "Framer Motion", "#ff4fd8"),
     ("figma", "Figma", "#ff7262")],
    [("postgresql", "PostgreSQL", "#7aa2ff"), ("drizzle", "Drizzle ORM", "#c5f74f"), ("nodedotjs", "Node.js", "#5fa04e"),
     ("socketdotio", "Socket.io", INK), ("vitest", "Vitest", "#fcc72b"), ("vercel", "Vercel", INK),
     ("claude", "Claude", "#d97757"), ("git", "Git", "#f05032")],
]


def pill(slug, label, color, x, y):
    w = 78 + len(label) * 11.6
    return w, f"""<g transform="translate({x:.1f} {y})">
<rect width="{w:.1f}" height="60" rx="30" fill="{SURFACE}" stroke="{INK}" stroke-opacity=".1"/>
<use href="#i-{slug}" x="22" y="18" width="24" height="24" fill="{color}"/>
<text x="58" y="38" class="sans" font-size="20" fill="{INK}">{escape(label)}</text>
</g>"""


def stack():
    W, H = 1200, 600
    cats = [("FRONTEND", ["Next.js", "React", "TypeScript", "Angular", "Tailwind CSS"]),
            ("BACKEND", ["Node.js", "PostgreSQL · Neon", "Drizzle ORM", "Socket.io", "Vitest"]),
            ("WORKFLOW", ["AI agents", "Claude", "Vercel", "Figma", "Git"])]
    cat_svg = []
    for c, (name, items) in enumerate(cats):
        x = 560 + c * 200
        cat_svg.append(masked(f"c{c}", x, 122, 200, 26, f'<text x="{x}" y="140" class="mono" font-size="11.5" fill="{TEAL}">{name}</text>', delay=.4 + c * .1))
        for i, it in enumerate(items):
            y = 176 + i * 30
            cat_svg.append(masked(f"c{c}i{i}", x, y - 22, 200, 30,
                                  f'<text x="{x}" y="{y}" class="sans" font-size="17" fill="{INK}"><tspan class="mono" font-size="10" fill="{MUTED}">0{i + 1}  </tspan>{escape(it)}</text>',
                                  delay=.5 + c * .1 + i * .05))

    rows = []
    css = ""
    for r, row in enumerate(STACK_ROWS):
        y = 370 + r * 84
        x = 0
        pills = []
        for rep in range(2):
            for slug, label, color in row:
                w, p = pill(slug, label, color, x, y)
                pills.append(p)
                x += w + 14
        span = x / 2
        name = f"row{r}"
        direction = "normal" if r == 0 else "reverse"
        css += f".{name}{{animation:{name} {span / 38:.1f}s linear infinite {direction}}}@keyframes {name}{{to{{transform:translateX(-{span:.1f}px)}}}}"
        rows.append(f'<g class="fade-up" {d(.9 + r * .15)}><g class="{name}">{"".join(pills)}</g></g>')

    defs = f"""
<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".1" stop-color="#fff"/><stop offset=".9" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
{"".join(f'<symbol id="i-{slug}" viewBox="0 0 24 24"><path d="{ICONS[slug]}"/></symbol>' for row in STACK_ROWS for slug, _, _ in row)}
<mask id="fadeEdges"><rect width="{W}" height="{H}" fill="url(#edge)"/></mask>
"""
    body = f"""
{header_row(W, 2, "TOOLKIT", "WHAT I REACH FOR DAILY")}
{masked("h1", 0, 122, 540, 110, f'<text x="56" y="214" class="sans" font-size="96" font-weight="600" letter-spacing="-.04em" fill="{INK}">Tools of</text>', cls="rise-xl", delay=.2)}
{masked("h2", 0, 232, 540, 110, f'<text x="56" y="318" class="serif" font-size="108" fill="{TEAL}">the craft.</text>', cls="rise-xl", delay=.32)}
{"".join(cat_svg)}
<g mask="url(#fadeEdges)">{"".join(rows)}</g>
"""
    write("stack.svg", svg(W, H, body, css, defs, title=(
        "Toolkit — Frontend: Next.js, React, TypeScript, Angular, Tailwind CSS. "
        "Backend: Node.js, PostgreSQL (Neon), Drizzle ORM, Socket.io, Vitest. Workflow: AI agents, Claude, Vercel, Figma, Git.")))


# ============================================================ EXPERIENCE ===
def experience():
    W, H = 1200, 600
    roles = [
        ("2026 — NOW", "AI Developer", "Nar", "Enterprise software for the energy sector.", TEAL),
        ("2024 — 2026", "Full-Stack Developer", "Nar", "End-to-end features, from interface to system.", BLUE),
        ("2021 — 2023", "Frontend Developer", "Nar", "Interfaces for enterprise energy products.", VIOLET),
    ]
    out = []
    top = 250
    gap = 108
    out.append(f'<rect x="300" y="{top - 8}" width="2" height="{gap * 2 + 16}" fill="{INK}" fill-opacity=".14"/>')
    out.append(f'<rect x="300" y="{top - 8}" width="2" height="{gap * 2 + 16}" fill="{TEAL}" class="draw-y" style="animation-duration:2.2s;animation-delay:.6s"/>')
    for i, (when, role, project, desc, color) in enumerate(roles):
        y = top + i * gap
        t = .7 + i * .45
        out.append(masked(f"w{i}", 40, y - 18, 240, 30, f'<text x="260" y="{y + 5}" text-anchor="end" class="mono" font-size="12.5" fill="{MUTED}">{when}</text>', delay=t))
        out.append(f'<g class="pop" {d(t)}><circle cx="301" cy="{y}" r="8" fill="{BG}" stroke="{color}" stroke-width="2"/><circle cx="301" cy="{y}" r="3.5" fill="{color}"/></g>')
        if i == 0:
            out.append(f'<circle class="pulse" cx="301" cy="{y}" r="7" fill="{TEAL}"/>')
        out.append(masked(f"r{i}", 340, y - 34, 520, 46,
                          f'<text x="340" y="{y + 9}" class="sans" font-size="32" font-weight="500" letter-spacing="-.02em" fill="{INK}">{escape(role)} <tspan class="serif" fill="{color}">· {escape(project)}</tspan></text>',
                          delay=t + .05))
        out.append(masked(f"s{i}", 340, y + 18, 560, 30, f'<text x="340" y="{y + 40}" class="sans" font-size="17" fill="{MUTED}">{escape(desc)}</text>', delay=t + .12))

    side = [("AI-NATIVE WORKFLOW", TEAL), ("Research, design QA, tests", INK), ("and copy run on agents I", INK),
            ("built. I decide what ships.", INK), ("", INK), ("+ R&amp;D and TÜBİTAK projects", MUTED)]
    side_svg = "".join(
        masked(f"sd{i}", 900, 250 + i * 28 - 22, 260, 30,
               f'<text x="912" y="{250 + i * 28}" class="{"mono" if i in (0, 5) else "sans"}" font-size="{11.5 if i in (0, 5) else 17}" fill="{c}">{t}</text>',
               delay=1.6 + i * .07)
        for i, (t, c) in enumerate(side) if t)
    body = f"""
{header_row(W, 3, "EXPERIENCE", "WHERE I WORK")}
{masked("h", 0, 112, W, 96, f'<text x="56" y="186" class="sans" font-size="72" font-weight="600" letter-spacing="-.04em" fill="{INK}">Five years in <tspan class="serif" font-weight="400" fill="{TEAL}">energy.</tspan></text>', cls="rise-xl", delay=.2)}
{"".join(out)}
<rect x="892" y="228" width="1" height="160" fill="{INK}" fill-opacity=".12" class="draw-y" {d(1.5)}/>
{side_svg}
<rect x="56" y="{H - 64}" width="{W - 112}" height="1" fill="{INK}" fill-opacity=".1" class="draw-x" {d(1.8)}/>
{masked("ft", 0, H - 58, W, 34, f'<text x="56" y="{H - 34}" class="mono" font-size="11.5" fill="{MUTED}">NAR SISTEM TEKNOLOJI · ENERGY</text><text x="{W - 56}" y="{H - 34}" text-anchor="end" class="mono" font-size="11.5" fill="{MUTED}">2021 → TODAY</text>', delay=2)}
"""
    write("experience.svg", svg(W, H, body, title=(
        "Experience at Nar Sistem Teknoloji (energy): AI Developer, 2026–now; Full-Stack Developer, 2024–2026; "
        "Frontend Developer, 2021–2023. Plus R&D and TÜBİTAK projects. Research, design QA, tests and copy run on AI agents I built.")))


# ================================================================== WORK ===
def work_header():
    W, H = 1200, 300
    body = f"""
{header_row(W, 4, "SELECTED WORK", "13 PRODUCTS · 5 FIELDS")}
{masked("h", 0, 112, W, 170, f'<text x="50" y="250" class="sans" font-size="150" font-weight="700" letter-spacing="-.05em" fill="{INK}" textLength="560" lengthAdjust="spacingAndGlyphs">Selected</text>', cls="rise-xl", delay=.15)}
{masked("h2", 0, 112, W, 170, f'<text x="640" y="250" class="serif" font-size="164" fill="{TEAL}" textLength="330" lengthAdjust="spacingAndGlyphs">work</text>', cls="rise-xl", delay=.28)}
{masked("n", 980, 130, 180, 60, f'<text x="1000" y="170" class="mono" font-size="22" fill="{MUTED}">(06)</text>', delay=.5)}
"""
    write("work.svg", svg(W, H, body, title="Selected work — six featured products out of thirteen."))


def motif_chart(c):
    pts = [(0, 120), (40, 104), (80, 112), (120, 82), (160, 90), (200, 60), (240, 72), (280, 40), (320, 52), (360, 24), (400, 30), (440, 8)]
    path = "M" + " L".join(f"{x} {y}" for x, y in pts)
    candles = []
    for i in range(11):
        x = 20 + i * 40
        h = 18 + (i * 37 % 26)
        y = 150 - h
        candles.append(f'<rect x="{x}" y="{y}" width="12" height="{h}" rx="2" fill="{c}" opacity=".22" class="bob" style="animation-delay:{i * .18:.2f}s"/>')
    return f"""
<g transform="translate(80 20)">
{"".join(candles)}
<path d="{path} L440 160 L0 160 Z" fill="url(#area)" opacity=".5"/>
<path d="{path}" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" class="trace"/>
<circle cx="440" cy="8" r="6" fill="{c}"/><circle cx="440" cy="8" r="6" fill="{c}" class="pulse"/>
<text x="440" y="-2" dx="-14" text-anchor="end" class="mono" font-size="12" fill="{c}">US MARKETS · DAILY BULLETIN</text>
</g>"""


def motif_notes(c):
    cards = []
    for i, (rot, dx, label) in enumerate([(-9, -70, "FILM"), (4, 40, "BOOK"), (-2, 150, "GAME")]):
        cards.append(f"""<g transform="translate({230 + dx} 92) rotate({rot})"><g class="float" style="animation-delay:{i * .7:.1f}s">
<rect x="-64" y="-80" width="128" height="160" rx="12" fill="{SURFACE}" stroke="{c}" stroke-opacity=".45"/>
<rect x="-48" y="-62" width="96" height="70" rx="6" fill="{c}" opacity="{.12 + i * .06:.2f}"/>
<text x="-48" y="30" class="mono" font-size="11" fill="{c}">{label}</text>
<rect x="-48" y="42" width="80" height="5" rx="2.5" fill="{INK}" opacity=".18"/><rect x="-48" y="54" width="56" height="5" rx="2.5" fill="{INK}" opacity=".12"/>
</g></g>""")
    stars = "".join(f'<path transform="translate({462 + i * 24} 178) scale(.45)" d="M0 -20 L6 -6 L21 -6 L9 3 L13 18 L0 9 L-13 18 L-9 3 L-21 -6 L-6 -6Z" fill="{c}" class="twinkle" style="animation-delay:{i * .25:.2f}s"/>' for i in range(5))
    return "".join(cards) + stars


def motif_calm(c):
    rings = "".join(f'<circle cx="300" cy="96" r="{18 + i * 18}" fill="none" stroke="{c}" stroke-opacity="{.6 - i * .1:.2f}" class="breathe" style="animation-delay:{i * .35:.2f}s"/>' for i in range(5))
    return f"""{rings}<circle cx="300" cy="96" r="12" fill="{c}"/>
<text x="300" y="196" text-anchor="middle" class="mono blink" font-size="11" fill="{c}">INHALE · HOLD · EXHALE</text>"""


def motif_pitch(c):
    return f"""<g transform="translate(110 14)" fill="none" stroke="{c}" stroke-opacity=".5" stroke-width="1.5">
<rect width="380" height="170" rx="6"/><line x1="190" y1="0" x2="190" y2="170"/><circle cx="190" cy="85" r="30"/>
<rect x="0" y="45" width="44" height="80"/><rect x="336" y="45" width="44" height="80"/>
</g>
<path id="ballpath" d="M180 150 C 240 40, 330 160, 420 70 S 500 120, 470 99" fill="none"/>
{"".join(f'<circle cx="{x}" cy="{y}" r="6" fill="{c}" opacity=".85" class="float" style="animation-delay:{i * .4:.1f}s"/>' for i, (x, y) in enumerate([(180, 150), (260, 70), (330, 140), (420, 70), (380, 40), (220, 120)]))}
<circle r="7" fill="{INK}"><animateMotion dur="4s" repeatCount="indefinite" rotate="auto"><mpath href="#ballpath"/></animateMotion></circle>
<text x="490" y="204" text-anchor="end" class="mono" font-size="12" fill="{c}">16 FRIENDS · 1 LEAGUE</text>"""


def motif_waves(c):
    def wave(y, amp, op, dur, i):
        segs = "".join(f" q 50 {-amp if k % 2 == 0 else amp} 100 0" for k in range(14))
        return f'<path d="M -200 {y}{segs} V 220 H -200 Z" fill="{c}" opacity="{op}" class="wave" style="animation-duration:{dur}s;animation-delay:{-i}s"/>'
    compass = "".join(f'<rect x="-1.5" y="-46" width="3" height="{14 if a % 90 else 22}" fill="{INK}" opacity=".6" transform="rotate({a})"/>' for a in range(0, 360, 30))
    return f"""<g transform="translate(450 70)"><g class="spin" style="animation-duration:24s">{compass}<path d="M0 -36 L8 0 L0 36 L-8 0 Z" fill="{c}"/></g></g>
{wave(150, 12, .18, 7, 0)}{wave(166, 9, .28, 5, 1)}{wave(184, 7, .45, 4, 2)}
<text x="60" y="44" class="mono" font-size="12" fill="{c}">SPOILER-SAFE  ·  NO FILLER</text>"""


def motif_dungeon(c):
    tiles = []
    for r in range(4):
        for col in range(12):
            x, y = 72 + col * 38, 12 + r * 38
            seed = (r * 7 + col * 13) % 10
            op = .05 + seed * .016
            cls = ' class="torch"' if seed in (3, 7) else ""
            tiles.append(f'<rect x="{x}" y="{y}" width="34" height="34" rx="4" fill="{c}" opacity="{op:.2f}"{cls} style="animation-delay:{seed * .3:.1f}s"/>')
    heroes = "".join(f'<rect x="{x}" y="{y}" width="20" height="20" rx="3" fill="{col}" class="hop" style="animation-delay:{i * .2:.1f}s"/>' for i, (x, y, col) in enumerate([(187, 61, INK), (225, 61, TEAL), (187, 99, VIOLET), (225, 99, BLUE)]))
    return "".join(tiles) + heroes + f'<text x="528" y="196" text-anchor="end" class="mono" font-size="12" fill="{c}">CO-OP · 2–4 PLAYERS</text>'


PROJECTS = [
    ("aciliszili", 1, "Açılış", " Zili", "FINANCE · DAILY", "#4ade80", motif_chart,
     ["US markets, tracked in Turkish: earnings calendar,", "analyses, macro data and a daily bulletin."],
     ["Next.js 16", "Postgres", "AI agents"]),
    ("digynotes", 2, "Digy", "Notes", "PRODUCTIVITY", "#fbbf24", motif_notes,
     ["A personal log for films, books, games and places —", "ratings, tags, collections and a social feed."],
     ["Next.js", "Prisma", "Neon"]),
    ("derinay", 3, "Derin", "ay", "HEALTH · CLINIC", VIOLET, motif_calm,
     ["A calm panel for a one-person clinical practice:", "clients, sessions, invoices, payments and tax."],
     ["Next.js", "TypeScript", "Postgres"]),
    ("elevenforge", 4, "Eleven", "Forge", "GAME · MANAGER", "#a3e635", motif_pitch,
     ["Multiplayer online football manager in Turkish —", "16 friends, one league, matches simulated daily."],
     ["Next.js", "TypeScript", "Cron"]),
    ("onepiece", 5, "One Piece", " Hub", "CONTENT · WIKI", "#fb7185", motif_waves,
     ["A spoiler-safe Turkish wiki: filler-free arcs,", "character encyclopedia and watch tracking."],
     ["Next.js", "Drizzle", "Motion"]),
    ("dungeon", 6, "Dungeon", " Mates", "GAME · REALTIME", "#fb923c", motif_dungeon,
     ["A co-op dungeon crawler I built to play with", "friends — real-time, right in the browser."],
     ["Next.js", "Socket.io", "Motion"]),
]


def project_card(slug, idx, a, b, kind, c, motif, desc, tags):
    W, H = 600, 470
    css = f"""
.trace{{animation:trace 4.5s {EXPO_IN_OUT} infinite}}
@keyframes trace{{0%{{stroke-dashoffset:1}}55%,85%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:-1}}}}
.bob{{transform-box:fill-box;transform-origin:50% 100%;animation:bob 2.2s ease-in-out infinite alternate}}
@keyframes bob{{to{{transform:scaleY(.55)}}}}
.float{{animation:float 3.6s ease-in-out infinite alternate}}
@keyframes float{{to{{transform:translateY(-10px)}}}}
.twinkle{{transform-box:fill-box;transform-origin:center;animation:twinkle 2.5s ease-in-out infinite}}
@keyframes twinkle{{50%{{transform:scale(.6);opacity:.4}}}}
.breathe{{transform-box:fill-box;transform-origin:center;animation:breathe 5s ease-in-out infinite}}
@keyframes breathe{{50%{{transform:scale(1.18);stroke-opacity:.1}}}}
.wave{{animation:wave 6s linear infinite}}
@keyframes wave{{to{{transform:translateX(-200px)}}}}
.torch{{animation:torch 1.8s steps(3) infinite alternate}}
@keyframes torch{{to{{opacity:.45}}}}
.hop{{animation:hop 1.2s cubic-bezier(.5,0,.5,1) infinite alternate}}
@keyframes hop{{to{{transform:translateY(-6px)}}}}
.arrow{{animation:arrow 2.6s {EXPO_IN_OUT} infinite}}
@keyframes arrow{{0%,40%{{transform:translate(0,0)}}50%{{transform:translate(18px,-18px)}}50.01%{{transform:translate(-18px,18px)}}60%,100%{{transform:translate(0,0)}}}}
"""
    defs = f"""
<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c}" stop-opacity=".5"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient>
<radialGradient id="glow" cx=".5" cy=".3" r=".7"><stop offset="0" stop-color="{c}" stop-opacity=".22"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>
<linearGradient id="border" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">
  <stop offset="0" stop-color="{c}" stop-opacity="0"/><stop offset=".5" stop-color="{c}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="-700 0;700 0" dur="5s" begin="{idx * .6:.1f}s" repeatCount="indefinite"/>
</linearGradient>
<clipPath id="stage"><rect x="24" y="64" width="552" height="224" rx="16"/></clipPath>
"""
    tag_svg = []
    tx = 32
    for i, t in enumerate(tags):
        w = 26 + len(t) * 7.8
        tag_svg.append(f'<g class="fade-up" {d(.75 + i * .07)}><rect x="{tx:.1f}" y="414" width="{w:.1f}" height="30" rx="15" fill="none" stroke="{INK}" stroke-opacity=".2"/>'
                       f'<text x="{tx + w / 2:.1f}" y="434" text-anchor="middle" class="mono" font-size="11" letter-spacing=".04em" fill="{INK}">{escape(t)}</text></g>')
        tx += w + 8
    body = f"""
<rect width="{W}" height="{H}" fill="url(#glow)"/>
{masked("k1", 0, 18, 300, 40, f'<text x="32" y="44" class="mono" font-size="12" fill="{c}">({idx:02d})</text>', delay=.1)}
{masked("k2", 300, 18, 300, 40, f'<text x="{W - 32}" y="44" text-anchor="end" class="mono" font-size="12" fill="{MUTED}">{kind}</text>', delay=.16)}
<g clip-path="url(#stage)" class="fade" {d(.25)}>
  <rect x="24" y="64" width="552" height="224" fill="{BG}" fill-opacity=".6"/>
  <g transform="translate(0 82)">{motif(c)}</g>
</g>
<rect x="24.5" y="64.5" width="551" height="223" rx="16" fill="none" stroke="{INK}" stroke-opacity=".08"/>
{masked("t", 0, 296, W, 64, f'<text x="30" y="344" class="sans" font-size="46" font-weight="600" letter-spacing="-.03em" fill="{INK}">{escape(a)}<tspan class="serif" font-weight="400" fill="{c}">{escape(b)}</tspan></text>', delay=.35)}
{masked("d0", 0, 356, W, 26, f'<text x="32" y="375" class="sans" font-size="18" fill="{MUTED}">{escape(desc[0])}</text>', delay=.5)}
{masked("d1", 0, 380, W, 26, f'<text x="32" y="399" class="sans" font-size="18" fill="{MUTED}">{escape(desc[1])}</text>', delay=.56)}
{"".join(tag_svg)}
<g transform="translate({W - 54} 428)">
  <g class="pop" {d(.85)}>
    <circle r="24" fill="{c}"/>
    <clipPath id="ac"><circle r="24"/></clipPath>
    <g clip-path="url(#ac)"><g class="arrow" style="animation-delay:{1.5 + idx * .3:.1f}s"><path d="M-7 7 L7 -7 M-4 -7 H7 V4" stroke="{BG}" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g></g>
  </g>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="27" fill="none" stroke="url(#border)" stroke-width="1.5" opacity=".7"/>
"""
    write(f"project-{slug}.svg", svg(W, H, body, css, defs, title=f"{a}{b} — {' '.join(desc)} ({', '.join(tags)})"))


# ================================================================== NPM ===
def motif_theme(c):
    sw = [BG, SURFACE, BLUE, VIOLET, TEAL]
    out = []
    for i, col in enumerate(sw):
        out.append(f'<g transform="translate({400 + (i % 3) * 56} {92 + (i // 3) * 56})"><g class="pop" {d(.5 + i * .08)}>'
                   f'<rect x="-22" y="-22" width="44" height="44" rx="12" fill="{col}" stroke="{INK}" stroke-opacity=".15" class="float" style="animation-delay:{i * .4:.1f}s"/></g></g>')
    out.append(f'<text x="512" y="152" class="mono" font-size="10" fill="{MUTED}" letter-spacing=".08em">TOKENS</text>')
    return "".join(out)


def motif_ui(c):
    return f"""<g class="fade" {d(.5)}>
<rect x="388" y="72" width="176" height="96" rx="18" fill="{INK}" fill-opacity=".05" stroke="{INK}" stroke-opacity=".14"/>
<circle cx="476" cy="120" r="70" fill="url(#spot)" class="roam"/>
<rect x="404" y="88" width="72" height="24" rx="12" fill="{c}" fill-opacity=".15" stroke="{c}" stroke-opacity=".5"/>
<text x="440" y="104" text-anchor="middle" class="mono" font-size="10" fill="{c}" letter-spacing=".06em">CHIP</text>
<rect x="404" y="124" width="120" height="6" rx="3" fill="{INK}" opacity=".2"/><rect x="404" y="138" width="84" height="6" rx="3" fill="{INK}" opacity=".12"/>
<g class="roam"><path d="M470 112 L470 134 L476 128 L482 140 L486 138 L480 126 L488 126 Z" fill="{INK}"/></g>
</g>"""


PACKAGES = [
    ("theme", "Design tokens &amp; a Tailwind preset built on", "the ahmetakyapi.com visual language.", motif_theme),
    ("ui", "React components — glass, chip, cursor,", "spotlight. Built on Framer Motion.", motif_ui),
]


def npm_card(i, name, l1, l2, motif):
    W, H = 600, 320
    cmd = f"npm i @ahmetakyapi/{name}"
    cw = 8.4
    tw = len(cmd) * cw
    t0 = 1.2 + i * .3
    css = f"""
.type{{transform-box:view-box;transform-origin:0 0;animation:type {len(cmd) * .055:.2f}s steps({len(cmd)}) both}}
@keyframes type{{from{{transform:scaleX(0)}}}}
.caret{{animation:caret {len(cmd) * .055:.2f}s steps({len(cmd)}) both}}
@keyframes caret{{from{{transform:translateX(-{tw:.1f}px)}}}}
.float{{animation:float 3.6s ease-in-out infinite alternate}}
@keyframes float{{to{{transform:translateY(-6px)}}}}
.roam{{animation:roam 6s ease-in-out infinite alternate}}
@keyframes roam{{0%{{transform:translate(-50px,-14px)}}50%{{transform:translate(30px,10px)}}100%{{transform:translate(60px,-8px)}}}}
"""
    defs = f"""<radialGradient id="spot"><stop offset="0" stop-color="{TEAL}" stop-opacity=".35"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></radialGradient>
<clipPath id="typed"><rect x="56" y="252" width="{tw:.1f}" height="28" class="type" style="animation-delay:{t0:.2f}s;transform-origin:56px 0"/></clipPath>"""
    body = f"""
{masked("k1", 0, 18, 300, 40, f'<text x="32" y="44" class="mono" font-size="12" fill="#ff5f6d">(NPM)</text>', delay=.1)}
{masked("k2", 300, 18, 300, 40, f'<text x="{W - 32}" y="44" text-anchor="end" class="mono" font-size="12" fill="{MUTED}">OPEN SOURCE · v2.1.0</text>', delay=.16)}
{masked("n1", 0, 76, 380, 30, f'<text x="32" y="98" class="mono" font-size="15" fill="{MUTED}">@AHMETAKYAPI/</text>', delay=.25)}
{masked("n2", 0, 104, 380, 92, f'<text x="28" y="176" class="serif" font-size="84" fill="{INK}">{name}</text>', cls="rise-xl", delay=.32)}
{motif(TEAL)}
{masked("d0", 0, 192, W, 26, f'<text x="32" y="211" class="sans" font-size="18" fill="{MUTED}">{l1}</text>', delay=.5)}
{masked("d1", 0, 216, W, 26, f'<text x="32" y="235" class="sans" font-size="18" fill="{MUTED}">{l2}</text>', delay=.56)}
<g class="fade-up" {d(.8)}>
  <rect x="24" y="250" width="{W - 48}" height="44" rx="12" fill="{BG}" stroke="{INK}" stroke-opacity=".1"/>
  <text x="40" y="277" class="mono" font-size="14" letter-spacing="0" fill="{TEAL}">$</text>
  <g clip-path="url(#typed)"><text x="56" y="277" class="mono" font-size="14" letter-spacing="0" fill="{INK}" textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{cmd}</text></g>
  <g class="caret" style="animation-delay:{t0:.2f}s"><rect x="{56 + tw + 2:.1f}" y="262" width="8" height="18" fill="{TEAL}" class="blink"/></g>
  <text x="{W - 40}" y="277" text-anchor="end" class="mono" font-size="11" fill="{MUTED}">↗ NPMJS.COM</text>
</g>
"""
    write(f"npm-{name}.svg", svg(W, H, body, css, defs, title=f"@ahmetakyapi/{name} on npm — {l1.replace('&amp;', '&')} {l2}"))


# ================================================================ FOOTER ===
def footer():
    W, H = 1200, 640

    def outline(x):
        return f'<text x="{x}" y="636" class="sans" font-size="200" font-weight="700" letter-spacing="-.04em" fill="none" stroke="{INK}" stroke-opacity=".22" stroke-width="1.5" textLength="1900" lengthAdjust="spacingAndGlyphs">AHMET AKYAPI — AHMET AKYAPI — </text>'

    css = """
.big-marquee{animation:bigm 40s linear infinite}
@keyframes bigm{to{transform:translateX(-1950px)}}
"""
    defs = f"""
<linearGradient id="sheen2" gradientUnits="userSpaceOnUse" x1="50" y1="0" x2="760" y2="0">
  <stop offset="0" stop-color="{TEAL}"/><stop offset=".45" stop-color="{TEAL}"/><stop offset=".55" stop-color="{INK}"/><stop offset=".65" stop-color="{TEAL}"/><stop offset="1" stop-color="{TEAL}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="-800 0;800 0;800 0" keyTimes="0;.5;1" dur="6s" begin="1.5s" repeatCount="indefinite"/>
</linearGradient>
<path id="ring2" d="M 0,-80 a 80,80 0 1,1 0,160 a 80,80 0 1,1 0,-160"/>
"""
    body = f"""
{header_row(W, 5, "CONTACT", "AN IDEA, A HALF-BUILT UI, OR JUST A QUESTION")}
{masked("l1", 0, 112, W, 150, f'<text x="48" y="236" class="sans" font-size="140" font-weight="700" letter-spacing="-.05em" fill="{INK}" textLength="760" lengthAdjust="spacingAndGlyphs">Let\'s work</text>', cls="rise-xl", delay=.15)}
{masked("l2", 0, 262, W, 160, f'<text x="50" y="388" class="serif" font-size="160" fill="url(#sheen2)" textLength="560" lengthAdjust="spacingAndGlyphs">together.</text>', cls="rise-xl", delay=.28)}
<g transform="translate(1000 270)">
  <g class="pop" {d(.6)}>
    <circle r="112" fill="{TEAL}"/>
    <g class="spin" style="animation-duration:16s"><text class="mono" font-size="13" fill="{BG}" letter-spacing=".3em"><textPath href="#ring2" textLength="500">SAY HELLO · SAY HELLO · SAY HELLO · </textPath></text></g>
    <g class="arrow-dn"><path d="M-22 22 L22 -22 M-10 -22 H22 V10" stroke="{BG}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>
  </g>
</g>
<rect x="56" y="440" width="{W - 112}" height="1" fill="{INK}" fill-opacity=".14" class="draw-x" {d(.6)}/>
{masked("e", 0, 446, W, 40, f'<text x="56" y="474" class="mono" font-size="13" fill="{INK}">AHMETAKYAPII@GMAIL.COM</text><text x="600" y="474" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">ISTANBUL · GMT+3</text><text x="{W - 56}" y="474" text-anchor="end" class="mono" font-size="13" fill="{MUTED}">©2026 AHMET AKYAPI</text>', delay=.75)}
<g class="fade" {d(.9)}><g class="big-marquee">{outline(0)}{outline(1950)}</g></g>
"""
    write("footer.svg", svg(W, H, body, css, defs, title="Let's work together — ahmetakyapii@gmail.com · Istanbul, GMT+3"))


# =============================================================== BUTTONS ===
def globe(c):
    return (f'<g fill="none" stroke="{c}" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4.2" ry="10"/>'
            f'<line x1="2" y1="12" x2="22" y2="12"/></g>')


def mail(c):
    return f'<g fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"><rect x="2" y="4.5" width="20" height="15" rx="2.5"/><path d="M3 6.5 L12 13 L21 6.5"/></g>'


def linkedin(c):
    return (f'<rect x="1" y="1" width="22" height="22" rx="4" fill="{c}"/>'
            f'<text x="12" y="17.5" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-weight="700" font-size="14" fill="{BG}">in</text>')


BUTTONS = [
    ("website", "Website", lambda c: globe(c)),
    ("email", "Email", lambda c: mail(c)),
    ("x", "X / Twitter", lambda c: f'<path d="{ICONS["x"]}" fill="{c}"/>'),
    ("linkedin", "LinkedIn", lambda c: linkedin(c)),
    ("github", "GitHub", lambda c: f'<path d="{ICONS["github"]}" fill="{c}"/>'),
]


def button(i, slug, label, ic):
    W, H = 300, 76
    css = f"""
.shine{{animation:shine 4s {EXPO_IN_OUT} infinite;animation-delay:{1 + i * .35:.2f}s}}
@keyframes shine{{0%{{transform:translateX(-160px)}}35%,100%{{transform:translateX(460px)}}}}
"""
    defs = f"""<linearGradient id="sg" x1="0" x2="1"><stop offset="0" stop-color="{INK}" stop-opacity="0"/><stop offset=".5" stop-color="{INK}" stop-opacity=".16"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient>"""
    body = f"""
<rect width="{W}" height="{H}" fill="{SURFACE}"/>
<g class="shine"><rect x="0" y="-20" width="110" height="{H + 40}" fill="url(#sg)" transform="skewX(-20)"/></g>
<g class="fade-up" {d(.1 + i * .08)}>
<g transform="translate(28 26)">{ic(INK)}</g>
<text x="72" y="45" class="sans" font-size="21" font-weight="500" fill="{INK}">{escape(label)}</text>
<g transform="translate({W - 40} 38)"><circle r="17" fill="{TEAL}"/><path d="M-5 5 L5 -5 M-3 -5 H5 V3" stroke="{BG}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>
</g>
"""
    write(f"btn-{slug}.svg", svg(W, H, body, css, defs, title=label, radius=38))


if __name__ == "__main__":
    print("Generating README assets →")
    hero()
    about()
    stack()
    experience()
    work_header()
    for p in PROJECTS:
        project_card(*p)
    for i, pk in enumerate(PACKAGES):
        npm_card(i, *pk)
    footer()
    for i, b in enumerate(BUTTONS):
        button(i, *b)
