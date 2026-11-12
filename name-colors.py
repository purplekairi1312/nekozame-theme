#!/usr/bin/env python3
"""give every color in palette.toml its real name, from its hex.

looks each one up in color-name-list (github.com/meodai/color-name-list, MIT),
picking the perceptually closest named color (CIELAB distance), and no name
twice. run it after changing a hex, then ./generate.py.
"""
import json
import math
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://cdn.jsdelivr.net/npm/color-name-list@11/dist/colornames.json"


def lab(h):
    h = h.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    r, g, b = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


named = [(n["name"], lab(n["hex"])) for n in json.load(urllib.request.urlopen(URL))]
path = os.path.join(HERE, "palette.toml")
text = open(path, encoding="utf-8").read()
used = set()


def rename(m):
    key, hexc, use = m.group(1), m.group(2), m.group(3)
    target = lab(hexc)
    for name, _ in sorted(named, key=lambda n: math.dist(target, n[1])):
        if name not in used:
            used.add(name)
            break
    return f'{key} = {{ hex = "{hexc}", name = "{name}", use = "{use}" }}'


text = re.sub(r'^(\w+)\s*=\s*\{ hex = "(#[0-9a-fA-F]{6})", name = "[^"]*", use = "([^"]*)" \}',
              rename, text, flags=re.M)
open(path, "w", encoding="utf-8").write(text)
print("named", len(used), "colors")
