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
