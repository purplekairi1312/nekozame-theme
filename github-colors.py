#!/usr/bin/env python3
"""turn github's own dark theme into nekozame, for zen's userContent.css.

github draws every colour from ~1000 css variables. this fetches its dark
theme, gives each variable a nekozame colour and writes them into
templates/zen/userContent.css between its github markers, as palette roles,
so generate.py fills them in like any other template. grays follow their
lightness from the darkest nekozame surface to the text, every other colour
becomes the nekozame pastel nearest its hue, and a few roles are set by hand:
the page, outlines and buttons darker than the page, text on pink buttons.

run it again when github adds colours, then ./generate.py.
usage: ./github-colors.py
"""
import colorsys
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "templates", "zen", "userContent.css")

page = urllib.request.urlopen("https://github.com/", timeout=30).read().decode()
url = re.search(r'https://github\.githubassets\.com/assets/dark-[0-9a-f]+\.css', page).group(0)
css = urllib.request.urlopen(url, timeout=30).read().decode()

# github's dark grays, darkest to lightest, against nekozame's
GRAYS = [(0.02, "deep"), (0.045, "panel"), (0.07, "bg"), (0.12, "raised"), (0.18, "region"),
         (0.30, "selection"), (0.45, "linenum"), (0.58, "dim"), (0.70, "comment"),
         (0.85, "muted"), (0.95, "pinktext")]
# hue (degrees) of each pastel, for the coloured ones
HUES = [(0, "error"), (25, "peach"), (50, "butter"), (95, "green"), (140, "mint"),
        (180, "cyan"), (210, "blue"), (270, "violet"), (320, "orchid"), (360, "error")]

# set by hand, before anything else
NAMED = {
    "bgColor-default": "{{bg}}", "bgColor-inset": "{{deep}}", "bgColor-muted": "{{panel}}",
    "header-bgColor": "{{panel}}", "overlay-bgColor": "{{panel}}",
    "fgColor-default": "{{pinktext}}", "fgColor-muted": "{{comment}}", "fgColor-onEmphasis": "{{deep}}",
    "fgColor-accent": "{{blue}}", "fgColor-link": "{{blue}}",
    "underlineNav-borderColor-active": "{{orchid}}",
    "button-default-bgColor-rest": "{{panel}}", "button-default-bgColor-hover": "{{deep}}",
    "button-default-bgColor-active": "{{deep}}", "button-default-bgColor-selected": "{{deep}}",
    "button-primary-bgColor-rest": "{{orchid}}", "button-primary-bgColor-hover": "{{pink}}",
    "button-primary-bgColor-active": "{{pink}}", "button-primary-fgColor-rest": "{{deep}}",
    "button-primary-iconColor-rest": "{{deep}}", "button-primary-borderColor-rest": "{{orchid}}",
}


def nearest_hue(h):
    return min(HUES, key=lambda x: abs(x[0] - h))[1]


def gray(l):
    for (l0, a), (l1, b) in zip(GRAYS, GRAYS[1:]):
        if l <= l0:
            return "{{%s}}" % a
        if l < l1:
            t = round((l - l0) / (l1 - l0) * 100)
            if t < 15:
                return "{{%s}}" % a
            if t > 85:
                return "{{%s}}" % b
            return "color-mix(in srgb, {{%s}} %d%%, {{%s}})" % (b, t, a)
    return "{{%s}}" % GRAYS[-1][1]


def convert(name, value):
    if name in NAMED:
        return NAMED[name]
    m = re.fullmatch(r"#([0-9a-f]{6})([0-9a-f]{2})?", value.strip().lower())
    if not m:
        return None
    r, g, b = (int(m.group(1)[i:i + 2], 16) / 255 for i in (0, 2, 4))
    alpha = int(m.group(2), 16) / 255 if m.group(2) else 1
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    neutral = s < 0.25 or max(r, g, b) - min(r, g, b) < 0.08
    if neutral and ("borderColor" in name or name.startswith("border-")):
        out = "{{deep}}"  # outlines: darker than the page, not lighter
    elif neutral:
        out = gray(l)
    else:
        role = nearest_hue(h * 360)
        # dark shades (muted backgrounds) become the pastel sunk into the page
        # solid "emphasis" ones carry dark text, so they stay the full pastel
        out = "{{%s}}" % role if l > 0.4 or "mphasis" in name else "color-mix(in srgb, {{%s}} 35%%, {{bg}})" % role
    if alpha < 1:
        out = "color-mix(in srgb, %s %d%%, transparent)" % (out, round(alpha * 100))
    return out


seen, lines = set(), []
for name, value in re.findall(r"--([\w-]+):([^;}]+)", css):
    if name in seen:
        continue
    new = convert(name, value)
    if new:
        seen.add(name)
        lines.append(f"        --{name}: {new} !important;")

block = ("/* github */\n@-moz-document domain(\"github.com\") {\n    :root, [data-color-mode] {\n"
         "        color-scheme: dark !important;\n" + "\n".join(lines) + "\n    }\n}\n/* /github */")
text = open(TEMPLATE, encoding="utf-8").read()
text = re.sub(r"/\* github \*/.*?/\* /github \*/", lambda _: block, text, flags=re.S)
open(TEMPLATE, "w", encoding="utf-8").write(text)
print(f"{len(lines)} github colours from {url}")
