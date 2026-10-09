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
GLYPHS = json.load(open(os.path.join(os.path.dirname(__file__), "glyphs.json"), encoding="utf-8"))

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


def word(text, x, baseline, width, delay, tracking=0.0, stagger=.07, fill=INK, animate=True):
    """Outlined word (see outline.py), uniformly scaled to `width`.

    Each glyph first draws its outline, then fills in, staggered left to right.
    """
    g = GLYPHS[text]
    upm = g["upm"]
    n = len(g["glyphs"])
    track = tracking * upm
    scale = width / (g["width"] + track * (n - 1))
    out = []
    for i, gl in enumerate(g["glyphs"]):
        gx = x + (gl["x"] + track * i) * scale
        tf = f'translate({gx:.1f} {baseline}) scale({scale:.5f} {-scale:.5f})'
        if animate:
            t = delay + i * stagger
            out.append(f'<path class="ink" transform="{tf}" d="{gl["d"]}" fill="{fill}" stroke="{fill}" stroke-width="1.2" '
                       f'vector-effect="non-scaling-stroke" pathLength="1" style="animation-delay:{t:.3f}s,{t + .75:.3f}s"/>')
        else:
            out.append(f'<path transform="{tf}" d="{gl["d"]}" fill="{fill}"/>')
    return "".join(out), scale


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  assets/{name:<22} {len(content.encode()) / 1024:6.1f} KB")


# ================================================================== HERO ===
def hero():
    W, H = 1200, 700
    REVEAL = .35        # hero content starts

    first, _ = word("Ahmet", 48, 300, 640, REVEAL, tracking=-.035)
    last, _ = word("Akyapı", 372, 540, 720, REVEAL + .45)
    last_mask, _ = word("Akyapı", 372, 540, 720, 0, fill="#fff", animate=False)

    css = f"""
.ink{{stroke-dasharray:1;animation:ink-draw 1.6s {EXPO_IN_OUT} both,ink-fill 1.1s ease both}}
@keyframes ink-draw{{from{{stroke-dashoffset:1}}}}
@keyframes ink-fill{{from{{fill-opacity:0}}}}
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
<linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="300" y1="0" x2="1100" y2="0" gradientTransform="translate(-900 0)">
  <stop offset="0" stop-color="{TEAL}" stop-opacity="0"/><stop offset=".4" stop-color="{TEAL}" stop-opacity="0"/>
  <stop offset=".47" stop-color="{VIOLET}" stop-opacity=".9"/><stop offset=".53" stop-color="{TEAL}" stop-opacity=".9"/>
  <stop offset=".6" stop-color="{TEAL}" stop-opacity="0"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="-900 0;900 0;900 0" keyTimes="0;.55;1" dur="7s" begin="{REVEAL + 1.6}s" repeatCount="indefinite"/>
</linearGradient>
<mask id="lastmask"><g>{last_mask}</g></mask>
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
<g filter="url(#blur)" class="fade" {d(0)}>
  <circle class="blob b1" cx="980" cy="520" r="250" fill="#1d4ed8" opacity=".55"/>
  <circle class="blob b2" cx="220" cy="140" r="210" fill="#5b42d6" opacity=".5"/>
  <circle class="blob b3" cx="720" cy="360" r="140" fill="#2f7a6d" opacity=".55"/>
</g>
{grid}

{masked("m1", 0, 40, 400, 40, f'<text x="56" y="68" class="mono" font-size="13" fill="{MUTED}">AHMET AKYAPI <tspan fill="{TEAL}">©2026</tspan></text>', delay=REVEAL)}
{masked("m2", 400, 40, 400, 40, f'<text x="600" y="68" text-anchor="middle" class="mono" font-size="13" fill="{MUTED}">İSTANBUL · TÜRKİYE</text>', delay=REVEAL + .08)}
{masked("m3", 800, 40, 400, 40, f'<text x="{W - 80}" y="68" text-anchor="end" class="mono" font-size="13" fill="{INK}">BUILDING WITH AI AGENTS</text>', delay=REVEAL + .16)}
<g class="pop" {d(REVEAL + .4)}><circle cx="{W - 62}" cy="63" r="5" fill="{TEAL}"/></g>
<circle class="pulse" cx="{W - 62}" cy="63" r="5" fill="{TEAL}"/>
<rect x="56" y="92" width="{W - 112}" height="1" fill="{INK}" fill-opacity=".14" class="draw-x" {d(REVEAL)}/>

<g>{first}</g>
<g>{last}
  <rect x="300" y="318" width="900" height="302" fill="url(#sheen)" mask="url(#lastmask)"/>
</g>
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

"""
    write("hero.svg", svg(W, H, body, css, defs,
                          "Ahmet Akyapı — Full-Stack & AI Developer, Istanbul. Currently AI Developer at Nar Sistem Teknoloji."))


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
    ("x", "X", lambda c: f'<path d="{ICONS["x"]}" fill="{c}"/>'),
    ("linkedin", "LinkedIn", lambda c: linkedin(c)),
    ("github", "GitHub", lambda c: f'<path d="{ICONS["github"]}" fill="{c}"/>'),
    ("npm", "npm", lambda c: f'<path d="{ICONS["npm"]}" fill="{c}"/>'),
]


def button(i, slug, label, ic):
    W, H = 200, 76
    css = f"""
.shine{{animation:shine 4s {EXPO_IN_OUT} infinite;animation-delay:{1 + i * .35:.2f}s}}
@keyframes shine{{0%{{transform:translateX(-160px)}}35%,100%{{transform:translateX(360px)}}}}
"""
    defs = f"""<linearGradient id="sg" x1="0" x2="1"><stop offset="0" stop-color="{INK}" stop-opacity="0"/><stop offset=".5" stop-color="{INK}" stop-opacity=".16"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient>"""
    body = f"""
<rect width="{W}" height="{H}" fill="{SURFACE}"/>
<g class="shine"><rect x="0" y="-20" width="110" height="{H + 40}" fill="url(#sg)" transform="skewX(-20)"/></g>
<g class="fade-up" {d(.1 + i * .08)}>
<g transform="translate(28 26)">{ic(INK)}</g>
<text x="72" y="45" class="sans" font-size="21" font-weight="500" fill="{INK}">{escape(label)}</text>
</g>
"""
    write(f"btn-{slug}.svg", svg(W, H, body, css, defs, title=label, radius=38))


if __name__ == "__main__":
    print("Generating README assets →")
    hero()
    for i, b in enumerate(BUTTONS):
        button(i, *b)
