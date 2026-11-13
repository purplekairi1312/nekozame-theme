#!/usr/bin/env python3
"""turn github's and youtube's own dark themes into nekozame, for zen's userContent.css.

both sites draw every colour from css variables (github ~1000, youtube ~200).
this fetches each site's dark theme, gives each variable a nekozame colour and
writes them into templates/zen/userContent.css between the site's markers, as
palette roles, so generate.py fills them in like any other template. grays
follow their lightness from the darkest nekozame surface to the text, every
other colour becomes the nekozame pastel nearest its hue, and a few roles are
set by hand: the page, outlines and buttons darker than the page, text on pink.

run it again when a site changes its colours, then ./generate.py.
usage: ./web-colors.py
"""
import colorsys
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "templates", "zen", "userContent.css")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:140.0) Gecko/20100101 Firefox/140.0",
      "Cookie": "SOCS=CAI"}  # past youtube's cookie page

# the sites' dark grays, darkest to lightest, against nekozame's
GRAYS = [(0.02, "deep"), (0.045, "panel"), (0.07, "bg"), (0.12, "raised"), (0.18, "region"),
         (0.30, "selection"), (0.45, "linenum"), (0.58, "dim"), (0.70, "comment"),
         (0.85, "muted"), (0.95, "pinktext")]
# hue (degrees) of each pastel, for the coloured ones
HUES = [(0, "error"), (25, "peach"), (50, "butter"), (95, "green"), (140, "mint"),
        (180, "cyan"), (210, "blue"), (270, "violet"), (320, "orchid"), (360, "error")]


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode("utf-8", "replace")


def github():
    url = re.search(r'https://github\.githubassets\.com/assets/dark-[0-9a-f]+\.css', get("https://github.com/")).group(0)
    return url, get(url)


def youtube():
    page = get("https://www.youtube.com/")
    url = re.search(r'https://www\.youtube\.com/s/_/ytmainappweb/_/ss/[^"]+', page).group(0).replace("&amp;", "&")
    css = get(url)
    # the newest colour set, dark
    body = re.search(r'html\[color-version=v2_0\]\[dark\]\{([^{}]*)\}', css).group(1)
    return url, body


SITES = {
    "github": dict(
        fetch=github, domain="github.com", selector=":root, [data-color-mode]", skip=(),
        named={
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
        }),
    "youtube": dict(
        fetch=youtube, domain="youtube.com", selector="html, [dark], [light]",
        # colours drawn over the video itself stay as they are
        skip=("--yt-sys-color-baseline--overlay-", "--yt-sys-color-baseline--scrim-",
              "--yt-sys-color-baseline--static-", "--yt-sys-color-baseline--keyboard-"),
        named={f"yt-sys-color-baseline--{k}": v for k, v in {
            "base-background": "{{bg}}", "raised-background": "{{panel}}", "menu-background": "{{panel}}",
            "surface-container": "{{panel}}", "solid-background-inverse": "{{bg}}",
            "frosted-glass-desktop": "{{bg}}", "frosted-glass-mobile": "{{bg}}",
            "text-primary": "{{pinktext}}", "text-secondary": "{{comment}}", "text-disabled": "{{dim}}",
            "wordmark-text": "{{pinktext}}", "text-primary-inverse": "{{deep}}",
            "inverted-background": "{{orchid}}", "inverted-background-hover": "{{pink}}",
            "mono-filled-hover": "{{pink}}", "outline-opaque": "{{deep}}",
            "call-to-action": "{{blue}}", "call-to-action-hover": "{{cyan}}",
            "static-brand-red": "{{orchid}}", "red-indicator": "{{orchid}}", "brand-red-contrast": "{{orchid}}",
        }.items()}),
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


def parse(value):
    """#rgb, #rrggbb(aa) or rgba() as r, g, b in 0-1 and alpha; None for anything else."""
    v = value.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3})", v)
    if m:
        v = "#" + "".join(c * 2 for c in m.group(1))
    m = re.fullmatch(r"#([0-9a-f]{6})([0-9a-f]{2})?", v)
    if m:
        return (*(int(m.group(1)[i:i + 2], 16) / 255 for i in (0, 2, 4)),
                int(m.group(2), 16) / 255 if m.group(2) else 1)
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)", v)
    if m:
        return (*(int(m.group(i)) / 255 for i in (1, 2, 3)), float(m.group(4) or 1))
    return None


def convert(name, value, named):
    if name in named:
        return named[name]
    c = parse(value)
    if not c:
        return None
    r, g, b, alpha = c
    if alpha == 0:
        return "transparent"
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    neutral = s < 0.25 or max(r, g, b) - min(r, g, b) < 0.08
    if neutral and ("borderColor" in name or name.startswith("border-") or "outline" in name):
        return "{{deep}}"  # outlines: solid, darker than the page, not lighter
    if neutral:
        out = gray(l)
    else:
        role = nearest_hue(h * 360)
        # dark shades (muted backgrounds) become the pastel sunk into the page;
        # solid "emphasis" ones carry dark text, so they stay the full pastel
        out = "{{%s}}" % role if l > 0.4 or "mphasis" in name else \
            "color-mix(in srgb, {{%s}} 35%%, {{bg}})" % role
    if alpha < 1:
        out = "color-mix(in srgb, %s %d%%, transparent)" % (out, round(alpha * 100))
    return out


text = open(TEMPLATE, encoding="utf-8").read()
for site, cfg in SITES.items():
    url, css = cfg["fetch"]()
    seen, lines = set(), []
    for name, value in re.findall(r"--([\w-]+):([^;}]+)", css):
        if name in seen or ("--" + name).startswith(cfg["skip"]):
            continue
        new = convert(name, value, cfg["named"])
        if new:
            seen.add(name)
            lines.append(f"        --{name}: {new} !important;")
    block = (f"/* {site} */\n@-moz-document domain(\"{cfg['domain']}\") {{\n    {cfg['selector']} {{\n"
             "        color-scheme: dark !important;\n" + "\n".join(lines) + f"\n    }}\n}}\n/* /{site} */")
    text = re.sub(rf"/\* {site} \*/.*?/\* /{site} \*/", lambda _: block, text, flags=re.S)
    print(f"{site}: {len(lines)} colours from {url[:90]}")
open(TEMPLATE, "w", encoding="utf-8").write(text)
