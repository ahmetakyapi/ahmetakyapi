#!/usr/bin/env python3
"""Converts the hero name into glyph outlines (scripts/glyphs.json).

Outlines render identically everywhere (no font fallback inside <img>) and let
the hero animate the name letter by letter. Only needs re-running if the name
or the fonts change:

  pip install fonttools
  python3 scripts/outline.py InterDisplay-Bold.otf InstrumentSerif-Italic.ttf
"""
import json
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

WORDS = [("Ahmet", 0), ("Akyapı", 1)]  # (text, index of the font argument)


def outline(path, text):
    font = TTFont(path)
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    upm = font["head"].unitsPerEm
    x = 0
    glyphs = []
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[name].draw(pen)
        glyphs.append({"char": ch, "x": x, "d": pen.getCommands()})
        x += hmtx[name][0]
    return {"upm": upm, "width": x, "glyphs": glyphs}


if __name__ == "__main__":
    fonts = sys.argv[1:3]
    data = {text: outline(fonts[i], text) for text, i in WORDS}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphs.json")
    json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print("wrote", out)
