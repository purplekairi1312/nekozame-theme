// nekozame for steam: game mode, big picture, its menus and the desktop client.
// generated from palette.toml by generate.py; edit the palette there.
// steam colours nearly everything in its own stylesheets (not through variables),
// so this goes through them like dark reader does and swaps every colour for its
// nekozame one: greys and steam's blue-greys become the plums (by how light they
// are), steam's blue becomes pink, its greens, reds and yellows the pastels.
// pictures aren't touched. nekozame os runs it in every steam page
// (nekozame-steam-theme); it's safe to run more than once.
(function () {
  if (window.__nekozame) return;
  window.__nekozame = true;

  const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  // greys, darkest to lightest: steam's lightness (0-1) -> a nekozame shade
  const PLUMS = [
    [0.0, hex("#1f1a29")], [0.07, hex("#2a2435")], [0.12, hex("#342c40")], [0.17, hex("#433a55")],
    [0.24, hex("#4f4562")], [0.31, hex("#5a4f6e")], [0.4, hex("#685c7f")], [0.52, hex("#a094b8")],
    [0.64, hex("#b3a7cb")], [0.8, hex("#e8def5")], [0.92, hex("#f1e6ff")], [1.0, hex("#ffffff")],
  ];
  const PINK_TEXT = hex("#ffc0e5");     // blue text, lines, underlines
  const PINK_FILL = hex("#b0689b");        // blue behind white text: deep enough to read
  const PINK_DARK = hex("#5c3458");        // dark blues (pressed, shadows)
  const MINT = hex("#c8f7dc"), MINT_FILL = hex("#5f9e7c");
  const ROSE = hex("#ffc0d2"), ROSE_FILL = hex("#b05a72");
  const BUTTER = hex("#fff1b0"), PEACH = hex("#ffd2b8");

  function lerp(stops, t) {
    for (let i = 1; i < stops.length; i++) {
      if (t <= stops[i][0]) {
        const [t0, a] = stops[i - 1], [t1, b] = stops[i];
        const k = (t - t0) / (t1 - t0 || 1);
        return a.map((v, j) => Math.round(v + (b[j] - v) * k));
      }
    }
    return stops[stops.length - 1][1];
  }

  function hsl([r, g, b]) {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2;
    if (max === min) return [0, 0, l];
    const d = max - min, s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    let h = max === r ? (g - b) / d + (g < b ? 6 : 0) : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
    return [h * 60, s, l];
  }

  // one colour -> its nekozame colour. text and lines get the light pastels, fills the
  // deeper ones, so steam's white text stays readable on them
  function swap(rgb, isText) {
    const [h, s, l] = hsl(rgb);
    const blueish = h >= 185 && h <= 240;
    if (s < 0.12 || (blueish && s < 0.5 && l < 0.45) || (blueish && l > 0.82)) return lerp(PLUMS, l);
    if (blueish) return isText ? PINK_TEXT : l < 0.3 ? PINK_DARK : PINK_FILL;
    if (h >= 85 && h < 165) return isText ? MINT : MINT_FILL;
    if (h < 20 || h >= 330) return isText ? ROSE : ROSE_FILL;
    if (h >= 40 && h < 70) return BUTTER;
    if (h >= 20 && h < 40) return PEACH;
    return rgb;
  }

  const COLOR = /#(?:[0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4})\b|rgba?\([^)]*\)/gi;

  function parse(tok) {
    if (tok[0] === "#") {
      let h = tok.slice(1);
      if (h.length <= 4) h = h.split("").map((c) => c + c).join("");
      const v = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
      return [v, h.length === 8 ? parseInt(h.slice(6, 8), 16) / 255 : 1];
    }
    const n = tok.slice(tok.indexOf("(") + 1, -1).split(/[\s,/]+/).filter(Boolean).map(parseFloat);
    if (n.length < 3 || n.some(isNaN)) return null;
    return [n.slice(0, 3), n.length > 3 ? n[3] : 1];
  }

  function swapValue(value, isText) {
    return value.replace(COLOR, (tok) => {
      const p = parse(tok);
      if (!p) return tok;
      const [rgb, a] = p;
      const out = swap(rgb, isText);
      return a < 1 ? `rgba(${out.join(", ")}, ${a})` : `rgb(${out.join(", ")})`;
    });
  }

  const TEXTY = /^(color|border|outline|text-decoration|caret|fill|stroke|--.*(text|fg|foreground|border|accent))/i;

  function doRules(rules) {
    for (const rule of rules) {
      if (rule.cssRules && !rule.style) { doRules(rule.cssRules); continue; }
      const st = rule.style;
      if (!st) continue;
      for (let i = 0; i < st.length; i++) {
        const prop = st[i], val = st.getPropertyValue(prop);
        if (!val || !COLOR.test(val)) { COLOR.lastIndex = 0; continue; }
        COLOR.lastIndex = 0;
        const out = swapValue(val, TEXTY.test(prop));
        if (out !== val) st.setProperty(prop, out, st.getPropertyPriority(prop));
      }
    }
  }

  // stylesheets from another address (the store's come from steam's cdn) can't be
  // read from here: fetch their text, swap the colours in it, put that copy in the page
  // and switch the original off. relative urls in them are made absolute first
  function swapText(css, base) {
    css = css.replace(/url\(\s*(['"]?)([^'")]+)\1\s*\)/g, (m, q, u) => {
      try { return `url("${new URL(u, base).href}")`; } catch (e) { return m; }
    });
    return css.replace(/([\w-]+)(\s*:\s*)([^;{}]+)/g, (m, prop, sep, val) =>
      COLOR.test(val) ? (COLOR.lastIndex = 0, prop + sep + swapValue(val, TEXTY.test(prop))) : (COLOR.lastIndex = 0, m));
  }
  const fetching = new Set();
  function copyOf(sheet) {
    const href = sheet.href;
    if (!href || fetching.has(href) || !sheet.ownerNode) return;
    fetching.add(href);
    fetch(href).then((r) => r.text()).then((css) => {
      const style = document.createElement("style");
      style.dataset.nekozame = href;
      style.textContent = swapText(css, href);
      sheet.ownerNode.after(style);
      sheet.disabled = true;
    }).catch(() => {});
  }

  const done = new WeakSet();
  function sweep() {
    for (const sheet of document.styleSheets) {
      if (done.has(sheet)) continue;
      try { doRules(sheet.cssRules); done.add(sheet); } catch (e) { copyOf(sheet); }
    }
  }
  sweep();
  new MutationObserver(sweep).observe(document.documentElement, { childList: true, subtree: true });
  setInterval(sweep, 3000);  // stylesheets that finish loading later
})();
