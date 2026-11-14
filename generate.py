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


# the plasma style (panel, popups, tooltips, the task manager, list highlights). plasma
# cuts each frame into nine named pieces like kvantum ("center", "topleft", or
# "focus-center" with a prefix); anything not drawn here comes from breeze.
def nine(prefix, oy, fill, border=None, r=8, opacity=1.0, line=1.0, border_opacity=1.0):
    """a rounded rect as plasma's nine pieces, at row oy. returns (svg, height used)."""
    m, ox = 24, 10
    p = f"{prefix}-" if prefix else ""
    fo = f' fill-opacity="{opacity}"'
    cx, cy, rx, by = ox + r, oy + r, ox + r + m, oy + r + m
    a = r - line / 2
    bo = f' stroke-opacity="{border_opacity}"'
    st = (lambda d: f'<path d="{d}" fill="none" stroke="{border}" stroke-width="{line}"{bo}/>') if border else (lambda d: "")
    ln = (lambda x, y, w, h: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{border}" fill-opacity="{border_opacity}"/>') if border else (lambda *a: "")
    h = line
    pieces = {
        "topleft": f'<path d="M{cx},{cy} L{cx},{oy} A{r},{r} 0 0 0 {ox},{cy} Z" fill="{fill}"{fo}/>' + st(f"M{cx},{oy + h/2} A{a},{a} 0 0 0 {ox + h/2},{cy}"),
        "topright": f'<path d="M{rx},{cy} L{rx},{oy} A{r},{r} 0 0 1 {rx + r},{cy} Z" fill="{fill}"{fo}/>' + st(f"M{rx},{oy + h/2} A{a},{a} 0 0 1 {rx + r - h/2},{cy}"),
        "bottomleft": f'<path d="M{cx},{by} L{ox},{by} A{r},{r} 0 0 0 {cx},{by + r} Z" fill="{fill}"{fo}/>' + st(f"M{ox + h/2},{by} A{a},{a} 0 0 0 {cx},{by + r - h/2}"),
        "bottomright": f'<path d="M{rx},{by} L{rx + r},{by} A{r},{r} 0 0 1 {rx},{by + r} Z" fill="{fill}"{fo}/>' + st(f"M{rx + r - h/2},{by} A{a},{a} 0 0 1 {rx},{by + r - h/2}"),
        "top": f'<rect x="{cx}" y="{oy}" width="{m}" height="{r}" fill="{fill}"{fo}/>' + ln(cx, oy, m, h),
        "bottom": f'<rect x="{cx}" y="{by}" width="{m}" height="{r}" fill="{fill}"{fo}/>' + ln(cx, by + r - h, m, h),
        "left": f'<rect x="{ox}" y="{cy}" width="{r}" height="{m}" fill="{fill}"{fo}/>' + ln(ox, cy, h, m),
        "right": f'<rect x="{rx}" y="{cy}" width="{r}" height="{m}" fill="{fill}"{fo}/>' + ln(rx + r - h, cy, h, m),
        "center": f'<rect x="{cx}" y="{cy}" width="{m}" height="{m}" fill="{fill}"{fo}/>',
    }
    svg = "".join(f'<g id="{p}{k}">{v}</g>' for k, v in pieces.items())
    return svg, 2 * r + m + 10


def plasma_svg(frames):
    """frames: [(prefix, fill, border, r, opacity[, border opacity])], each its own row.
    the panel also gets mask-* pieces: plasma blurs what's behind it through them."""
    parts, y = [], 10
    for prefix, fill_, border, r, opacity, *bo in frames:
        svg, hgt = nine(prefix, y, fill_, border, r, opacity, border_opacity=bo[0] if bo else 1.0)
        parts.append(svg)
        y += hgt
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!-- nekozame for plasma. drawn by generate.py from palette.toml -->\n"
            f'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="{y}">\n' + "\n".join(parts) + "\n</svg>\n")


c = colors
P = os.path.join(out, "plasma", "nekozame")
for d in ("widgets", "dialogs"):
    os.makedirs(os.path.join(P, d), exist_ok=True)
plasma = {
    # the panel: plum, softly rounded, a faint pink edge (it floats away from the screen edge)
    "widgets/panel-background.svg": [("", c["panel"], c["orchid"], 10, 0.96, 0.35),
                                     ("mask", "#000000", None, 10, 1.0)],
    # popups (menus, the app launcher, the tray's panels)
    "dialogs/background.svg": [("", c["panel"], c["raised"], 10, 0.98)],
    "widgets/tooltip.svg": [("", c["deep"], c["orchid"], 8, 0.98)],
    "widgets/background.svg": [("", c["panel"], c["raised"], 10, 0.92)],
    # the task manager: the open app glows pink, hover lilac, attention butter yellow
    "widgets/tasks.svg": [("normal", "#000000", None, 6, 0.0), ("minimized", "#000000", None, 6, 0.0),
                          ("focus", c["orchid"], c["orchid"], 6, 0.30), ("hover", c["violet"], None, 6, 0.22),
                          ("attention", c["butter"], c["butter"], 6, 0.35)],
    # highlighted rows in lists: the launcher, the tray, settings
    "widgets/viewitem.svg": [("hover", c["orchid"], None, 6, 0.25), ("selected", c["orchid"], None, 6, 0.55),
                             ("selected+hover", c["orchid"], None, 6, 0.70)],
}
for name, frames in plasma.items():
    open(os.path.join(P, name), "w").write(plasma_svg(frames))
# window decorations (kwin's aurorae): a plum title bar with round, mac-style buttons
# in the palette's pastels. a button is one svg with a piece per state; the title bar
# is nine pieces per state (active, inactive), like everything else here.
A = os.path.join(out, "aurorae", "nekozame")
os.makedirs(A, exist_ok=True)


def aurorae_button(color, glyph):
    """active/hover/pressed: the colour (hover shows the glyph); inactive and
    deactivated: a muted dot, like a mac's buttons when the window isn't focused."""
    size, rr = 16, 6.5
    states = {
        "active": (color, 1.0, ""),
        "hover": (color, 1.0, glyph),
        "pressed": (color, 0.75, glyph),
        "inactive": (c["dim"], 0.55, ""),
        "deactivated": (c["dim"], 0.35, ""),
    }
    parts = []
    for i, (state, (col, op, g)) in enumerate(states.items()):
        x = 10 + i * (size + 10)
        parts.append(f'<g id="{state}-center" transform="translate({x},10)">'
                     f'<rect width="{size}" height="{size}" fill="#000000" fill-opacity="0"/>'
                     f'<circle cx="8" cy="8" r="{rr}" fill="{col}" fill-opacity="{op}"/>{g}</g>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!-- nekozame window button. drawn by generate.py -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{10 + 5 * 26}" height="36">\n' + "\n".join(parts) + "\n</svg>\n")


ink = c["deep"]
g = lambda d: f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
buttons = {
    "close": (c["error"], g("M5.5,5.5 L10.5,10.5 M10.5,5.5 L5.5,10.5")),
    "minimize": (c["butter"], g("M5,8 H11")),
    "maximize": (c["mint"], g("M8,5 V11 M5,8 H11")),
    "restore": (c["mint"], g("M5.5,8 H10.5")),
    "alldesktops": (c["violet"], g("M6,6 h4 v4 h-4 Z")),
    "keepabove": (c["blue"], g("M5.5,9.5 L8,7 L10.5,9.5")),
    "keepbelow": (c["blue"], g("M5.5,6.5 L8,9 L10.5,6.5")),
    "shade": (c["blue"], g("M5,6.5 H11")),
    "help": (c["blue"], g("M6.3,6.3 a1.8,1.8 0 1 1 2.5,1.6 c-0.6,0.3 -0.8,0.6 -0.8,1.2 M8,11 v0.1")),
}
for name, (col, glyph) in buttons.items():
    open(os.path.join(A, f"{name}.svg"), "w").write(aurorae_button(col, glyph))

# the title bar: rounded on top, square at the bottom where the window's content
# starts. active: plum; inactive: the darker plum. pink title on the active window
deco = []
y = 10
for prefix, fill_ in (("decoration", c["panel"]), ("decoration-inactive", c["deep"])):
    svg, hgt = nine(prefix, y, fill_, None, 10, 1.0)
    # square bottom corners: plasma's bottom corner pieces become plain squares
    svg = svg.replace(f'<g id="{prefix}-bottomleft">', f'<g id="{prefix}-bottomleft-round" display="none">')
    svg = svg.replace(f'<g id="{prefix}-bottomright">', f'<g id="{prefix}-bottomright-round" display="none">')
    by = y + 10 + 24
    svg += (f'<rect id="{prefix}-bottomleft" x="10" y="{by}" width="10" height="10" fill="{fill_}"/>'
            f'<rect id="{prefix}-bottomright" x="44" y="{by}" width="10" height="10" fill="{fill_}"/>')
    deco.append(svg)
    y += hgt
open(os.path.join(A, "decoration.svg"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<!-- nekozame window frame. drawn by generate.py -->\n'
    f'<svg xmlns="http://www.w3.org/2000/svg" width="80" height="{y}">\n' + "\n".join(deco) + "\n</svg>\n")
open(os.path.join(A, "nekozamerc"), "w").write(f"""[General]
ActiveTextColor={",".join(map(str, rgb(c["orchid"])))}
InactiveTextColor={",".join(map(str, rgb(c["dim"])))}
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=150
DecorationPosition=0
UseTextShadow=false

[Layout]
BorderLeft=1
BorderRight=1
BorderBottom=1
TitleEdgeTop=6
TitleEdgeBottom=6
TitleEdgeLeft=10
TitleEdgeRight=10
TitleBorderLeft=6
TitleBorderRight=6
TitleHeight=20
ButtonWidth=16
ButtonHeight=16
ButtonSpacing=6
ButtonMarginTop=0
ExplicitButtonSpacer=10
PaddingTop=0
PaddingBottom=0
PaddingLeft=0
PaddingRight=0
""")
open(os.path.join(A, "metadata.desktop"), "w").write("""[Desktop Entry]
Name=nekozame
Comment=nekozame: a plum title bar with round, mac-style buttons in pastels
X-KDE-PluginInfo-Author=purplekairi1312
X-KDE-PluginInfo-Name=nekozame
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-License=CC-BY-NC-SA-4.0
X-KDE-PluginInfo-Website=https://github.com/purplekairi1312/nekozame-theme
X-Plasma-API=declarativeappletscript
""")

# css loader (decky) gets the same steam theme next to its theme.json
shutil.copy(os.path.join(out, "steam", "nekozame.css"), os.path.join(out, "css-loader", "nekozame", "nekozame.css"))

# the pointer: the trans flag, glossy like the bubble logo (cursors.py draws it)
import cursors  # noqa: E402
cursors.build(os.path.join(out, "cursors", "nekozame"))

# the theme's own colors (the same as kde/nekozame.colors), and what kde lists it as
shutil.copy(os.path.join(out, "kde", "nekozame.colors"), os.path.join(P, "colors"))
open(os.path.join(P, "metadata.json"), "w").write("""{
    "KPlugin": {
        "Authors": [{ "Name": "purplekairi1312" }],
        "Description": "nekozame: soft violet-gray with pastel pink",
        "Id": "nekozame",
        "License": "CC-BY-NC-SA-4.0",
        "Name": "nekozame",
        "Website": "https://github.com/purplekairi1312/nekozame-theme"
    },
    "X-Plasma-API-Minimum-Version": "6.0"
}
""")


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
