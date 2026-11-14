"""nekozame's pointer: the trans flag in a glossy bubble style, like the logo.

drawn here with nothing but the standard library (shapes on a 32-unit grid, sampled
4x4 per pixel), at several sizes, and written as xcursor files with their alias
links. generate.py calls build(); the result goes in themes/cursors/nekozame/.
"""
import math
import os
import struct

TRANS = ["#5bcefa", "#f5a9b8", "#ffffff", "#f5a9b8", "#5bcefa"]   # the trans flag
SIZES = (24, 32, 48, 64, 96)
SS = 4                                                           # samples per pixel, each way


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# --- shapes on the 32-unit grid --------------------------------------------------

def poly_inside(pts, x, y):
    inside, j = False, len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


class Poly:
    def __init__(self, *pts):
        self.pts = pts
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        self.box = (min(xs), min(ys), max(xs), max(ys))

    def inside(self, x, y):
        return poly_inside(self.pts, x, y)

    def dist(self, x, y):  # distance to the edge
        p = self.pts
        return min(seg_dist(x, y, *p[i], *p[(i + 1) % len(p)]) for i in range(len(p)))


class Circle:
    def __init__(self, cx, cy, r):
        self.c, self.r = (cx, cy), r
        self.box = (cx - r, cy - r, cx + r, cy + r)

    def inside(self, x, y):
        return math.hypot(x - self.c[0], y - self.c[1]) <= self.r

    def dist(self, x, y):
        return abs(math.hypot(x - self.c[0], y - self.c[1]) - self.r)


class Union:
    def __init__(self, *shapes):
        self.shapes = shapes
        bs = [s.box for s in shapes]
        self.box = (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))

    def inside(self, x, y):
        return any(s.inside(x, y) for s in self.shapes)

    def dist(self, x, y):
        # distance to the union's outline: only edges that aren't inside another shape
        best = 99.0
        for s in self.shapes:
            d = s.dist(x, y)
            if d < best and not any(o is not s and o.inside(x, y) for o in self.shapes):
                best = d
        return best


def moved(shape, dx, dy):
    if isinstance(shape, Poly):
        return Poly(*[(x + dx, y + dy) for x, y in shape.pts])
    if isinstance(shape, Circle):
        return Circle(shape.c[0] + dx, shape.c[1] + dy, shape.r)
    return Union(*[moved(s, dx, dy) for s in shape.shapes])


def rotated(shape, deg, cx=16, cy=16):
    a = math.radians(deg)
    rot = lambda x, y: (cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a),
                        cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a))
    if isinstance(shape, Poly):
        return Poly(*[rot(x, y) for x, y in shape.pts])
    if isinstance(shape, Circle):
        return Circle(*rot(*shape.c), shape.r)
    return Union(*[rotated(s, deg, cx, cy) for s in shape.shapes])


# --- painting --------------------------------------------------------------------

def stripes(box, y):
    """the trans flag across a shape, top to bottom."""
    t = (y - box[1]) / max(box[3] - box[1], 1e-6)
    return hexc(TRANS[min(int(t * 5), 4)])


class Layer:
    """a shape, filled with the flag (or a colour), outlined, with a gloss."""
    def __init__(self, shape, fill="flag", outline="#433a55", width=1.4, gloss=True):
        self.shape, self.fill, self.outline, self.width, self.gloss = shape, fill, outline, width, gloss

    def sample(self, x, y):
        s = self.shape
        ins, d = s.inside(x, y), s.dist(x, y)
        if not ins and d > self.width:
            return None
        if self.outline and d <= self.width:
            return hexc(self.outline) + (255,)
        if not ins:
            return None
        col = stripes(s.box, y) if self.fill == "flag" else hexc(self.fill)
        if self.gloss:  # a soft highlight near the top left, like the bubble
            bx0, by0, bx1, by1 = s.box
            gx, gy = bx0 + (bx1 - bx0) * 0.32, by0 + (by1 - by0) * 0.22
            g = max(0.0, 1 - math.hypot((x - gx) / ((bx1 - bx0) * 0.38 + 1e-6), (y - gy) / ((by1 - by0) * 0.26 + 1e-6)))
            k = 0.45 * g * g
            col = tuple(int(c + (255 - c) * k) for c in col)
        return col + (255,)


def render(layers, size, shadow=True):
    """layers drawn bottom to top on a size x size image (premultiplied argb rows)."""
    scale = 32 / size
    px = []
    sh = [moved(l.shape, 0.7, 1.1) for l in layers] if shadow else []
    for j in range(size):
        row = []
        for i in range(size):
            acc = [0.0, 0.0, 0.0, 0.0]
            for sj in range(SS):
                for si in range(SS):
                    x = (i + (si + 0.5) / SS) * scale
                    y = (j + (sj + 0.5) / SS) * scale
                    c = None
                    for l in reversed(layers):
                        c = l.sample(x, y)
                        if c:
                            break
                    if c is None and shadow and any(s.inside(x, y) or s.dist(x, y) <= 1.6 for s in sh):
                        c = (0, 0, 0, 70)
                    if c:
                        a = c[3] / 255
                        acc[0] += c[0] * a
                        acc[1] += c[1] * a
                        acc[2] += c[2] * a
                        acc[3] += a
            n = SS * SS
            row.append(tuple(int(v / n + 0.5) for v in acc[:3]) + (int(acc[3] / n * 255 + 0.5),))
        px.append(row)
    return px


def xcursor(images):
    """images: [(nominal size, w, h, xhot, yhot, delay ms, rows of premultiplied rgba)]."""
    ntoc = len(images)
    header = struct.pack("<4sIII", b"Xcur", 16, 0x10000, ntoc)
    pos = 16 + ntoc * 12
    toc, chunks = b"", b""
    for size, w, h, xh, yh, delay, rows in images:
        toc += struct.pack("<III", 0xFFFD0002, size, pos)
        body = struct.pack("<IIIIIIIII", 36, 0xFFFD0002, size, 1, w, h, xh, yh, delay)
        body += b"".join(struct.pack("<I", (a << 24) | (r << 16) | (g << 8) | b) for row in rows for r, g, b, a in row)
        chunks += body
        pos += len(body)
    return header + toc + chunks


# --- the cursors -------------------------------------------------------------------

ARROW = Poly((3, 2), (3, 24), (8.5, 19), (12, 27.5), (15.5, 26), (12, 17.5), (19, 17.5))
BUBBLE = Circle(16, 16, 8.5)


def spinner_layers(frame, cx=16, cy=16, r=8, dot=2.4, frames=8):
    """a ring of dots in the flag's colours; one bright dot goes round."""
    out = []
    for k in range(frames):
        a = 2 * math.pi * k / frames - math.pi / 2
        bright = (k - frame) % frames
        size = dot * (1.0 if bright == 0 else 0.85 if bright in (1, frames - 1) else 0.65)
        out.append(Layer(Circle(cx + r * math.cos(a), cy + r * math.sin(a), size),
                         fill=TRANS[k % 5] if TRANS[k % 5] != "#ffffff" else "#f5a9b8", width=0.9, gloss=False))
    return out


def double_arrow(horizontal=True, head=6.0, bar=2.0, tip=4.0):
    """a two-headed arrow across the grid; head: half the arrowhead's width."""
    hl = tip + head  # where the head meets the bar
    p = Poly((tip, 16), (hl, 16 - head), (hl, 16 - bar), (32 - hl, 16 - bar), (32 - hl, 16 - head), (32 - tip, 16),
             (32 - hl, 16 + head), (32 - hl, 16 + bar), (hl, 16 + bar), (hl, 16 + head))
    return p if horizontal else rotated(p, 90)


def four_way():
    h = double_arrow(True, head=4.2, bar=1.6, tip=3.5)
    return Union(h, rotated(h, 90))


CURSORS = {
    # name: (layers per frame, hotspot on the 32 grid, frame delay ms)
    "default": ([[Layer(ARROW)]], (3, 2), 0),
    "pointer": ([[Layer(BUBBLE), Layer(Circle(12.5, 12.5, 2.0), fill="#ffffff", outline=None, gloss=False)]], (16, 16), 0),
    "text": ([[Layer(Union(Poly((14.5, 6), (17.5, 6), (17.5, 26), (14.5, 26)), Poly((11, 4), (21, 4), (21, 7), (11, 7)),
                           Poly((11, 25), (21, 25), (21, 28), (11, 28))), width=1.1)]], (16, 16), 0),
    "crosshair": ([[Layer(Union(Poly((15, 4), (17, 4), (17, 13), (15, 13)), Poly((15, 19), (17, 19), (17, 28), (15, 28)),
                                Poly((4, 15), (13, 15), (13, 17), (4, 17)), Poly((19, 15), (28, 15), (28, 17), (19, 17))),
                          fill="#ffffff", width=1.0, gloss=False)]], (16, 16), 0),
    "not-allowed": ([[Layer(BUBBLE, fill="#ffb3c8"),
                      Layer(rotated(Poly((7.5, 14.6), (24.5, 14.6), (24.5, 17.4), (7.5, 17.4)), 45), fill="#433a55",
                            outline=None, gloss=False)]], (16, 16), 0),
    "move": ([[Layer(four_way(), width=1.1)]], (16, 16), 0),
    "ew-resize": ([[Layer(double_arrow(True), width=1.1)]], (16, 16), 0),
    "ns-resize": ([[Layer(double_arrow(False), width=1.1)]], (16, 16), 0),
    "nwse-resize": ([[Layer(rotated(double_arrow(True), 45), width=1.1)]], (16, 16), 0),
    "nesw-resize": ([[Layer(rotated(double_arrow(True), -45), width=1.1)]], (16, 16), 0),
    "wait": ([spinner_layers(f) for f in range(8)], (16, 16), 70),
    "progress": ([[Layer(ARROW)] + spinner_layers(f, cx=23, cy=23, r=5, dot=1.6) for f in range(8)], (3, 2), 70),
    "help": ([[Layer(ARROW), Layer(Circle(23, 22, 5.5), fill="#5bcefa"),
               Layer(Circle(23, 24.8, 1.0), fill="#433a55", outline=None, gloss=False)]], (3, 2), 0),
    "copy": ([[Layer(ARROW), Layer(Circle(23, 23, 5), fill="#c8f7dc"),
               Layer(Union(Poly((22.2, 20), (23.8, 20), (23.8, 26), (22.2, 26)), Poly((20, 22.2), (26, 22.2), (26, 23.8), (20, 23.8))),
                     fill="#433a55", outline=None, gloss=False)]], (3, 2), 0),
    "zoom-in": ([[Layer(Circle(14, 14, 8)), Layer(Poly((19, 21), (21, 19), (28, 26), (26, 28)), fill="#433a55", outline=None, gloss=False),
                  Layer(Union(Poly((13.2, 10), (14.8, 10), (14.8, 18), (13.2, 18)), Poly((10, 13.2), (18, 13.2), (18, 14.8), (10, 14.8))),
                        fill="#433a55", outline=None, gloss=False)]], (14, 14), 0),
    "zoom-out": ([[Layer(Circle(14, 14, 8)), Layer(Poly((19, 21), (21, 19), (28, 26), (26, 28)), fill="#433a55", outline=None, gloss=False),
                   Layer(Poly((10, 13.2), (18, 13.2), (18, 14.8), (10, 14.8)), fill="#433a55", outline=None, gloss=False)]], (14, 14), 0),
}

# every other name apps ask for, and which drawing it gets
ALIASES = {
    "default": ["left_ptr", "arrow", "top_left_arrow", "context-menu", "alias", "right_ptr", "draft_large", "draft_small"],
    "pointer": ["hand", "hand1", "hand2", "pointing_hand", "9d800788f1b08800ae810202380a0822", "e29285e634086352946a0e7090d73106"],
    "text": ["xterm", "ibeam", "vertical-text"],
    "crosshair": ["cross", "tcross", "cell", "color-picker", "plus", "target"],
    "not-allowed": ["no-drop", "forbidden", "crossed_circle", "circle", "03b6e0fcb3499374a867c041f52298f0", "dnd-no-drop", "pirate"],
    "move": ["fleur", "all-scroll", "size_all", "grab", "grabbing", "openhand", "closedhand", "dnd-move", "pointer-move",
             "fcf1c3c7cd4491d801f1e1c78f100000", "4498f0e0c1937ffe01fd06f973665830", "9081237383d90e509aa00f00170e968f"],
    "ew-resize": ["col-resize", "e-resize", "w-resize", "size_hor", "sb_h_double_arrow", "h_double_arrow", "left_side",
                  "right_side", "split_h", "028006030e0e7ebffc7f7070c0600140", "14fef782d02440884392942c11205230"],
    "ns-resize": ["row-resize", "n-resize", "s-resize", "size_ver", "sb_v_double_arrow", "v_double_arrow", "top_side",
                  "bottom_side", "split_v", "00008160000006810000408080010102", "2870a09082c103050810ffdffffe0204"],
    "nwse-resize": ["nw-resize", "se-resize", "size_fdiag", "top_left_corner", "bottom_right_corner",
                    "c7088f0f3e6c8088236ef8e1e3e70000"],
    "nesw-resize": ["ne-resize", "sw-resize", "size_bdiag", "top_right_corner", "bottom_left_corner",
                    "fcf1c3c7cd4491d801f1e1c78f100000-bdiag", "fd_double_arrow"],
    "wait": ["watch", "clock"],
    "progress": ["left_ptr_watch", "half-busy", "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"],
    "help": ["question_arrow", "whats_this", "left_ptr_help", "d9ce0ab605698f320427677b458ad60b", "5c6cd98b3f3ebcb1f9c7f1c204630408"],
    "copy": ["dnd-copy", "dnd-link", "link", "1081e37283d90000800003c07f3ef6bf", "6407b0e94181790501fd1e167b474872",
             "3085a0e285430894940527032f8b26df", "640fb0e74195791501fd1ed57b41487f", "b66166c04f8c3109214a4fbd64a50fc8"],
    "zoom-in": ["zoom_in"],
    "zoom-out": ["zoom_out"],
}


def build(out_dir):
    cur = os.path.join(out_dir, "cursors")
    os.makedirs(cur, exist_ok=True)
    for name, (frames, (hx, hy), delay) in CURSORS.items():
        images = []
        for size in SIZES:
            for layers in frames:
                rows = render(layers, size)
                images.append((size, size, size, int(hx * size / 32), int(hy * size / 32), delay, rows))
        open(os.path.join(cur, name), "wb").write(xcursor(images))
        for alias in ALIASES.get(name, []):
            link = os.path.join(cur, alias)
            if os.path.lexists(link):
                os.remove(link)
            os.symlink(name, link)
    open(os.path.join(out_dir, "index.theme"), "w").write(
        "[Icon Theme]\nName=nekozame\nComment=nekozame's pointer: the trans flag, glossy like a bubble\n")
