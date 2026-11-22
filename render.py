"""Render entry.png: a 1024x1024 flat-vector news infographic for 21 Nov 2026.

PIL primitives only, one type family (DejaVu Sans Bold / Regular).
Drawn at 3x and downsampled with LANCZOS so circles, diagonals and glyph edges
come out clean; every coordinate below is in 1024-unit design space.
"""

import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
S = 3  # supersample factor

BG = (247, 244, 239)
INK = (26, 26, 26)
GREY = (95, 95, 95)
CARD = (255, 255, 255)
STROKE = (226, 221, 212)
RED = (198, 40, 40)
HAIR = (226, 221, 212)
GRID = (237, 232, 223)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

_fonts = {}


def font(size, bold=True):
    """Font at supersampled size, cached."""
    if size < 18:
        raise ValueError(f"font size {size} violates the 18px floor")
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(BOLD if bold else REG, int(round(size * S)))
    return _fonts[key]


def measure(text, size, bold=True):
    """Width in design units."""
    return font(size, bold).getlength(text) / S


def box4(b):
    """Accept either (x0,y0,x1,y1) or ((x0,y0),(x1,y1))."""
    if len(b) == 2:
        return (b[0][0], b[0][1], b[1][0], b[1][1])
    return (b[0], b[1], b[2], b[3])


def asc(size, bold=True):
    return font(size, bold).getmetrics()[0] / S


class Canvas:
    def __init__(self):
        self.img = Image.new("RGB", (W * S, H * S), BG)
        self.d = ImageDraw.Draw(self.img)

    def rect(self, box, fill=None, outline=None, width=1):
        s = self.S
        b = box4(box)
        self.d.rectangle(
            [b[0] * s, b[1] * s, b[2] * s, b[3] * s],
            fill=fill,
            outline=outline,
            width=max(1, int(round(width * s))),
        )

    def rrect(self, box, r, fill=None, outline=None, width=1):
        s = self.S
        b = box4(box)
        self.d.rounded_rectangle(
            [b[0] * s, b[1] * s, b[2] * s, b[3] * s],
            radius=r * s,
            fill=fill,
            outline=outline,
            width=max(1, int(round(width * s))),
        )

    def line(self, pts, fill, width=1):
        s = self.S
        self.d.line(
            [(p[0] * s, p[1] * s) for p in pts],
            fill=fill,
            width=max(1, int(round(width * s))),
            joint="curve",
        )

    def ellipse(self, box, fill=None, outline=None, width=1):
        s = self.S
        b = box4(box)
        self.d.ellipse(
            [b[0] * s, b[1] * s, b[2] * s, b[3] * s],
            fill=fill,
            outline=outline,
            width=max(1, int(round(width * s))),
        )

    def poly(self, pts, fill=None, outline=None, width=1):
        s = self.S
        self.d.polygon(
            [(p[0] * s, p[1] * s) for p in pts],
            fill=fill,
            outline=outline,
            width=max(1, int(round(width * s))),
        )

    def text(self, x, y, s, size, fill, bold=True, align="left"):
        """y = ink top of capitals; align sets the horizontal origin."""
        f = font(size, bold)
        top = f.getbbox("H")[1]
        anchor = {"left": "la", "right": "ra", "center": "ma"}[align]
        self.d.text((x * S, y * S - top), s, font=f, fill=fill, anchor=anchor)

    def text_bl(self, x, baseline, s, size, fill, bold=True, align="left"):
        """y = text baseline."""
        anchor = {"left": "ls", "right": "rs", "center": "ms"}[align]
        self.d.text((x * S, baseline * S), s, font=font(size, bold), fill=fill, anchor=anchor)

    def text_center(self, cx, cy, s, size, fill, bold=True):
        self.d.text((cx * S, cy * S), s, font=font(size, bold), fill=fill, anchor="mm")

    S = S


C = Canvas()


def wrap(text, size, maxw, bold=True):
    """Wrap to maxw, breaking hyphenated compounds at the hyphen when needed."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if measure(trial, size, bold) <= maxw:
            cur = trial
            continue
        if cur:
            lines.append(cur)
            cur = ""
        # a single token wider than the column: break it at its hyphen
        if measure(w, size, bold) > maxw and "-" in w[1:-1]:
            head, _, tail = w.partition("-")
            head += "-"
            if measure(head, size, bold) <= maxw:
                lines.append(head)
                w = tail
        cur = w
    if cur:
        lines.append(cur)
    return lines


def fit(text, size, maxw, maxlines, bold=True, floor=18):
    """Wrap at size; step down (never below floor) until it fits maxlines."""
    s = size
    while s >= floor:
        lines = wrap(text, s, maxw, bold)
        if len(lines) <= maxlines and all(measure(l, s, bold) <= maxw for l in lines):
            return lines, s
        s -= 1
    return wrap(text, floor, maxw, bold), floor


# ---------------------------------------------------------------- masthead
def masthead():
    C.text(32, 58, "WORLD NEWS", 24, GREY, bold=True)
    C.text(992, 46, "SATURDAY 21 NOVEMBER 2026", 34, INK, bold=True, align="right")
    C.rect((32, 110, 992, 113), fill=INK)


# ---------------------------------------------------------------- hero icon
def hero_art():
    x0, y0, x1, y1 = 48, 136, 300, 452

    # faint plotting grid
    for gy in (200, 248, 296, 344):
        C.line([(62, gy), (286, gy)], GRID, 1)

    # descending candlesticks: (cx, high, low, open, close)
    candles = [
        (78, 186, 252, 236, 200),
        (112, 196, 274, 212, 258),
        (146, 212, 300, 228, 286),
        (180, 246, 332, 258, 320),
        (214, 266, 356, 280, 346),
    ]
    for cx, hi, lo, op, cl in candles:
        up = cl < op
        col = INK if up else RED
        C.line([(cx, hi), (cx, lo)], col, 3)
        top, bot = min(op, cl), max(op, cl)
        C.rect((cx - 8, top, cx + 8, bot), fill=col)
        C.rect((cx - 8, top, cx + 8, max(bot, top + 3)), fill=col)

    # thick downward arrow, white under-stroke so it reads over the candles
    ax0, ay0, ax1, ay1 = 86, 194, 238, 336
    C.line([(ax0, ay0), (ax1, ay1)], CARD, 15)
    C.line([(ax0, ay0), (ax1, ay1)], RED, 9)

    ang = math.atan2(ay1 - ay0, ax1 - ax0)
    hl, hw = 30, 21
    tip = (ax1, ay1)
    back = (ax1 - hl * math.cos(ang), ay1 - hl * math.sin(ang))
    left = (back[0] - hw * math.sin(ang), back[1] + hw * math.cos(ang))
    right = (back[0] + hw * math.sin(ang), back[1] - hw * math.cos(ang))
    C.poly([tip, left, right], fill=RED)
    C.poly(
        [
            (tip[0] + 3 * math.cos(ang), tip[1] + 3 * math.sin(ang)),
            (left[0] + 3 * math.cos(ang), left[1] + 3 * math.sin(ang)),
            (right[0] + 3 * math.cos(ang), right[1] + 3 * math.sin(ang)),
        ],
        fill=RED,
    )

    # AI chip
    C.rrect((62, 396, 122, 432), 4, fill=CARD, outline=INK, width=2)
    C.text_center(92, 414, "AI", 22, INK, bold=True)


def hero():
    C.rect((32, 128, 992, 452), fill=CARD, outline=STROKE, width=1)
    C.rect((32, 128, 992, 136), fill=RED)
    hero_art()

    # chip
    cw = measure("MARKETS \u00b7 GLOBAL", 22) + 24
    C.rect((320, 164, 320 + cw, 198), fill=RED)
    C.text(320 + 12, 170, "MARKETS \u00b7 GLOBAL", 22, CARD, bold=True)

    # headline
    C.text(320, 210, "AI sell-off hits", 46, INK, bold=True)
    C.text(320, 264, "world markets", 46, INK, bold=True)

    # stat row
    base = 372
    C.text_bl(320, base, "\u22123.7%", 34, INK, bold=True)
    C.text_bl(320 + measure("\u22123.7%", 34) + 9, base, "S&P 500", 22, GREY, bold=True)
    C.line([(620, 340), (620, 384)], STROKE, 1)
    C.text_bl(644, base, "\u22125.06%", 34, INK, bold=True)
    C.text_bl(644 + measure("\u22125.06%", 34) + 9, base, "Nikkei", 22, GREY, bold=True)

    C.text(320, 392, "on doubts AI spending will pay off", 22, GREY, bold=False)


# ---------------------------------------------------------------- icons
def _map(x, y, s):
    k = s / 40.0
    return lambda px, py: (x + px * k, y + py * k)


def icon_gavel_scales(x, y, s=40):
    p = _map(x, y, s)
    light = (159, 168, 218)
    # scales
    C.line([p(20, 12), p(20, 32)], light, 2.4)
    C.line([p(7, 15), p(33, 15)], light, 2.4)
    C.poly([p(7, 15), p(2.5, 25), p(11.5, 25)], fill=light)
    C.poly([p(33, 15), p(28.5, 25), p(37.5, 25)], fill=light)
    C.line([p(13, 33), p(27, 33)], light, 2.4)
    # gavel over it
    C.line([p(15, 30), p(26, 19)], (57, 73, 171), 3)
    C.poly([p(24, 9), p(33, 18), p(28.5, 22.5), p(19.5, 13.5)], fill=(57, 73, 171))


def icon_missile(x, y, s=40):
    p = _map(x, y, s)
    dark = (55, 71, 79)
    acc = (230, 74, 25)
    # missile: nose + shaft + fins, angled up-right
    C.poly([p(35, 3), p(38, 15), p(27, 12)], fill=dark)
    C.line([p(27, 12), p(18, 21)], dark, 3.6)
    C.poly([p(23, 10), p(28, 6), p(29, 12)], fill=dark)
    # dotted trail
    for t in (14, 10.5, 7, 3.5):
        C.ellipse([p(t - 1.3, t + 4.4 - 1.3), p(t + 1.3, t + 4.4 + 1.3)], fill=acc)
    # two map locations: pin rings with a centre dot
    for cx, cy, r in ((8, 31, 5.2), (21, 34, 4.4)):
        C.ellipse([p(cx - r, cy - r), p(cx + r, cy + r)], outline=dark, width=2)
        C.ellipse([p(cx - 1.5, cy - 1.5), p(cx + 1.5, cy + 1.5)], fill=acc)


def icon_cuffs(x, y, s=40):
    p = _map(x, y, s)
    br = (78, 52, 46)
    # two cuffs on different axes, so they never read as binoculars
    C.ellipse([p(1, 10), p(17, 26)], outline=br, width=3.2)
    C.ellipse([p(21, 16), p(37, 32)], outline=br, width=3.2)
    # chain: two links
    C.ellipse([p(15, 21), p(20, 26)], outline=br, width=2.4)
    C.ellipse([p(19, 25), p(24, 30)], outline=br, width=2.4)


def icon_globe_clock(x, y, s=40):
    p = _map(x, y, s)
    teal = (0, 121, 107)
    # globe
    C.ellipse([p(1.5, 1.5), p(33.5, 33.5)], outline=teal, width=2.8)
    C.ellipse([p(10.5, 1.5), p(24.5, 33.5)], outline=teal, width=1.8)
    C.line([p(1.5, 17.5), p(33.5, 17.5)], teal, 1.8)
    # clock inset, bottom-right: disc, rim, hands
    C.ellipse([p(21, 21), p(40, 40)], fill=(255, 255, 255), outline=teal, width=2.6)
    C.line([p(30.5, 30.5), p(30.5, 25)], teal, 2.4)
    C.line([p(30.5, 30.5), p(35, 32.5)], teal, 2.4)


def icon_tanker(x, y, s=40):
    p = _map(x, y, s)
    amb = (178, 106, 0)
    flame = (230, 74, 25)
    C.poly([p(3, 25), p(37, 25), p(31, 35), p(9, 35)], fill=amb)
    C.rect((p(12, 20)[0], p(12, 17)[1], p(28, 25)[0], p(28, 25)[1]), fill=amb)
    C.poly(
        [p(20, 3), p(24, 9), p(22, 13), p(26, 17), p(20, 18), p(14, 13), p(17, 9), p(16, 6)],
        fill=flame,
    )


def icon_mosquito_shield(x, y, s=40):
    p = _map(x, y, s)
    pu = (106, 27, 154)
    C.poly(
        [p(20, 1), p(36, 6), p(34, 22), p(20, 38), p(6, 22), p(4, 6)],
        outline=pu,
        width=2.4,
    )
    # body: thin tilted abdomen + round thorax
    C.line([p(16, 24), p(22, 14)], pu, 2.8)
    C.ellipse([p(20.4, 12.2), p(25.6, 17.4)], fill=pu)
    # long proboscis, the signature that separates a mosquito from a spider
    C.line([p(23, 13), p(30, 8)], pu, 1.8)
    # wings: two thin ellipses angled back
    C.ellipse([p(22, 12.6), p(31, 16.4)], outline=pu, width=1.4)
    C.ellipse([p(15, 12.2), p(23, 15.4)], outline=pu, width=1.4)
    # six long legs, splayed
    for dx, dy in ((-1, -1), (0.4, -1.2), (1.6, -1)):
        C.line([p(18, 18), p(18 + 5 * dx, 18 - 5 * dy)], pu, 1.5)
    for dx, dy in ((-1, 0.6), (0, 1), (1.2, 0.8)):
        C.line([p(19, 20), p(19 + 5 * dx, 20 + 5 * dy)], pu, 1.5)


def icon_tents(x, y, s=40):
    p = _map(x, y, s)
    br = (93, 64, 55)
    # ground line: kills the mountain-range reading
    C.line([p(0, 27), p(40, 27)], br, 2.2)
    # big tent with an A-frame door, guy rope to the left
    C.poly([p(21, 4), p(35, 27), p(7, 27)], fill=br)
    C.poly([p(21, 10), p(27, 27), p(15, 27)], fill=(255, 255, 255))
    C.line([p(21, 4), p(1, 27)], br, 1.6)
    # small tent behind-right
    C.poly([p(33, 13), p(40, 27), p(26, 27)], fill=(120, 88, 78))
    C.poly([p(33, 18), p(36, 27), p(30, 27)], fill=(255, 255, 255))
    # one person in front of the tents, large enough to read as a figure
    C.ellipse([p(2.6, 29), p(8.4, 34.8)], fill=br)
    C.poly([p(1.2, 40), p(1.2, 37), p(9.8, 37), p(9.8, 40)], fill=br)
    C.rrect((p(1.8, 35.4)[0], p(1.8, 35.4)[1], p(9.2, 38.4)[0], p(9.2, 38.4)[1]), 1.2, fill=br)


def icon_parliament(x, y, s=40):
    p = _map(x, y, s)
    bl = (2, 119, 189)
    # pediment + columns, kept to the upper-left so the pistol owns the corner
    C.poly([p(15, 2), p(29, 11), p(1, 11)], fill=bl)
    C.rect((p(1, 12.5)[0], p(1, 12.5)[1], p(29, 15)[0], p(29, 15)[1]), fill=bl)
    for cx in (3.5, 9, 14.5, 20, 25.5):
        C.rect((p(cx, 16)[0], p(cx, 16)[1], p(cx + 2.6, 24)[0], p(cx + 2.6, 24)[1]), fill=(150, 202, 230))
    C.rect((p(1, 25)[0], p(1, 25)[1], p(29, 27.6)[0], p(29, 27.6)[1]), fill=bl)
    # pistol silhouette, large and clear: slide + barrel, then grip
    C.rect((p(17, 29)[0], p(17, 29)[1], p(38, 33.2)[0], p(38, 33.2)[1]), fill=INK)
    C.poly([p(27.2, 33.2), p(33.6, 33.2), p(30.6, 39.6), p(23.6, 39.6)], fill=INK)
    C.rect((p(20, 30.2)[0], p(20, 30.2)[1], p(23.4, 32)[0], p(23.4, 32)[1]), fill=(255, 255, 255))


ICONS = {
    "law": icon_gavel_scales,
    "conflict": icon_missile,
    "security": icon_cuffs,
    "climate": icon_globe_clock,
    "energy": icon_tanker,
    "science": icon_mosquito_shield,
    "humanitarian": icon_tents,
    "rights": icon_parliament,
}


# ---------------------------------------------------------------- grid
CARDS = [
    (2, "Myanmar guilty of genocide", "ICJ's first such verdict", "LAW", (57, 73, 171), "law"),
    (3, "Missiles hit Poland, Ukraine", "Kryvyi Rih: 2 dead, 60 hurt", "CONFLICT", (55, 71, 79), "conflict"),
    (4, "Cartel boss captured", "11 killed in Sinaloa", "SECURITY", (78, 52, 46), "security"),
    (5, "COP31 runs overtime", "Fossil-fuel deadlock, Antalya", "CLIMATE", (0, 121, 107), "climate"),
    (6, "Tankers burn near Hormuz", "2 ships hit mines", "ENERGY", (140, 84, 0), "energy"),
    (7, "Dengue cut 69%", "Brazil mosquito trial", "SCIENCE", (106, 27, 154), "science"),
    (8, "700,000 displaced", "Southern Ethiopia", "AID", (93, 64, 55), "humanitarian"),
    (9, "Police-shooting law passes", "French Senate; critics object", "RIGHTS", (2, 119, 189), "rights"),
]

COL_X = [33, 276, 519, 762]
ROW_Y = [476, 716]
TW, TH = 229, 226
TX = 20  # text left inside card
TMAX = 229 - TX - 14  # 195


def card(i, num, head, sub, cat, colour, icon):
    cx = COL_X[i % 4]
    cy = ROW_Y[i // 4]

    C.rect((cx, cy, cx + TW, cy + TH), fill=CARD, outline=STROKE, width=1)
    C.rect((cx, cy, cx + 6, cy + TH), fill=colour)

    ICONS[icon](cx + TX, cy + 14)

    # category chip
    cwid = measure(cat, 18) + 16
    num_x = cx + TW - 12
    assert cx + 72 + cwid <= num_x - 8, (num, cat, cwid)
    C.rrect((cx + 72, cy + 20, cx + 72 + cwid, cy + 46), 13, fill=colour)
    C.text(cx + 72 + 8, cy + 25, cat, 18, CARD, bold=True)

    # corner numeral
    C.text(num_x, cy + 10, str(num), 26, GREY, bold=True, align="right")

    # headline
    hsize = 27
    lines, hsize = fit(head, hsize, TMAX, 3)
    lh = round(hsize * 1.19)
    a = asc(hsize)
    top = cy + 62
    for k, ln in enumerate(lines):
        assert measure(ln, hsize, True) <= TMAX, (num, ln, measure(ln, hsize, True))
        C.text_bl(cx + TX, top + a + k * lh, ln, hsize, INK, bold=True)

    y = top + len(lines) * lh + 6

    # sub
    slines, ssize = fit(sub, 20, TMAX, 2, bold=False)
    slh = round(ssize * 1.25)
    sa = asc(ssize, bold=False)
    for k, ln in enumerate(slines):
        assert measure(ln, ssize, False) <= TMAX, (num, ln)
        C.text_bl(cx + TX, y + sa + k * slh, ln, ssize, GREY, bold=False)

    bottom = y + len(slines) * slh
    assert bottom <= cy + TH - 4, (num, bottom - cy)


def grid():
    for i, c in enumerate(CARDS):
        card(i, *c)


# ---------------------------------------------------------------- footer
def footer():
    C.rect((32, 946, 992, 947), fill=HAIR)
    C.text(
        512,
        958,
        "9 stories \u00b7 6 regions \u00b7 figures as reported on 21 Nov 2026 \u00b7 some reports still developing.",
        18,
        GREY,
        bold=False,
        align="center",
    )


def main():
    masthead()
    hero()
    grid()
    footer()
    out = C.img.resize((W, H), Image.LANCZOS)
    out.save("entry.png", "PNG", optimize=True)
    print("wrote entry.png", out.size, out.mode)


if __name__ == "__main__":
    main()
