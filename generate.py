#!/usr/bin/env python3
"""build every app theme in themes/ from palette.toml and templates/.

templates refer to palette roles: {{orchid}} is a hex color, {{orchid|rgb}} is
"255,192,229" (kde, konsole), {{ansi0}} ... {{ansi15}} are the terminal colors.
colors written as plain hex in a template are app-specific shades on purpose.

also draws a square for every color in assets/ and rewrites the palette table
in README.md between its <!-- palette --> markers.

usage: ./generate.py
"""
import os
import re
import shutil
import struct
import tomllib
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
pal = tomllib.load(open(os.path.join(HERE, "palette.toml"), "rb"))

colors = {}
for section in ("surface", "text", "accent"):
    colors.update({k: v["hex"] for k, v in pal[section].items()})
for i, c in enumerate(pal["ansi"]["normal"] + pal["ansi"]["bright"]):
    colors[f"ansi{i}"] = c


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def fill(m):
    name, fmt = m.group(1), m.group(2)
    if name not in colors:
        raise SystemExit(f"unknown palette role: {name}")
    c = colors[name]
    return "%d,%d,%d" % rgb(c) if fmt == "rgb" else c


out = os.path.join(HERE, "themes")
shutil.rmtree(out, ignore_errors=True)
for root, _, files in os.walk(os.path.join(HERE, "templates")):
    for f in files:
        src = os.path.join(root, f)
        dst = os.path.join(out, os.path.relpath(src, os.path.join(HERE, "templates")))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        text = open(src, encoding="utf-8").read()
        open(dst, "w", encoding="utf-8").write(re.sub(r"\{\{(\w+)(?:\|(\w+))?\}\}", fill, text))

# swatches for krita, gimp, aseprite and anything else that reads .gpl
gpl = ["GIMP Palette", "Name: nekozame", "Columns: 5", "# nekozame, purplekairi1312"]
for section in ("surface", "text", "accent"):
    for c in pal[section].values():
        gpl.append("%3d %3d %3d\t%s" % (*rgb(c["hex"]), c["name"]))
os.makedirs(os.path.join(out, "palettes"), exist_ok=True)
open(os.path.join(out, "palettes", "nekozame.gpl"), "w").write("\n".join(gpl) + "\n")


# kvantum draws qt widgets from pieces of an svg, found by id. a frame is eight
# pieces around a middle ("button-normal-topleft" ... "button-normal"), one set
# per state; indicators (check boxes, arrows, the slider knob) are one piece.
# flat, softly rounded shapes in palette colors, each on its own row.
def kvantum_svg():
    c = colors
    parts, row = [], [0]

    def place(h):
        row[0] += h + 10
        return row[0] - h - 10

    def frame(name, state, fill, border=None, f=4, juncts=False):
        oy = place(2 * f + 20)
        ox, m = 10, 20
        op = ' fill-opacity="0"' if fill is None else ""
        fill = fill or "#000000"
        cx, cy = ox + f, oy + f            # inner corner of the top left piece
        rx, by = ox + f + m, oy + f + m    # left edge of the right pieces, top of the bottom ones
        stroke = lambda d: f'<path d="{d}" fill="none" stroke="{border}" stroke-width="1"/>' if border else ""
        line = lambda x, y, w, h: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{border}"/>' if border else ""
        a = f - 0.5
        pieces = {
            "topleft": f'<path d="M{cx},{cy} L{cx},{oy} A{f},{f} 0 0 0 {ox},{cy} Z" fill="{fill}"{op}/>'
                       + stroke(f"M{cx},{oy + .5} A{a},{a} 0 0 0 {ox + .5},{cy}"),
            "topright": f'<path d="M{rx},{cy} L{rx},{oy} A{f},{f} 0 0 1 {rx + f},{cy} Z" fill="{fill}"{op}/>'
                        + stroke(f"M{rx},{oy + .5} A{a},{a} 0 0 1 {rx + f - .5},{cy}"),
            "bottomleft": f'<path d="M{cx},{by} L{ox},{by} A{f},{f} 0 0 0 {cx},{by + f} Z" fill="{fill}"{op}/>'
                          + stroke(f"M{ox + .5},{by} A{a},{a} 0 0 0 {cx},{by + f - .5}"),
            "bottomright": f'<path d="M{rx},{by} L{rx + f},{by} A{f},{f} 0 0 1 {rx},{by + f} Z" fill="{fill}"{op}/>'
                           + stroke(f"M{rx + f - .5},{by} A{a},{a} 0 0 1 {rx},{by + f - .5}"),
            "top": f'<rect x="{cx}" y="{oy}" width="{m}" height="{f}" fill="{fill}"{op}/>' + line(cx, oy, m, 1),
            "bottom": f'<rect x="{cx}" y="{by}" width="{m}" height="{f}" fill="{fill}"{op}/>' + line(cx, by + f - 1, m, 1),
            "left": f'<rect x="{ox}" y="{cy}" width="{f}" height="{m}" fill="{fill}"{op}/>' + line(ox, cy, 1, m),
            "right": f'<rect x="{rx}" y="{cy}" width="{f}" height="{m}" fill="{fill}"{op}/>' + line(rx + f - 1, cy, 1, m),
        }
        pre = f"{name}-{state}" if state else name  # the focus ring has no states
        for side, svg in pieces.items():
            parts.append(f'<g id="{pre}-{side}">{svg}</g>')
            if juncts and side in ("top", "bottom", "left", "right"):
                for j in ("leftjunct", "rightjunct"):
                    parts.append(f'<g id="{pre}-{side}-{j}">{svg}</g>')
        parts.append(f'<rect id="{pre}" x="{cx}" y="{cy}" width="{m}" height="{m}" fill="{fill}"{op}/>')

    def piece(id_, size, svg):
        """one indicator: a transparent square keeps its bounds, svg is drawn in 0..size."""
        oy = place(size)
        parts.append(f'<g id="{id_}" transform="translate(10,{oy})">'
                     f'<rect width="{size}" height="{size}" fill="#000000" fill-opacity="0"/>{svg}</g>')

    states = ("normal", "focused", "pressed", "toggled", "disabled")
    # name: (frame width, colors per state as (fill, border); missing states fall back to normal)
    frames = {
        "button": (4, {"normal": (c["raised"], None), "focused": (c["region"], None), "pressed": (c["selection"], None),
                       "toggled": (c["orchid"], None), "disabled": (c["panel"], None)}),
        "tbutton": (4, {"normal": (None, None), "focused": (c["raised"], None), "pressed": (c["selection"], None),
                        "toggled": (c["selection"], None), "disabled": (None, None)}),
        "lineedit": (3, {"normal": (c["deep"], c["raised"]), "focused": (c["deep"], c["orchid"]),
                         "disabled": (c["panel"], c["raised"])}),
        "common": (3, {"normal": (None, c["raised"]), "focused": (None, c["orchid"])}),
        "group": (3, {"normal": (None, c["raised"])}),
        "tooltip": (3, {"normal": (c["deep"], c["orchid"])}),
        "tab": (4, {"normal": (c["deep"], None), "focused": (c["raised"], None), "toggled": (c["orchid"], None),
                    "disabled": (c["deep"], None)}),
        "floating-tab": (4, {"normal": (c["deep"], None), "focused": (c["raised"], None), "toggled": (c["orchid"], None)}),
        "itemview": (3, {"normal": (None, None), "focused": (c["raised"], None), "pressed": (c["orchid"], None),
                         "toggled": (c["orchid"], None), "disabled": (None, None)}),
        "menu": (4, {"normal": (c["panel"], c["raised"])}),
        "menuitem": (3, {"normal": (None, None), "focused": (c["orchid"], None), "pressed": (c["orchid"], None),
                         "toggled": (c["orchid"], None)}),
        "menubaritem": (3, {"normal": (None, None), "focused": (c["raised"], None), "pressed": (c["orchid"], None),
                            "toggled": (c["orchid"], None)}),
        "progress": (3, {"normal": (c["deep"], None), "disabled": (c["deep"], None)}),
        "progress-pattern": (3, {"normal": (c["orchid"], None), "disabled": (c["dim"], None)}),
        "scrollbargroove": (4, {"normal": (c["deep"], None)}),
        "scrollbarslider": (4, {"normal": (c["linenum"], None), "focused": (c["pink"], None),
                                "pressed": (c["orchid"], None), "disabled": (c["raised"], None)}),
        "slider": (3, {"normal": (c["deep"], None), "focused": (c["deep"], None), "toggled": (c["orchid"], None),
                       "disabled": (c["raised"], None)}),
        "header": (1, {"normal": (c["panel"], c["deep"]), "focused": (c["raised"], c["deep"]),
                       "pressed": (c["selection"], c["deep"])}),
    }
    for name, (f, looks) in frames.items():
        for state in states:
            if state in looks:
                fill, border = looks[state]
                frame(name, state, fill, border, f, juncts=False)
    frame("tabframe", "normal", None, c["raised"], 3, juncts=True)
    frame("focus", None, None, c["orchid"], 2)  # keyboard focus
    for state, fill in (("normal", c["deep"]), ("focused", c["panel"])):
        parts.append(f'<rect id="titlebar-{state}" x="10" y="{place(20)}" width="20" height="20" fill="{fill}"/>')

    # check boxes and radio buttons: deep with a soft border, pink when on
    box = lambda fill, border: f'<rect x="1" y="1" width="14" height="14" rx="4" fill="{fill}" stroke="{border}" stroke-width="1.5"/>'
    tick = f'<path d="M4.5,8.3 L7,10.8 L11.8,5.6" fill="none" stroke="{c["deep"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    dash = f'<rect x="4" y="7" width="8" height="2" rx="1" fill="{c["deep"]}"/>'
    ring = lambda fill, border: f'<circle cx="8" cy="8" r="6.5" fill="{fill}" stroke="{border}" stroke-width="1.5"/>'
    dot = f'<circle cx="8" cy="8" r="3" fill="{c["deep"]}"/>'
    for state, off, on in (("normal", c["dim"], c["orchid"]), ("focused", c["orchid"], c["pink"]),
                           ("pressed", c["orchid"], c["orchid"]), ("disabled", c["raised"], c["dim"])):
        piece(f"checkbox-{state}", 16, box(c["deep"], off))
        piece(f"checkbox-checked-{state}", 16, box(on, on) + tick)
        piece(f"checkbox-tristate-{state}", 16, box(on, on) + dash)
        piece(f"radio-{state}", 16, ring(c["deep"], off))
        piece(f"radio-checked-{state}", 16, ring(on, on) + dot)
    # the slider knob
    for state, fill in (("normal", c["pink"]), ("focused", c["orchid"]), ("pressed", c["orchid"]),
                        ("disabled", c["dim"])):
        piece(f"slidercursor-{state}", 16, f'<circle cx="8" cy="8" r="7" fill="{fill}" stroke="{c["deep"]}" stroke-width="1.5"/>')

    # arrows: soft chevrons
    chevrons = {"down": "M2,3.5 L4.5,6 L7,3.5", "up": "M2,5.5 L4.5,3 L7,5.5",
                "left": "M5.5,2 L3,4.5 L5.5,7", "right": "M3.5,2 L6,4.5 L3.5,7"}
    for state, col in (("normal", c["fg"]), ("focused", c["pink"]), ("pressed", c["orchid"]),
                       ("toggled", c["deep"]), ("disabled", c["dim"])):
        for d, path in chevrons.items():
            piece(f"arrow-{d}-{state}", 9, f'<path d="{path}" fill="none" stroke="{col}" stroke-width="1.5" '
                                           f'stroke-linecap="round" stroke-linejoin="round"/>')
        piece(f"arrow-plus-{state}", 9, f'<path d="M4.5,1.5 V7.5 M1.5,4.5 H7.5" stroke="{col}" stroke-width="1.5" stroke-linecap="round"/>')
        piece(f"arrow-minus-{state}", 9, f'<path d="M1.5,4.5 H7.5" stroke="{col}" stroke-width="1.5" stroke-linecap="round"/>')

    # grips: a few dots
    dots = lambda col, pts: "".join(f'<circle cx="{x}" cy="{y}" r="1.2" fill="{col}"/>' for x, y in pts)
    for state, col in (("normal", c["dim"]), ("focused", c["pink"]), ("pressed", c["orchid"])):
        piece(f"splitter-grip-{state}", 16, dots(col, [(8, 4), (8, 8), (8, 12)]))
    for state, col in (("normal", c["dim"]), ("focused", c["pink"])):
        piece(f"resize-grip-{state}", 12, dots(col, [(10, 4), (10, 7), (7, 7), (10, 10), (7, 10), (4, 10)]))
    piece("toolbar-handle", 16, dots(c["dim"], [(8, 4), (8, 8), (8, 12)]))

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!-- nekozame for kvantum. drawn by generate.py from palette.toml -->\n"
            f'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="{row[0] + 10}">\n'
            + "\n".join(parts) + "\n</svg>\n")


open(os.path.join(out, "kvantum", "nekozame", "nekozame.svg"), "w").write(kvantum_svg())


def png(path, color, size=20):
    """a solid square, written with nothing but the standard library."""
    row = b"\x00" + bytes(rgb(color)) * size
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(row * size)) + chunk(b"IEND", b""))
    open(path, "wb").write(data)


# squares + the readme table. full urls, so they show on sourcehut too
RAW = "https://raw.githubusercontent.com/purplekairi1312/nekozame-theme/main/assets"
os.makedirs(os.path.join(HERE, "assets"), exist_ok=True)
rows = ["| | Name | Hex | Used for |", "|---|---|---|---|"]
for section in ("surface", "text", "accent"):
    for key, c in pal[section].items():
        png(os.path.join(HERE, "assets", f"{key}.png"), c["hex"])
        rows.append(f'| <img src="{RAW}/{key}.png" width="20" height="20" alt=""> | {c["name"]} '
                    f'| `{c["hex"]}` | {c["use"]} |')
readme = os.path.join(HERE, "README.md")
text = open(readme, encoding="utf-8").read()
text = re.sub(r"<!-- palette -->.*?<!-- /palette -->",
              "<!-- palette -->\n" + "\n".join(rows) + "\n<!-- /palette -->", text, flags=re.S)
open(readme, "w", encoding="utf-8").write(text)

print("built", sum(len(f) for _, _, f in os.walk(out)), "files in themes/")
