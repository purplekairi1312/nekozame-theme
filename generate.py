#!/usr/bin/env python3
"""build every app theme in themes/ from palette.toml and templates/.

templates refer to palette roles: {{orchid}} is a hex color, {{orchid|rgb}} is
"255,192,229" (kde, konsole), {{ansi0}} ... {{ansi15}} are the terminal colors.
colors written as plain hex in a template are app-specific shades on purpose.

usage: ./generate.py
"""
import os
import re
import shutil
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
pal = tomllib.load(open(os.path.join(HERE, "palette.toml"), "rb"))

colors = {}
for section in ("surface", "text", "accent"):
    colors.update(pal[section])
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
    for name, c in pal[section].items():
        gpl.append("%3d %3d %3d\t%s" % (*rgb(c), name))
os.makedirs(os.path.join(out, "palettes"), exist_ok=True)
open(os.path.join(out, "palettes", "nekozame.gpl"), "w").write("\n".join(gpl) + "\n")

print("built", sum(len(f) for _, _, f in os.walk(out)), "files in themes/")
